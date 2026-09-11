from groq import Groq

from app.core.config import settings


client = Groq(api_key=settings.groq_api_key)


def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are an e-commerce customer support assistant.

Answer the user's question using ONLY the information provided in the context.

Always include the source name from the context at the end of your answer
in this format:
Source: <filename>

If the context does not contain enough information to answer the question,
say that you could not find the information in the knowledge base.

Do not invent prices, stock, delivery dates, return policies, warranty terms,
or any other information.

Context:
{context}

User question:
{question}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content