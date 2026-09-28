TROUBLESHOOTING_FLOWS = {

    # ---------------------------------------------------------
    # LOGIN FAILURE
    # ---------------------------------------------------------
    "login": [
        "Please verify that you are using the correct Qlik Sense login URL.",
        
        "Please verify that you are entering the correct username and password.",
        
        "Please check the password status and confirm that the password is active and has not expired.",
        
        "Please clear your browser cache and history, then try logging in again.",
        
        "Please try logging in using another supported browser.",
        
        "Please check your VPN and network connection and make sure you are connected correctly.",
        
        "If you are facing issues while logging in to the Merck environment, please use the Merck login portal to reset your password: https://me.merckgroup.com/"
    ],


    # ---------------------------------------------------------
    # PASSWORD
    # ---------------------------------------------------------
    "password": [
        "Please check that Caps Lock is turned off and verify that your keyboard is working correctly.",
        
        "Please try entering your password again carefully.",
        
        "If you are still unable to log in, please reset your password.",
        
        "If you are facing issues while logging in to the Merck environment, please use the Merck login portal to reset your password: https://me.merckgroup.com/"
    ],


    # ---------------------------------------------------------
    # BROWSER COMPATIBILITY
    # ---------------------------------------------------------
    "browser": [
        "Please check that you are using a supported browser.",
        
        "Please clear your browser cache and history, then try accessing Qlik Sense again.",
        
        "Please check your browser extensions and temporarily disable any extensions that may interfere with Qlik Sense.",
        
        "Please update your browser to the latest supported version.",
        
        "Please check your VPN and network connection and make sure you are connected correctly."
    ],


    # ---------------------------------------------------------
    # ACCESS ISSUES
    # ---------------------------------------------------------
    "access": [
        "Please refresh Qlik Sense and log in again.",
        
        "Please clear your browser cache and history, then try accessing Qlik Sense again.",
        
        "Please update your browser to the latest supported version.",
        
        "Please check your VPN and network connection and make sure you are connected correctly.",
        
        "Please verify that you are using a supported browser."
    ],


    # ---------------------------------------------------------
    # CORRECT TICKET WORKFLOW
    # ---------------------------------------------------------
    "incorrect_ticket": [
        "Please provide the Application Name.",
        
        "Please provide the Environment.",
        
        "Please provide the License Type.",
        
        "Please specify whether you are a Developer or Business User.",
        
        "Please provide a clear description of the issue.",
        
        "Please provide the Application Link. The Application Link should be included in the ticket comments."
    ]
}


# ---------------------------------------------------------
# GET NEXT TROUBLESHOOTING STEP
# ---------------------------------------------------------

def get_next_step(category: str, current_step: int):

    steps = TROUBLESHOOTING_FLOWS.get(category)

    if not steps:
        return None

    if current_step >= len(steps):
        return None

    return steps[current_step]


# ---------------------------------------------------------
# GET TOTAL NUMBER OF STEPS
# ---------------------------------------------------------

def get_total_steps(category: str):

    steps = TROUBLESHOOTING_FLOWS.get(category)

    if not steps:
        return 0

    return len(steps)