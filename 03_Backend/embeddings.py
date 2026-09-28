import os

from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")


# Create Gemini client
client = genai.Client(api_key=api_key)


def create_embedding(text: str):
    """
    Convert text into a numerical embedding using Gemini.
    """

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values


if __name__ == "__main__":

    test_text = "I cannot login to Qlik Sense."

    embedding = create_embedding(test_text)

    print("Embedding created successfully!")
    print("Embedding dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])