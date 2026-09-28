from search_knowledge import search_knowledge
from gemini_client import ask_gemini


def generate_rag_response(user_question: str):

    # Step 1: Search the knowledge base
    results = search_knowledge(
        user_question,
        top_k=3
    )

    if not results:
        return "I could not find relevant information in the knowledge base."

    # Step 2: Build context from search results
    context = "\n\n".join(
        result["document"]
        for result in results
    )

    # Step 3: Ask Gemini to answer using the retrieved context
    prompt = f"""
You are a Qlik Sense Support Assistant.

Use ONLY the information provided in the Knowledge Base Context
to answer the user's question.

Knowledge Base Context:
{context}

User Question:
{user_question}

Rules:
- Give clear and simple guidance.
- Do not invent troubleshooting steps.
- Do not provide multiple troubleshooting steps at once.
- Provide only ONE relevant troubleshooting step.
- Ask the user to try the step.
- Then ask whether the issue is resolved.
"""

    response = ask_gemini(prompt)

    return response


if __name__ == "__main__":

    question = "I forgot my Qlik Sense password"

    response = generate_rag_response(question)

    print("User Question:")
    print(question)

    print("\n" + "=" * 60)

    print("Gemini RAG Response:")
    print(response)