import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_answer(context, query):

    prompt = f"""
    You are an AI study assistant.

    Answer ONLY using the provided context.

    If the answer is not present in the context,
    say:

    "I could not find that information in the uploaded material."

    Context:
    {context}
    
    Question:
    {query}
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    return data["response"]

def rewrite_query(chat_history, current_query):

    if not chat_history:
        return current_query

    history_text = "\n".join(
        [
            f"{msg['role']}: {msg['content']}"
            for msg in chat_history[-4:]
        ]
    )

    prompt = f"""
    Given the conversation history and latest question,
    rewrite the latest question into a standalone question.

    Conversation:
    {history_text}

    Latest Question:
    {current_query}

    Standalone Question:
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    return data["response"].strip()