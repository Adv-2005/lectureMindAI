import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_answer(context, query):

    prompt = f"""
    Answer the question using ONLY the context below.

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