const API = "http://localhost:8000";

const chat = document.getElementById("chat-box");
const input = document.getElementById("user-input");

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = sender === "user" ? "user-msg" : "bot-msg";
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  addMessage(msg, "user");
  input.value = "";

  let fd = new FormData();
  fd.append("question", msg);

  let res = await fetch(`${API}/ask`, { method: "POST", body: fd });
  let data = await res.json();

  addMessage(data.answer, "bot");
}

input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

async function uploadNotes() {
  let file = document.getElementById("notes-upload").files[0];
  let fd = new FormData();
  fd.append("file", file);

  await fetch(`${API}/upload-notes`, { method: "POST", body: fd });
  addMessage("Notes uploaded successfully!", "bot");
}
