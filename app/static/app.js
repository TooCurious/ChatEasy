
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

const chatEl = document.getElementById("chat");
const formEl = document.getElementById("form");
const inputEl = document.getElementById("input");
const sendEl = document.getElementById("send");
const STORAGE_KEY = "modern-chat-messages:v1";

// Autosize textarea
function autosize() {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
}
inputEl.addEventListener("input", autosize);
window.addEventListener("load", autosize);

// Load/save
function loadMessages() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}
function saveMessages(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

let messages = loadMessages();
render(messages);

// Submit logic
formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text) return;

  const me = {
    id: generateId(),
    role: "user",
    text,
    time: Date.now()
  };

  messages.push(me);
  saveMessages(messages);
  inputEl.value = "";
  autosize();
  render(messages, true);

  // Sending a request to the backend
  requestAssistantReply(me);
});

// Enter → send, Shift+Enter → new line
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    formEl.requestSubmit();
  }
});

// Render
function render(list, scroll = false) {
  chatEl.innerHTML = "";
  list.forEach((msg) => {
    chatEl.appendChild(messageNode(msg));
  });
  if (scroll) scrollToBottom();
}

function messageNode(msg) {
  const wrap = document.createElement("section");
  wrap.className = `message ${msg.role === "user" ? "me" : "ai"}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const text = document.createElement("div");
  text.className = "content";
  text.textContent = msg.text;
  const time = document.createElement("span");
  time.className = "time";
  time.textContent = formatTime(msg.time);
  bubble.append(text, time);
  wrap.append(bubble);
  return wrap;
}

function formatTime(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scrollToBottom() {
  chatEl.scrollTop = chatEl.scrollHeight;
}



// Typing indicator
function showTyping() {
  const wrap = document.createElement("section");
  wrap.className = "message ai";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const dots = document.createElement("div");
  dots.className = "typing";
  dots.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
  const time = document.createElement("span");
  time.className = "time";
  time.textContent = "typing…";
  bubble.append(dots, time);
  wrap.append(bubble);
  chatEl.appendChild(wrap);
  scrollToBottom();
  return wrap;
}

async function requestAssistantReply(userMessage) {
  const typingEl = showTyping();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage.text })
    });

    if (!response.ok) {
      throw new Error(`Network response was not ok, status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    const aiMessageElement = document.createElement("section");
    aiMessageElement.className = "message ai";
    const aiBubble = document.createElement("div");
    aiBubble.className = "bubble";
    const aiText = document.createElement("div");
    aiText.className = "content";
    aiText.textContent = '';
    const aiTime = document.createElement("span");
    aiTime.className = "time";
    aiTime.textContent = "just now";
    aiBubble.append(aiText, aiTime);
    aiMessageElement.append(aiBubble);

    typingEl.remove();
    chatEl.appendChild(aiMessageElement);
    scrollToBottom();

    let firstLineReceived = false;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done || firstLineReceived) break;

        buffer += decoder.decode(value, { stream: true });

        console.log("Current buffer:", JSON.stringify(buffer));

            try {

              aiText.textContent = buffer;
              aiTime.textContent = formatTime(Date.now());

                const reply = {
                  id: generateId(),
                  role: "assistant",
                  text: buffer,
                  time: Date.now()
                };
                
                messages.push(reply);
                saveMessages(messages);
                render(messages, true);

                firstLineReceived = true; 
                break;
              
            } catch (e) {
              console.error('Error parsing SSE JSON:', e, 'Line:', buffer);
              aiText.textContent = `❌ Parsing Error`;
              aiTime.textContent = formatTime(Date.now());
              return;
            }
        
        if (firstLineReceived) break;
      }
    } finally {
      reader.releaseLock();
    }
  } catch (error) {
    console.error("Fetch error:", error);
    try { typingEl.remove(); } catch {}

    const errorReply = {
      id: generateId(),
      role: "assistant",
      text: `Error: Failed to receive a response from the server. (${error.message})`,
      time: Date.now()
    };
    messages.push(errorReply);
    saveMessages(messages);
    chatEl.appendChild(messageNode(errorReply));
    scrollToBottom();
  }
}