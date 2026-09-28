from fastapi import FastAPI
from pydantic import BaseModel

from gemini_client import ask_gemini
from troubleshooting import get_next_step
from conversation import ConversationState


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Qlik Sense AI Support Assistant",
    version="1.0"
)


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str


# --------------------------------------------------
# Conversation State
# --------------------------------------------------

conversation = ConversationState()


# --------------------------------------------------
# Ticket Fields
# --------------------------------------------------

TICKET_FIELDS = [
    ("user_id", "Please provide your User ID."),
    ("application_name", "Please provide the Application Name."),
    ("stream_name", "Please provide the Stream Name."),
    ("error_message", "Please provide the Error Message."),
    ("business_justification", "Please provide the Business Justification.")
]


# --------------------------------------------------
# Assignment Groups
# --------------------------------------------------

ASSIGNMENT_GROUPS = {
    "login": "Qlik Support",
    "password": "Qlik Support",
    "browser": "Qlik Support",
    "access": "Qlik Access Management",
    "incorrect_ticket": "Appropriate Support Team"
}


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Qlik Sense AI Support Assistant is running!"
    }


# --------------------------------------------------
# Chat Endpoint
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message.strip()

    if not user_message:
        return {
            "status": "error",
            "response": "Please enter a message."
        }

    message_lower = user_message.lower()


    # ==================================================
    # 1. TICKET CONFIRMATION
    # ==================================================

    if conversation.awaiting_ticket_confirmation:

        if message_lower in [
            "yes",
            "y",
            "yes please",
            "create ticket"
        ]:

            conversation.awaiting_ticket_confirmation = False
            conversation.ticket_required = True
            conversation.ticket_field_index = 0
            conversation.ticket_data = {}

            field_name, question = TICKET_FIELDS[0]

            return {
                "status": "collecting_ticket_information",
                "field": field_name,
                "response": question
            }


        elif message_lower in [
            "no",
            "n",
            "no thanks",
            "don't create ticket",
            "do not create ticket"
        ]:

            conversation.reset()

            return {
                "status": "closed",
                "response": "Okay. No support ticket will be created."
            }


        else:

            return {
                "status": "waiting_for_confirmation",
                "response": (
                    "Please answer Yes if you would like to create "
                    "a support ticket, or No if you do not."
                )
            }


    # ==================================================
    # 2. TICKET INFORMATION COLLECTION
    # ==================================================

    if conversation.ticket_required:

        field_index = conversation.ticket_field_index

        field_name, question = TICKET_FIELDS[field_index]

        # Save user's answer
        conversation.ticket_data[field_name] = user_message

        # Move to next field
        conversation.ticket_field_index += 1


        # ----------------------------------------------
        # More fields remaining
        # ----------------------------------------------

        if conversation.ticket_field_index < len(TICKET_FIELDS):

            next_field_name, next_question = TICKET_FIELDS[
                conversation.ticket_field_index
            ]

            return {
                "status": "collecting_ticket_information",
                "field": next_field_name,
                "response": next_question
            }


        # ----------------------------------------------
        # All fields collected
        # ----------------------------------------------

        attempted_steps = conversation.attempted_steps

        if attempted_steps:

            attempted_steps_text = "\n".join(
                [
                    f"{index + 1}. {step}"
                    for index, step in enumerate(attempted_steps)
                ]
            )

        else:

            attempted_steps_text = "No troubleshooting steps recorded."


        assignment_group = ASSIGNMENT_GROUPS.get(
            conversation.category,
            "Qlik Support"
        )


        # ----------------------------------------------
        # Generate Ticket Summary
        # ----------------------------------------------

        ticket_summary = (
            "Support Ticket Summary\n\n"
            f"Issue Category: {conversation.category}\n\n"
            f"User ID: {conversation.ticket_data['user_id']}\n\n"
            f"Application Name: "
            f"{conversation.ticket_data['application_name']}\n\n"
            f"Stream Name: "
            f"{conversation.ticket_data['stream_name']}\n\n"
            f"Error Message: "
            f"{conversation.ticket_data['error_message']}\n\n"
            f"Business Justification: "
            f"{conversation.ticket_data['business_justification']}\n\n"
            "Troubleshooting Steps Attempted:\n"
            f"{attempted_steps_text}\n\n"
            f"Recommended Assignment Group: {assignment_group}"
        )


        # Save category before reset
        category = conversation.category

        # Reset conversation
        conversation.reset()


        return {
            "status": "ticket_ready",
            "category": category,
            "response": (
                "Thank you. I have collected all the required "
                "information for the support ticket."
            ),
            "ticket_summary": ticket_summary
        }


    # ==================================================
    # 3. RESOLUTION CHECK
    # ==================================================

    if conversation.awaiting_resolution:

        # ----------------------------------------------
        # User says YES
        # ----------------------------------------------

        if message_lower in [
            "yes",
            "y",
            "yes it is resolved",
            "resolved",
            "it is resolved",
            "issue resolved",
            "works",
            "working",
            "fixed",
            "it works"
        ]:

            category = conversation.category

            conversation.reset()

            return {
                "status": "resolved",
                "response": (
                    f"Great! Your {category} issue has been resolved. "
                    "No support ticket is required."
                )
            }


        # ----------------------------------------------
        # User says NO
        # ----------------------------------------------

        if message_lower in [
            "no",
            "n",
            "not resolved",
            "still not working",
            "doesn't work",
            "does not work",
            "not working",
            "issue is still there",
            "still facing the issue",
            "still facing issue"
        ]:

            # Move to next troubleshooting step
            conversation.next_step()


            next_step = get_next_step(
                conversation.category,
                conversation.current_step
            )


            # ------------------------------------------
            # No more troubleshooting steps
            # ------------------------------------------

            if next_step is None:

                conversation.awaiting_resolution = False
                conversation.awaiting_ticket_confirmation = True

                return {
                    "status": "ticket_confirmation",
                    "response": (
                        "The available troubleshooting steps have "
                        "been completed, but the issue is still not "
                        "resolved.\n\n"
                        "Would you like me to help you create a "
                        "support ticket?"
                    )
                }


            # ------------------------------------------
            # Send next troubleshooting step
            # ------------------------------------------

            conversation.add_attempted_step(next_step)

            return {
                "status": "troubleshooting",
                "category": conversation.category,
                "step": conversation.current_step + 1,
                "response": (
                    f"{next_step}\n\n"
                    "Please try this step and let me know: "
                    "Is the issue resolved?"
                )
            }


        # ----------------------------------------------
        # Invalid resolution response
        # ----------------------------------------------

        return {
            "status": "waiting_for_resolution",
            "response": (
                "Please let me know whether the issue is resolved "
                "by answering Yes or No."
            )
        }


    # ==================================================
    # 4. NEW ISSUE - CATEGORY DETECTION
    # ==================================================

    if conversation.category is None:

        category_prompt = f"""
Identify the Qlik Sense support issue category from the user's message.

Allowed categories:

login
password
browser
access
incorrect_ticket

Rules:

- Login problems should return login.
- Password reset or forgotten password problems should return password.
- Browser, Chrome, Edge, cache, or compatibility problems should return browser.
- Access or permission problems should return access.
- Issues about tickets being incorrectly raised or not related to Qlik should return incorrect_ticket.

Return ONLY ONE category name.

User message:
{user_message}
"""


        # Ask Gemini to identify category
        category_response = ask_gemini(category_prompt)

        category = category_response.strip().lower()


        # ----------------------------------------------
        # Clean Gemini response
        # ----------------------------------------------

        if "incorrect_ticket" in category:
            category = "incorrect_ticket"

        elif "password" in category:
            category = "password"

        elif "browser" in category:
            category = "browser"

        elif "access" in category:
            category = "access"

        elif "login" in category:
            category = "login"

        else:

            return {
                "status": "unknown_category",
                "response": (
                    "I need a little more information to understand "
                    "your Qlik Sense issue. Please describe the problem."
                )
            }


        # ----------------------------------------------
        # Start conversation
        # ----------------------------------------------

        conversation.start(category)


        # Get first troubleshooting step
        step = get_next_step(
            conversation.category,
            conversation.current_step
        )


        if step is None:

            conversation.awaiting_resolution = False
            conversation.awaiting_ticket_confirmation = True

            return {
                "status": "ticket_confirmation",
                "response": (
                    "There are no available troubleshooting steps "
                    "for this issue. Would you like me to help you "
                    "create a support ticket?"
                )
            }


        # Record first step
        conversation.add_attempted_step(step)


        return {
            "status": "troubleshooting",
            "category": conversation.category,
            "step": conversation.current_step + 1,
            "response": (
                f"{step}\n\n"
                "Please try this step and let me know: "
                "Is the issue resolved?"
            )
        }


    # ==================================================
    # 5. FALLBACK
    # ==================================================

    return {
        "status": "waiting",
        "response": (
            "Please let me know whether the issue is resolved "
            "by answering Yes or No."
        )
    }