from transformers import pipeline

generator = pipeline('text-generation', model="Qwen/Qwen2.5-1.5B-Instruct")

def generate_answer(context, query):
    prompt = f"""
    Answer the question using ONLY on the context below.

    Context: {context}

    Question: {query}
    """

    response = generator(prompt, max_new_tokens=200)

    return response[0]['generated_text']