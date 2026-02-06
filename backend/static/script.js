let lastAnswerText = "";

// ----------------------------------
// SESSION MANAGEMENT
// ----------------------------------
// Generate a unique ID for this browser tab. Resets on refresh.
const session_id = "sess_" + Math.random().toString(36).substr(2, 9);
console.log("Current Session ID:", session_id);

// ----------------------------------
// ADD MESSAGE TO CHAT
// ----------------------------------
function appendMessage(text, sender) {
    const chatBox = document.getElementById("chatBox");

    const bubble = document.createElement("div");
    bubble.classList.add("chat-message", sender);
    bubble.innerText = text;

    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ----------------------------------
// SEND MESSAGE
// ----------------------------------
async function sendMessage() {
    const input = document.getElementById("userInput");
    const question = input.value.trim();

    if (!question) return;

    appendMessage(question, "user");
    input.value = "";

    const formData = new FormData();
    formData.append("question", question);
    formData.append("session_id", session_id); // Send ID so AI knows which notes to check

    try {
        const res = await fetch("/ask", {
            method: "POST",
            body: formData,
        });

        const data = await res.json();
        const answer = data.answer;

        lastAnswerText = answer;
        appendMessage(answer, "ai");
    } catch (err) {
        console.error(err);
        appendMessage("Error: Could not connect to the server.", "ai");
    }
}

// ENTER KEY LISTENER
document.getElementById("userInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

// ----------------------------------
// UPLOAD NOTES
// ----------------------------------
async function uploadNotes() {
    const fileInput = document.getElementById("notesFile");
    if (!fileInput.files.length) return alert("Choose a file.");

    // ADMIN TRICK: Hold SHIFT while clicking "Upload" to make files permanent (Global)
    const isAdmin = window.event.shiftKey; 

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("session_id", session_id);
    formData.append("is_admin", isAdmin); 

    if (isAdmin) {
        alert("Uploading as ADMIN... This file will be visible to everyone forever.");
    }

    try {
        const res = await fetch("/upload-notes", {
            method: "POST",
            body: formData,
        });

        const data = await res.json();
        alert(data.message);
    } catch (err) {
        console.error(err);
        alert("Upload failed.");
    }
}

// ----------------------------------
// VOICE → TEXT (No changes needed)
// ----------------------------------
async function convertVoice() {
    const fileInput = document.getElementById("voiceFile");
    if (!fileInput.files.length) return alert("Choose audio.");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const res = await fetch("/voice-to-text", {
        method: "POST",
        body: formData,
    });

    const data = await res.json();

    document.getElementById("userInput").value = data.text;
    appendMessage("🎤 Voice Input: " + data.text, "user");
}

// ----------------------------------
// TEXT → VOICE (No changes needed)
// ----------------------------------
async function textToVoice() {
    if (!lastAnswerText) return alert("No answer yet.");

    const formData = new FormData();
    formData.append("text", lastAnswerText);

    const res = await fetch("/text-to-voice", {
        method: "POST",
        body: formData,
    });

    const data = await res.json();
    new Audio("/" + data.audio).play();
}