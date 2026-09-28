from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gemini_client import ask_gemini
from troubleshooting import get_next_step
from conversation import ConversationState


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Qlik Sense AI Support Assistant",
    description="GenAI-based Qlik Sense troubleshooting assistant",
    version="1.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CONVERSATION STATE
# =========================================================

conversation = ConversationState()


# =========================================================
# REQUEST MODEL
# =========================================================

class ChatRequest(BaseModel):
    message: str


# =========================================================
# RESOLUTION DETECTION
# =========================================================

def detect_resolution(message: str):

    text = message.lower().strip()

    yes_words = [
        "yes",
        "yes it is resolved",
        "yes it is fixed",
        "resolved",
        "issue is resolved",
        "problem is resolved",
        "fixed",
        "it is fixed",
        "works",
        "working",
        "working now",
        "it works",
        "problem solved",
        "solved",
        "done"
    ]

    no_words = [
        "no",
        "not resolved",
        "still not working",
        "still not resolved",
        "not fixed",
        "doesn't work",
        "does not work",
        "not working",
        "still occurring",
        "same issue",
        "still have the issue",
        "still having the issue",
        "issue still exists"
    ]

    if text in yes_words:
        return "yes"

    if text in no_words:
        return "no"

    return None


# =========================================================
# TICKET RESPONSE DETECTION
# =========================================================

def detect_ticket_response(message: str):

    text = message.lower().strip()

    yes_words = [
        "yes",
        "yes please",
        "create ticket",
        "create a ticket",
        "raise ticket",
        "raise a ticket",
        "i want to create a ticket",
        "i want to raise a ticket"
    ]

    no_words = [
        "no",
        "no thanks",
        "not now",
        "later",
        "i don't want to create a ticket",
        "i do not want to create a ticket"
    ]

    if text in yes_words:
        return "yes"

    if text in no_words:
        return "no"

    return None


# =========================================================
# GREETING / GENERAL MESSAGE DETECTION
# =========================================================

def detect_general_message(message: str):

    text = message.lower().strip()

    greetings = [
        "hello",
        "hi",
        "hey",
        "hii",
        "hiii",
        "good morning",
        "good afternoon",
        "good evening",
        "good night"
    ]

    help_questions = [
        "help",
        "help me",
        "what can you help me with",
        "what can you help with",
        "what can you do",
        "how can you help",
        "what do you support",
        "what issues can you help with",
        "what issues do you support"
    ]

    if text in greetings:
        return "greeting"

    if text in help_questions:
        return "help"

    return None


# =========================================================
# DIRECT KEYWORD CLASSIFICATION
# =========================================================

def detect_category_by_keywords(message: str):

    text = message.lower().strip()

    # -----------------------------------------------------
    # TICKET
    # -----------------------------------------------------

    ticket_keywords = [
        "ticket",
        "support ticket",
        "raise a ticket",
        "raise ticket",
        "create a ticket",
        "create ticket",
        "incorrect ticket",
        "ticket information"
    ]

    if any(keyword in text for keyword in ticket_keywords):
        return "incorrect_ticket"


    # -----------------------------------------------------
    # PASSWORD
    # -----------------------------------------------------

    password_keywords = [
        "password",
        "forgot password",
        "forgot my password",
        "reset password",
        "password reset",
        "password expired",
        "password incorrect",
        "wrong password",
        "password not working"
    ]

    if any(keyword in text for keyword in password_keywords):
        return "password"


    # -----------------------------------------------------
    # BROWSER
    # -----------------------------------------------------

    browser_keywords = [
        "browser",
        "chrome",
        "edge",
        "firefox",
        "internet explorer",
        "browser issue",
        "browser problem",
        "browser not working",
        "cache",
        "extension"
    ]

    if any(keyword in text for keyword in browser_keywords):
        return "browser"


    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    login_keywords = [
        "login",
        "log in",
        "logged in",
        "logging in",
        "sign in",
        "signin",
        "cannot login",
        "can't login",
        "unable to login",
        "login failed",
        "login failure",
        "unable to log in",
        "cannot log in",
        "can't log in"
    ]

    if any(keyword in text for keyword in login_keywords):
        return "login"


    # -----------------------------------------------------
    # ACCESS
    # -----------------------------------------------------

    access_keywords = [
        "access",
        "cannot access",
        "can't access",
        "unable to access",
        "no access",
        "access denied",
        "access issue",
        "access problem",
        "application not opening",
        "app not opening",
        "qlik not opening",
        "application is not opening",
        "cannot open application",
        "can't open application",
        "unable to open application",
        "stream access"
    ]

    if any(keyword in text for keyword in access_keywords):
        return "access"


    return None


