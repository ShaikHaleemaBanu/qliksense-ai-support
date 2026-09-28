console.log("QLIK SUPPORT ASSISTANT UI - VERSION 3");


// ==================================================
// ELEMENTS
// ==================================================

const chatContainer =
    document.getElementById("chat-container");

const messageInput =
    document.getElementById("message-input");

const sendButton =
    document.getElementById("send-button");

const quickOptions =
    document.getElementById("quick-options");

const newChatButton =
    document.getElementById("new-chat-button");


// ==================================================
// ADD MESSAGE
// ==================================================

function addMessage(message, sender) {

    const messageWrapper =
        document.createElement("div");

    messageWrapper.classList.add(
        "message",
        sender === "user"
            ? "user-message"
            : "assistant-message"
    );


    // Avatar
    const avatar =
        document.createElement("div");

    avatar.classList.add("avatar");

    avatar.textContent =
        sender === "user"
            ? "You"
            : "AI";


    // Message content
    const messageContent =
        document.createElement("div");

    messageContent.classList.add(
        "message-content"
    );


    // Split lines
    const lines =
        message.split("\n");


    lines.forEach(line => {

        if (line.trim() !== "") {

            const paragraph =
                document.createElement("p");

            paragraph.textContent =
                line;

            messageContent.appendChild(
                paragraph
            );
        }

    });


    messageWrapper.appendChild(
        avatar
    );

    messageWrapper.appendChild(
        messageContent
    );

    chatContainer.appendChild(
        messageWrapper
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


// ==================================================
// SHOW TYPING INDICATOR
// ==================================================

function showTyping() {

    // Prevent duplicate indicators
    if (
        document.getElementById(
            "typing-indicator"
        )
    ) {
        return;
    }


    const typingWrapper =
        document.createElement("div");

    typingWrapper.id =
        "typing-indicator";

    typingWrapper.classList.add(
        "message",
        "assistant-message"
    );


    // AI avatar
    const avatar =
        document.createElement("div");

    avatar.classList.add("avatar");

    avatar.textContent =
        "AI";


    // Typing content
    const typingContent =
        document.createElement("div");

    typingContent.classList.add(
        "message-content",
        "typing-content"
    );


    const typingText =
        document.createElement("span");

    typingText.textContent =
        "AI is typing";


    // Animated dots
    const dots =
        document.createElement("span");

    dots.classList.add(
        "typing-dots"
    );

    dots.innerHTML =
        "<span>.</span><span>.</span><span>.</span>";


    typingContent.appendChild(
        typingText
    );

    typingContent.appendChild(
        dots
    );


    typingWrapper.appendChild(
        avatar
    );

    typingWrapper.appendChild(
        typingContent
    );


    chatContainer.appendChild(
        typingWrapper
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


// ==================================================
// HIDE TYPING INDICATOR
// ==================================================

function hideTyping() {

    const typing =
        document.getElementById(
            "typing-indicator"
        );

    if (typing) {

        typing.remove();

    }
}


// ==================================================
// WAIT FUNCTION
// ==================================================

function wait(milliseconds) {

    return new Promise(
        resolve => {

            setTimeout(
                resolve,
                milliseconds
            );

        }
    );
}


// ==================================================
// DISABLE / ENABLE CONTROLS
// ==================================================

function setControlsDisabled(
    disabled
) {

    sendButton.disabled =
        disabled;

    messageInput.disabled =
        disabled;


    document
        .querySelectorAll(".issue-button")
        .forEach(button => {

            button.disabled =
                disabled;

        });
}


// ==================================================
// TYPEWRITER EFFECT
// ==================================================

async function typeAssistantMessage(
    message
) {

    const messageWrapper =
        document.createElement("div");

    messageWrapper.classList.add(
        "message",
        "assistant-message"
    );


    // AI avatar
    const avatar =
        document.createElement("div");

    avatar.classList.add(
        "avatar"
    );

    avatar.textContent =
        "AI";


    // Content
    const messageContent =
        document.createElement("div");

    messageContent.classList.add(
        "message-content"
    );


    messageWrapper.appendChild(
        avatar
    );

    messageWrapper.appendChild(
        messageContent
    );


    chatContainer.appendChild(
        messageWrapper
    );


    // Split message into lines
    const lines =
        message.split("\n");


    for (
        let lineIndex = 0;
        lineIndex < lines.length;
        lineIndex++
    ) {

        const line =
            lines[lineIndex];


        // Ignore empty lines
        if (
            line.trim() === ""
        ) {

            continue;

        }


        const paragraph =
            document.createElement("p");


        messageContent.appendChild(
            paragraph
        );


        // Type each character
        for (
            let i = 0;
            i < line.length;
            i++
        ) {

            paragraph.textContent +=
                line.charAt(i);


            chatContainer.scrollTop =
                chatContainer.scrollHeight;


            // Typing speed
            await wait(18);

        }


        // Small pause between paragraphs
        await wait(120);

    }


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


// ==================================================
// SEND MESSAGE
// ==================================================

async function sendMessage(
    messageFromButton = null
) {

    const message =
        messageFromButton ||
        messageInput.value.trim();


    // Don't send empty messages
    if (!message) {

        return;

    }


    // ----------------------------------------------
    // Show user message immediately
    // ----------------------------------------------

    addMessage(
        message,
        "user"
    );


    // Clear input
    messageInput.value = "";


    // Hide quick buttons
    if (quickOptions) {

        quickOptions.style.display =
            "none";

    }


    // Disable controls
    setControlsDisabled(
        true
    );


    // ----------------------------------------------
    // Show typing indicator
    // ----------------------------------------------

    showTyping();


    try {

        // ------------------------------------------
        // Start backend request
        // ------------------------------------------

        const responsePromise =
            fetch(
                "http://127.0.0.1:8000/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );


        // ------------------------------------------
        // Minimum typing time
        // ------------------------------------------

        const minimumTypingTime =
            wait(2500);


        // Wait for both backend
        // and minimum typing time
        const [
            response
        ] = await Promise.all([
            responsePromise,
            minimumTypingTime
        ]);


        // ------------------------------------------
        // Check response
        // ------------------------------------------

        if (!response.ok) {

            throw new Error(
                `Server returned ${response.status}`
            );

        }


        // ------------------------------------------
        // Read JSON
        // ------------------------------------------

        const data =
            await response.json();


        // ------------------------------------------
        // Hide typing indicator
        // ------------------------------------------

        hideTyping();


        // ------------------------------------------
        // Type AI response
        // ------------------------------------------

        await typeAssistantMessage(
            data.response ||
            "No response received."
        );


    } catch (error) {

        console.error(
            "Connection error:",
            error
        );


        // Hide typing
        hideTyping();


        // Show error
        await typeAssistantMessage(
            "Sorry, I could not connect to the Qlik Sense Support Assistant. Please make sure the backend server is running."
        );


    } finally {

        // Enable controls
        setControlsDisabled(
            false
        );


        // Focus input
        messageInput.focus();

    }
}


// ==================================================
// SEND BUTTON
// ==================================================

sendButton.addEventListener(
    "click",
    () => {

        sendMessage();

    }
);


// ==================================================
// ENTER KEY
// ==================================================

messageInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter"
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


// ==================================================
// QUICK ISSUE BUTTONS
// ==================================================

document
    .querySelectorAll(".issue-button")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const message =
                    button.getAttribute(
                        "data-message"
                    );


                if (message) {

                    sendMessage(
                        message
                    );

                }

            }
        );

    });


// ==================================================
// NEW CONVERSATION
// ==================================================

newChatButton.addEventListener(
    "click",
    async () => {

        try {

            await fetch(
                "http://127.0.0.1:8000/reset",
                {
                    method: "POST"
                }
            );

        } catch (error) {

            console.error(
                "Reset error:",
                error
            );

        }


        // Clear chat
        chatContainer.innerHTML =
            "";


        // Welcome message
        addMessage(
            "Hello! I'm your Qlik Sense Support Assistant.\n\nI can help you troubleshoot common Qlik Sense issues step by step.\n\nSelect an issue below or describe your problem.",
            "assistant"
        );


        // Show quick options
        if (quickOptions) {

            quickOptions.style.display =
                "flex";

        }


        // Clear input
        messageInput.value =
            "";


        // Enable controls
        setControlsDisabled(
            false
        );


        // Focus input
        messageInput.focus();

    }
);