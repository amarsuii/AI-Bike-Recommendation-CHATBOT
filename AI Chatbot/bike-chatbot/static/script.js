const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

function appendMessage(text, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");

    // FORCE bot replies to show HTML (even if textContent appears somewhere)
    if (sender === "bot") {
        bubble.insertAdjacentHTML("beforeend", text);
    } else {
        bubble.textContent = text;
    }

    msgDiv.appendChild(bubble);
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage(text, "user");
    userInput.value = "";

    const loading = document.createElement("div");
    loading.classList.add("message", "bot");
    loading.innerHTML = `<div class="bubble">⏳ Searching bikes...</div>`;
    chatWindow.appendChild(loading);

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await res.json();
        loading.remove();
        appendMessage(data.reply, "bot");
    } catch (err) {
        loading.remove();
        appendMessage("⚠️ Server error, try again.", "bot");
    }
});
