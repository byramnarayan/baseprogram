/**
 * static/js/aihelp.js
 * Chat + Voice (Sarvam STT/TTS) interaction logic.
 */

let currentConversationId = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// ── Init ────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  if (!getToken()) { window.location.href = "/login"; return; }
  loadConversationList();
  document.getElementById("chat-input")?.focus();
});

// ── Auth ────────────────────────────────────────────────────────────────────
function getToken() { return localStorage.getItem("access_token") || ""; }
function authHeaders() {
  return { "Content-Type": "application/json", "Authorization": `Bearer ${getToken()}` };
}

// ── Text Chat ───────────────────────────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;
  appendMessage("user", message);
  input.value = ""; autoResize(input);
  const typingEl = showTyping(); toggleSend(false);

  try {
    const res = await fetch("/aihelp/chat", {
      method: "POST", headers: authHeaders(),
      body: JSON.stringify({ message, conversation_id: currentConversationId }),
    });
    if (res.status === 401) { window.location.href = "/login"; return; }
    if (!res.ok) { const e = await res.json().catch(()=>({})); throw new Error(e.detail||"Server error"); }
    const data = await res.json();
    currentConversationId = data.conversation_id;
    typingEl.remove();
    appendMessage("assistant", data.response, data.sources || []);
    loadConversationList();
  } catch(err) {
    typingEl.remove();
    appendMessage("assistant", `Sorry, something went wrong: ${err.message}`);
  } finally {
    toggleSend(true);
    document.getElementById("chat-input")?.focus();
  }
}

// ── Voice ────────────────────────────────────────────────────────────────────
async function toggleVoice() {
  if (isRecording) {
    stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
    mediaRecorder.onstop = () => { stream.getTracks().forEach(t => t.stop()); processVoiceInput(); };

    mediaRecorder.start();
    isRecording = true;
    setOrbState("listening", "Listening…");
    document.getElementById("mic-btn").classList.add("recording");
  } catch(err) {
    setOrbState("idle", "Mic access denied");
    console.error("Microphone error:", err);
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    document.getElementById("mic-btn").classList.remove("recording");
    setOrbState("thinking", "Processing…");
  }
}

async function processVoiceInput() {
  const blob = new Blob(audioChunks, { type: "audio/webm" });
  const lang = document.getElementById("voice-lang")?.value || "hi-IN";

  const formData = new FormData();
  formData.append("audio", blob, "audio.webm");
  if (currentConversationId) formData.append("conversation_id", currentConversationId);
  formData.append("language", lang);

  try {
    const res = await fetch("/aihelp/voice/chat", {
      method: "POST",
      headers: { "Authorization": `Bearer ${getToken()}` },
      body: formData,
    });

    if (res.status === 401) { window.location.href = "/login"; return; }

    // Check if we got audio back
    const contentType = res.headers.get("content-type") || "";

    if (contentType.includes("audio")) {
      // Success: got WAV audio back
      const transcript   = res.headers.get("X-Transcript") || "";
      const responseText = res.headers.get("X-Response") || "";
      const convId       = res.headers.get("X-Conversation-Id");

      if (convId) currentConversationId = parseInt(convId);
      if (transcript) {
        setTranscript(`"${transcript}"`);
        appendMessage("user", transcript);
      }
      if (responseText) appendMessage("assistant", responseText);

      // Play audio
      const audioBlob = await res.blob();
      playAudio(audioBlob);
      loadConversationList();
    } else {
      // Fallback JSON response (TTS failed but text is ok)
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Voice chat failed");
      if (data.transcript) { setTranscript(`"${data.transcript}"`); appendMessage("user", data.transcript); }
      if (data.response)   appendMessage("assistant", data.response);
      if (data.conversation_id) currentConversationId = data.conversation_id;
      loadConversationList();
    }

  } catch(err) {
    console.error("Voice chat error:", err);
    appendMessage("assistant", `Voice error: ${err.message}`);
  } finally {
    setOrbState("idle", "Tap mic to speak");
    audioChunks = [];
  }
}

function playAudio(blob) {
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  setOrbState("thinking", "Speaking…");
  audio.onended = () => { setOrbState("idle", "Tap mic to speak"); URL.revokeObjectURL(url); };
  audio.onerror = ()  => { setOrbState("idle", "Tap mic to speak"); URL.revokeObjectURL(url); };
  audio.play().catch(console.error);
}

