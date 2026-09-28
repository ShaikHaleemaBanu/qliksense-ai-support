import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)


SYSTEM_PROMPT = """
You are a GenAI-powered Qlik Sense Support Assistant.

Your job is to understand common Qlik Sense user issues and provide
clear, simple troubleshooting guidance.

Supported issue categories:
1. Login Failure
2. Password Issue
3. Browser Compatibility
4. Access Request Error
5. Incorrectly Raised Ticket

Important conversation rules:

- Be professional and concise.
- Do not provide multiple troubleshooting steps at once.
- Provide only ONE troubleshooting step at a time.
- After giving a step, ask the user to try it.
- Then ask whether the issue is resolved.
- Wait for the user's response before providing another step.
- Do not assume that the issue is resolved.
- If the user says the issue is resolved, acknowledge the resolution.
- If the user says the issue is not resolved, continue with the next
  applicable step.
- If troubleshooting steps are exhausted, suggest creating a support ticket.
- Never invent internal company information.
"""


def ask_gemini(message: str) -> str:

    prompt = f"""
{SYSTEM_PROMPT}

User message:
{message}
"""

    # Retry temporary Gemini server errors
    for attempt in range(4):

        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            return response.text

        except Exception as e:

            # Retry temporary server/API failures
            if "503" in str(e) or "UNAVAILABLE" in str(e):

                if attempt < 3:
                    wait_time = 2 ** attempt
                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                else:
                    raise

            else:
                raise