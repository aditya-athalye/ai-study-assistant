let lastAnswerText = "";

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

    // FIX: Removed "http://127.0.0.1:8000" to make it work on Render
    const res = await fetch("/ask", {
        method: "POST",
        body: formData,
    });

    const data = await res.json();
    const answer = data.answer;

    lastAnswerText = answer;
    appendMessage(answer, "ai");
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

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    // FIX: Removed localhost URL
    await fetch("/upload-notes", {
        method: "POST",
        body: formData,
    });

    alert("Notes uploaded!");
}

// ----------------------------------
// VOICE → TEXT
// ----------------------------------
async function convertVoice() {
    const fileInput = document.getElementById("voiceFile");
    if (!fileInput.files.length) return alert("Choose audio.");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    // FIX: Removed localhost URL
    const res = await fetch("/voice-to-text", {
        method: "POST",
        body: formData,
    });

    const data = await res.json();

    document.getElementById("userInput").value = data.text;
    appendMessage("🎤 Voice Input: " + data.text, "user");
}

// ----------------------------------
// TEXT → VOICE
// ----------------------------------
async function textToVoice() {
    if (!lastAnswerText) return alert("No answer yet.");

    const formData = new FormData();
    formData.append("text", lastAnswerText);

    // FIX: Removed localhost URL
    const res = await fetch("/text-to-voice", {
        method: "POST",
        body: formData,
    });

    const data = await res.json();

    // FIX: Added "/" to ensure it points to the root of the current site
    new Audio("/" + data.audio).play();
}