// ── Voice text input ─────────────────────────────────────────────────────────
function voiceTextKeyDown(e) {
  if (e.key === "Enter") voiceTextSend();
}
async function voiceTextSend() {
  const input = document.getElementById("voice-text");
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  // Send via text pipeline and speak the response
  appendMessage("user", message);
  const typingEl = showTyping();
  try {
    const res = await fetch("/aihelp/chat", {
      method: "POST", headers: authHeaders(),
      body: JSON.stringify({ message, conversation_id: currentConversationId }),
    });
    const data = await res.json();
    currentConversationId = data.conversation_id;
    typingEl.remove();
    appendMessage("assistant", data.response, data.sources || []);
    loadConversationList();

    // Speak the response via TTS
    const lang = document.getElementById("voice-lang")?.value || "hi-IN";
    const formData = new FormData();
    formData.append("text", data.response);
    formData.append("language", lang);
    const ttsRes = await fetch("/aihelp/voice/speak", {
      method: "POST",
      headers: { "Authorization": `Bearer ${getToken()}` },
      body: formData,
    });
    if (ttsRes.ok) {
      const audioBlob = await ttsRes.blob();
      playAudio(audioBlob);
    }
  } catch(err) {
    typingEl.remove();
    appendMessage("assistant", `Error: ${err.message}`);
  }
}

// ── Orb helpers ──────────────────────────────────────────────────────────────
function setOrbState(state, statusText) {
  const orb = document.getElementById("voice-orb");
  const status = document.getElementById("orb-status");
  orb.className = "orb" + (state !== "idle" ? ` ${state}` : "");
  if (status) status.textContent = statusText;
}
function setTranscript(text) {
  const el = document.getElementById("voice-transcript");
  if (el) el.textContent = text;
}

// ── Render helpers ────────────────────────────────────────────────────────────
function appendMessage(role, content, sources = []) {
  const container = document.getElementById("chat-messages");
  const msgEl = document.createElement("div");
  msgEl.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;
  msgEl.appendChild(bubble);
  container.appendChild(msgEl);
  if (role === "assistant" && sources.length > 0) container.appendChild(buildSourcesPanel(sources));
  container.scrollTop = container.scrollHeight;
}

function buildSourcesPanel(sources) {
  const panel = document.createElement("div"); panel.className = "sources-panel";
  const toggle = document.createElement("span"); toggle.className = "sources-toggle";
  toggle.textContent = `📄 ${sources.length} source${sources.length>1?"s":""}`;
  const list = document.createElement("div"); list.className = "sources-list";
  sources.forEach(s => {
    const item = document.createElement("div"); item.className = "source-item";
    item.textContent = s.text.length>140 ? s.text.substring(0,140)+"…" : s.text;
    list.appendChild(item);
  });
  toggle.addEventListener("click", () => list.classList.toggle("open"));
  panel.appendChild(toggle); panel.appendChild(list);
  return panel;
}

function showTyping() {
  const container = document.getElementById("chat-messages");
  const el = document.createElement("div");
  el.className = "message assistant typing-indicator";
  el.innerHTML = `<div class="bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
  return el;
}

// ── Conversation Sidebar ──────────────────────────────────────────────────────
async function loadConversationList() {
  if (!getToken()) return;
  try {
    const res = await fetch("/aihelp/conversations", { headers: authHeaders() });
    if (!res.ok) return;
    renderConversationList(await res.json());
  } catch {}
}

function renderConversationList(conversations) {
  const list = document.getElementById("conversation-list"); list.innerHTML = "";
  if (!conversations.length) {
    const e = document.createElement("div");
    e.style.cssText = "font-size:.78rem;color:#658C58;padding:.5rem .25rem;";
    e.textContent = "No conversations yet."; list.appendChild(e); return;
  }
  const label = document.createElement("div"); label.className = "sidebar-label";
  label.textContent = "Recent"; list.appendChild(label);
  conversations.forEach(conv => {
    const item = document.createElement("div");
    item.className = `conv-item${conv.id===currentConversationId?" active":""}`;
    item.textContent = conv.title || "New conversation";
    item.title = conv.title || "";
    item.onclick = () => loadConversation(conv.id);
    list.appendChild(item);
  });
}

async function loadConversation(convId) {
  try {
    const res = await fetch(`/aihelp/conversations/${convId}`, { headers: authHeaders() });
    if (!res.ok) return;
    const conv = await res.json();
    currentConversationId = conv.id;
    const container = document.getElementById("chat-messages"); container.innerHTML = "";
    conv.messages.forEach(msg => appendMessage(msg.role, msg.content));
    loadConversationList();
  } catch {}
}

function startNewConversation() {
  currentConversationId = null;
  document.getElementById("chat-messages").innerHTML = `
    <div class="message assistant"><div class="bubble">Starting fresh — what would you like to know? 🌱</div></div>`;
  setTranscript("");
  setOrbState("idle", "Tap mic to speak");
  loadConversationList();
  document.getElementById("chat-input")?.focus();
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function handleKeyDown(e) { if (e.key==="Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }
function autoResize(el) { el.style.height="auto"; el.style.height=Math.min(el.scrollHeight,140)+"px"; }
function toggleSend(enabled) { const b=document.getElementById("btn-send"); if(b) b.disabled=!enabled; }
