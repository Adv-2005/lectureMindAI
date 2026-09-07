import sqlite3
from typing import Annotated, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, RemoveMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from app.core.config import settings
from app.services.ingestion_service import get_vector_store


NO_ANSWER = "I could not find that information in the uploaded material."


class ChatState(TypedDict, total=False):
    """State persisted by LangGraph for one browser session/thread."""

    messages: Annotated[list[BaseMessage], add_messages]
    current_query: str
    rewritten_query: str
    selected_documents: list[str]
    retrieved_documents: list[Document]
    answer: str
    context: list[str]
    sources: list[dict]
    used_documents: list[str]


def get_chat_model() -> ChatOllama:
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.chat_model,
        temperature=0,
    )


REWRITE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Rewrite the latest user question as a concise standalone question. "
            "Do not answer it and do not add information not present in the conversation.",
        ),
        MessagesPlaceholder("history"),
        ("human", "Latest question: {question}"),
    ]
)

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an AI study assistant. Answer only from the supplied lecture-note "
            "context. If the context does not support an answer, respond exactly: "
            f'"{NO_ANSWER}". Cite supporting material using the [filename, p. N] labels '\
            "already present in the context.",
        ),
        ("human", "Context:\n{context}\n\nQuestion:\n{question}"),
    ]
)


def _content(message: BaseMessage) -> str:
    """Normalize chat-model content that may be returned as rich content blocks."""
    if isinstance(message.content, str):
        return message.content.strip()
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in message.content
    ).strip()


def rewrite_query(state: ChatState) -> dict:
    messages = state.get("messages", [])
    history = messages[:-1][-4:]
    question = state["current_query"]
    if not history:
        return {"rewritten_query": question}

    response = get_chat_model().invoke(
        REWRITE_PROMPT.format_messages(history=history, question=question)
    )
    rewritten = _content(response) or question
    return {"rewritten_query": rewritten}


def retrieve_documents(state: ChatState) -> dict:
    document_filter = None
    selected_documents = state.get("selected_documents", [])
    if selected_documents:
        document_filter = {"document_id": {"$in": selected_documents}}

    documents = get_vector_store().similarity_search(
        state["rewritten_query"],
        k=settings.retrieval_k,
        filter=document_filter,
    )
    return {"retrieved_documents": documents}


def _source(document: Document) -> dict:
    metadata = document.metadata
    return {
        "filename": metadata.get("filename", "Unknown source"),
        "page": metadata.get("page"),
        "document_id": metadata.get("document_id"),
    }


def generate_answer(state: ChatState) -> dict:
    documents = state.get("retrieved_documents", [])
    if not documents:
        return {
            "answer": NO_ANSWER,
            "context": [],
            "sources": [],
            "used_documents": [],
            "messages": [AIMessage(content=NO_ANSWER)],
        }

    sources = [_source(document) for document in documents]
    context = [document.page_content for document in documents]
    context_with_citations = "\n\n".join(
        f"[{source['filename']}, p. {source['page']}]\n{chunk}"
        for source, chunk in zip(sources, context)
    )
    answer = _content(
        get_chat_model().invoke(
            ANSWER_PROMPT.format_messages(
                context=context_with_citations,
                question=state["rewritten_query"],
            )
        )
    )
    answer = answer or NO_ANSWER
    used_documents = list(dict.fromkeys(source["filename"] for source in sources))
    return {
        "answer": answer,
        "context": context,
        "sources": sources,
        "used_documents": used_documents,
        "messages": [AIMessage(content=answer)],
    }


def trim_history(state: ChatState) -> dict:
    """Keep durable conversation state bounded to the configured message window."""
    messages = state.get("messages", [])
    if len(messages) <= settings.max_history_messages:
        return {}

    stale_messages = messages[: -settings.max_history_messages]
    return {
        "messages": [RemoveMessage(id=message.id) for message in stale_messages],
    }


def build_chat_graph():
    builder = StateGraph(ChatState)
    builder.add_node("rewrite_query", rewrite_query)
    builder.add_node("retrieve_documents", retrieve_documents)
    builder.add_node("generate_answer", generate_answer)
    builder.add_node("trim_history", trim_history)
    builder.add_edge(START, "rewrite_query")
    builder.add_edge("rewrite_query", "retrieve_documents")
    builder.add_edge("retrieve_documents", "generate_answer")
    builder.add_edge("generate_answer", "trim_history")
    builder.add_edge("trim_history", END)

    settings.prepare_directories()
    connection = sqlite3.connect(str(settings.checkpoint_db_path), check_same_thread=False)
    return builder.compile(checkpointer=SqliteSaver(connection))


chat_graph = build_chat_graph()


def ask_question(
    query: str,
    session_id: str,
    selected_documents: list[str] | None = None,
) -> dict:
    """Invoke the persistent LangGraph workflow and preserve the existing API shape."""
    result = chat_graph.invoke(
        {
            "messages": [HumanMessage(content=query)],
            "current_query": query,
            "selected_documents": selected_documents or [],
        },
        config={"configurable": {"thread_id": session_id}},
    )
    return {
        "answer": result["answer"],
        "context": result["context"],
        "sources": result["sources"],
        "used_documents": result["used_documents"],
    }