# =========================================================
# TICKET INFORMATION FIELDS
# =========================================================

TICKET_FIELDS = [

    (
        "application_name",
        "Please provide the Application Name."
    ),

    (
        "environment",
        "Please provide the Environment."
    ),

    (
        "license_type",
        "Please provide the License Type."
    ),

    (
        "user_type",
        "Please specify whether you are a Developer or Business User."
    ),

    (
        "issue_description",
        "Please provide a clear description of the issue."
    ),

    (
        "application_link",
        "Please provide the Application Link. "
        "The Application Link should be included in the ticket comments."
    )
]


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Qlik Sense AI Support Assistant is running!"
    }


# =========================================================
# RESET
# =========================================================

@app.post("/reset")
def reset_conversation():

    conversation.reset()

    return {
        "status": "reset",
        "message": "New conversation started."
    }


# =========================================================
# CHAT
# =========================================================

@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message.strip()


    # =====================================================
    # EMPTY MESSAGE
    # =====================================================

    if not user_message:

        return {
            "status": "error",
            "response": "Please describe your Qlik Sense issue."
        }


    # =====================================================
    # GENERAL GREETING / HELP
    # =====================================================

    general_message = detect_general_message(
        user_message
    )


    if general_message == "greeting":

        return {
            "status": "general",
            "response": (
                "Hello! I'm your Qlik Sense Support Assistant.\n\n"

                "I can help you troubleshoot common Qlik Sense "
                "issues step by step.\n\n"

                "I can help with:\n"
                "• Login issues\n"
                "• Password issues\n"
                "• Browser compatibility issues\n"
                "• Access issues\n"
                "• Support ticket information and guidance\n\n"

                "Please describe your Qlik Sense issue or select "
                "an issue from the options below."
            )
        }


    if general_message == "help":

        return {
            "status": "general",
            "response": (
                "I can help you with common Qlik Sense support "
                "issues step by step.\n\n"

                "Supported areas:\n"
                "• Login issues\n"
                "• Password issues\n"
                "• Browser compatibility issues\n"
                "• Access issues\n"
                "• Correct support ticket information\n\n"

                "For troubleshooting issues, I will guide you "
                "through one step at a time."
            )
        }


    # =====================================================
    # TICKET INFORMATION COLLECTION
    # =====================================================

    if conversation.ticket_collection_active:

        current_index = conversation.ticket_field_index


        if current_index < len(TICKET_FIELDS):

            field_name, next_question = TICKET_FIELDS[
                current_index
            ]


            # -------------------------------------------------
            # Save user's answer
            # -------------------------------------------------

            conversation.ticket_data[
                field_name
            ] = user_message


            # Move to next field
            conversation.ticket_field_index += 1


            # -------------------------------------------------
            # MORE INFORMATION REQUIRED
            # -------------------------------------------------

            if conversation.ticket_field_index < len(
                TICKET_FIELDS
            ):

                next_field_name, next_question = TICKET_FIELDS[
                    conversation.ticket_field_index
                ]

                return {
                    "status": "ticket_information",
                    "category": "incorrect_ticket",
                    "step": conversation.ticket_field_index + 1,
                    "response": next_question
                }


            # -------------------------------------------------
            # ALL INFORMATION COLLECTED
            # -------------------------------------------------

            conversation.ticket_collection_active = False

            conversation.ticket_information_complete = True


            ticket_data = conversation.ticket_data


            application_name = ticket_data.get(
                "application_name",
                ""
            )

            environment = ticket_data.get(
                "environment",
                ""
            )

            license_type = ticket_data.get(
                "license_type",
                ""
            )

            user_type = ticket_data.get(
                "user_type",
                ""
            )

            issue_description = ticket_data.get(
                "issue_description",
                ""
            )

            application_link = ticket_data.get(
                "application_link",
                ""
            )


            return {
                "status": "ticket_information_complete",
                "category": "incorrect_ticket",
                "ticket_data": ticket_data,
                "response": (
                    "Thank you. I have collected the following "
                    "information for your support ticket.\n\n"

                    f"Application Name: {application_name}\n"
                    f"Environment: {environment}\n"
                    f"License Type: {license_type}\n"
                    f"User Type: {user_type}\n"
                    f"Issue Description: {issue_description}\n"
                    f"Application Link: {application_link}\n\n"

                    "Please use the above information to create "
                    "the support ticket through your standard "
                    "support channel."
                )
            }


    # =====================================================
    # EXPLICIT TICKET INFORMATION REQUEST
    # =====================================================
    #
    # IMPORTANT:
    # This block comes BEFORE normal troubleshooting.
    #
    # Therefore, if the user is currently troubleshooting
    # Password/Login/Browser/Access and selects:
    #
    # "Support ticket information and guidance"
    #
    # the ticket workflow will start immediately.
    #
    # It will NOT ask:
    # "Is the issue resolved?"
    #
    # =====================================================

    explicit_category = detect_category_by_keywords(
        user_message
    )


    if explicit_category == "incorrect_ticket":

        conversation.start_ticket_collection()


        first_field_name, first_question = TICKET_FIELDS[0]


        return {
            "status": "ticket_information",
            "category": "incorrect_ticket",
            "step": 1,
            "response": (
                "Sure. I can help you prepare the "
                "information needed for a support ticket.\n\n"
                f"{first_question}"
            )
        }


    # =====================================================
    # AFTER TICKET INFORMATION IS COMPLETE
    # =====================================================

    if conversation.ticket_information_complete:

        conversation.reset()

        return {
            "status": "closed",
            "response": (
                "Thank you. Please let me know if you face any issues."
            )
        }


    # =====================================================
    # TICKET SUGGESTION AFTER TROUBLESHOOTING
    # =====================================================

    if conversation.ticket_required:

        ticket_response = detect_ticket_response(
            user_message
        )


        # -------------------------------------------------
        # YES
        # -------------------------------------------------

        if ticket_response == "yes":

            conversation.reset()

            return {
                "status": "ticket_suggested",
                "response": (
                    "Please create a support ticket through your "
                    "standard support channel for further assistance."
                )
            }


        # -------------------------------------------------
        # NO
        # -------------------------------------------------

        if ticket_response == "no":

            conversation.reset()

            return {
                "status": "closed",
                "response": (
                    "Okay. No support ticket will be created. "
                    "Please let me know if you face any issues."
                )
            }


        # -------------------------------------------------
        # ANY OTHER WORD
        # -------------------------------------------------

        conversation.reset()

        return {
            "status": "closed",
            "response": (
                "Thank you. Please let me know if you face any issues."
            )
        }


    # =====================================================
    # NORMAL TROUBLESHOOTING
    # =====================================================

    if conversation.category and conversation.awaiting_resolution:

        resolution = detect_resolution(
            user_message
        )


        # -------------------------------------------------
        # RESOLVED
        # -------------------------------------------------

        if resolution == "yes":

            category_name = conversation.category.replace(
                "_",
                " "
            ).title()


            conversation.reset()


            return {
                "status": "resolved",
                "response": (
                    f"Great! Your {category_name} issue has "
                    "been resolved. No support ticket is required."
                )
            }


        # -------------------------------------------------
        # NOT RESOLVED
        # -------------------------------------------------

        if resolution == "no":

            next_step_number = (
                conversation.current_step + 1
            )


            next_step = get_next_step(
                conversation.category,
                next_step_number
            )


            # -------------------------------------------------
            # NEXT STEP AVAILABLE
            # -------------------------------------------------

            if next_step:

                conversation.current_step = (
                    next_step_number
                )

                conversation.add_attempted_step(
                    next_step
                )

                conversation.awaiting_resolution = True


                return {
                    "status": "troubleshooting",
                    "category": conversation.category,
                    "step": next_step_number + 1,
                    "response": (
                        f"{next_step}\n\n"
                        "Please try this step and let me know "
                        "whether the issue is resolved."
                    )
                }


            # -------------------------------------------------
            # ALL STEPS COMPLETED
            # -------------------------------------------------

            conversation.awaiting_resolution = False

            conversation.ticket_required = True


            return {
                "status": "ticket_suggestion",
                "response": (
                    "The troubleshooting steps have been completed, "
                    "but the issue is still not resolved.\n\n"

                    "Please create a support ticket through your "
                    "standard support channel for further assistance."
                )
            }


        # -------------------------------------------------
        # INVALID RESOLUTION RESPONSE
        # -------------------------------------------------

        return {
            "status": "waiting_for_resolution",
            "response": (
                "Please let me know whether the issue is "
                "resolved or still occurring."
            )
        }


    # =====================================================
    # DIRECT KEYWORD CLASSIFICATION
    # =====================================================

    detected_category = detect_category_by_keywords(
        user_message
    )


    # =====================================================
    # GEMINI CLASSIFICATION
    # =====================================================
    #
    # Used when direct keywords cannot identify the issue.
    #
    # =====================================================

    if not detected_category:

        try:

            classification_prompt = f"""
You are a Qlik Sense Support Assistant.

Classify the user's issue into exactly ONE category.

Available categories:

login
password
browser
access
incorrect_ticket

Definitions:

login:
The user cannot log in to Qlik Sense or is experiencing
a login failure.

password:
The user has forgotten, entered incorrectly, or needs to
reset their password.

browser:
The user is experiencing a browser compatibility or
browser-related problem.

access:
The user cannot access a Qlik Sense application, stream,
resource, or required functionality.

incorrect_ticket:
The user needs help creating a correct Qlik support ticket
or needs guidance about information required for a ticket.

User message:
{user_message}

Return ONLY one category name.
"""


            category_response = ask_gemini(
                classification_prompt
            )


            category_text = (
                category_response.strip().lower()
            )


            valid_categories = [
                "login",
                "password",
                "browser",
                "access",
                "incorrect_ticket"
            ]


            for category in valid_categories:

                if category in category_text:

                    detected_category = category

                    break


        except Exception as e:

            print(
                "Gemini classification error:",
                str(e)
            )


    # =====================================================
    # UNKNOWN / UNSUPPORTED MESSAGE
    # =====================================================

    if not detected_category:

        return {
            "status": "general",
            "response": (
                "I can help with common Qlik Sense support issues.\n\n"

                "I can help you with:\n"
                "• Login issues\n"
                "• Password issues\n"
                "• Browser compatibility issues\n"
                "• Access issues\n"
                "• Support ticket information and guidance\n\n"

                "Please describe your Qlik Sense issue in a little "
                "more detail."
            )
        }


    # =====================================================
    # CORRECT TICKET WORKFLOW
    # =====================================================

    if detected_category == "incorrect_ticket":

        conversation.start_ticket_collection()


        first_field_name, first_question = TICKET_FIELDS[0]


        return {
            "status": "ticket_information",
            "category": "incorrect_ticket",
            "step": 1,
            "response": (
                "Sure. I can help you prepare the "
                "information needed for a support ticket.\n\n"
                f"{first_question}"
            )
        }


    # =====================================================
    # START NORMAL TROUBLESHOOTING
    # =====================================================

    conversation.start(
        detected_category
    )


    first_step = get_next_step(
        detected_category,
        0
    )


    # -----------------------------------------------------
    # NO STEP AVAILABLE
    # -----------------------------------------------------

    if not first_step:

        conversation.ticket_required = True

        conversation.awaiting_resolution = False


        return {
            "status": "ticket_suggestion",
            "response": (
                "The troubleshooting steps have been completed, "
                "but the issue is still not resolved.\n\n"

                "Please create a support ticket through your "
                "standard support channel for further assistance."
            )
        }


    # -----------------------------------------------------
    # SAVE FIRST STEP
    # -----------------------------------------------------

    conversation.add_attempted_step(
        first_step
    )


    return {
        "status": "troubleshooting",
        "category": detected_category,
        "step": 1,
        "response": (
            f"{first_step}\n\n"
            "Please try this step and let me know "
            "whether the issue is resolved."
        )
    }