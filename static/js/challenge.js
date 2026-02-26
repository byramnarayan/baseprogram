/**
 * static/js/challenge.js
 * Plant discovery challenge: tree, streak, badges, upload modal, plant chat.
 */

let selectedFile = null;
let identifiedPlant = null;
let plantChatHistory = [];

// ── Auth guard + init ────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  if (!localStorage.getItem("access_token")) { window.location.href = "/login"; return; }
  await Promise.all([loadTree(), loadStreak(), loadBadges()]);
});

function authHeaders() {
  return { "Authorization": `Bearer ${localStorage.getItem("access_token") || ""}` };
}

// ── Tree ──────────────────────────────────────────────────────────────────────
async function loadTree() {
  try {
    const res = await fetch("/challenge/tree", { headers: authHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById("total-leaves").textContent = data.total_leaves;
    document.getElementById("tree-level").textContent   = data.tree_level;
    document.getElementById("total-points").textContent = data.total_points;
    renderTreeLeaves(data.total_leaves);
  } catch(e) {}
}

function renderTreeLeaves(count) {
  const group = document.getElementById("tree-leaves");
  group.innerHTML = "";
  const positions = [
    {cx:55,cy:115},{cx:72,cy:100},{cx:85,cy:88},{cx:105,cy:108},{cx:118,cy:93},{cx:100,cy:75},
    {cx:225,cy:103},{cx:218,cy:88},{cx:235,cy:75},{cx:200,cy:105},{cx:192,cy:88},{cx:208,cy:70},
    {cx:80,cy:140},{cx:92,cy:128},{cx:215,cy:130},{cx:205,cy:120},
    {cx:135,cy:155},{cx:165,cy:155},{cx:140,cy:85},{cx:160,cy:80},{cx:150,cy:68},
  ];
  const toRender = Math.min(count, positions.length);
  const colors = ["#52B788","#40916C","#BBC863","#74C69D","#2D6A4F"];
  for (let i = 0; i < toRender; i++) {
    const p = positions[i];
    const leaf = document.createElementNS("http://www.w3.org/2000/svg","ellipse");
    leaf.setAttribute("cx", p.cx);
    leaf.setAttribute("cy", p.cy);
    leaf.setAttribute("rx", 12 + (i % 3) * 2);
    leaf.setAttribute("ry", 8 + (i % 2) * 2);
    leaf.setAttribute("fill", colors[i % colors.length]);
    leaf.setAttribute("opacity","0.92");
    leaf.setAttribute("transform",`rotate(${(i*37)%60-30} ${p.cx} ${p.cy})`);
    leaf.style.animation = `leafGrow 0.5s ease ${i*0.04}s both`;
    group.appendChild(leaf);
  }
}

// ── Streak strip ──────────────────────────────────────────────────────────────
async function loadStreak() {
  try {
    const res = await fetch("/challenge/streak", { headers: authHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    const strip = document.getElementById("challenge-streak-strip");
    const today = new Date().toISOString().split("T")[0];
    const names = ["S","M","T","W","T","F","S"];
    strip.innerHTML = "";
    data.days.forEach(day => {
      const d = new Date(day.date + "T00:00:00");
      const isToday = day.date === today;
      const label = isToday ? "Today" : names[d.getDay()];
      const cls  = day.verified ? "ok" : (isToday ? "now" : "no");
      const icon = day.verified ? "✓" : (isToday ? "🌿" : "✕");
      strip.innerHTML += `<div class="s-day"><span class="s-label">${label}</span><span class="s-dot ${cls}">${icon}</span></div>`;
    });
  } catch(e) {}
}

// ── Badge Collection ──────────────────────────────────────────────────────────
async function loadBadges() {
  try {
    const res = await fetch("/challenge/badges", { headers: authHeaders() });
    if (!res.ok) return;
    const badges = await res.json();
    const grid  = document.getElementById("badge-grid");
    const empty = document.getElementById("badge-empty");
    grid.innerHTML = "";
    if (!badges.length) { empty.style.display="block"; return; }
    empty.style.display = "none";
    badges.forEach((b,i) => { grid.innerHTML += buildHexBadge(b,i); });
  } catch(e) {}
}

function buildHexBadge(badge, index) {
  const color = badge.badge_color || "#2D6A4F";
  const dark  = adjustColor(color, -30);
  const id    = `hex-${badge.id}`;
  const first = badge.is_first_global
    ? `<text x="50" y="18" text-anchor="middle" font-size="7" fill="#f59e0b" font-weight="bold">★ FIRST</text>` : "";
  const safeB = JSON.stringify(badge).replace(/"/g,'&quot;');
  return `
  <div class="hex-badge" onclick='showBadgeDetail(${safeB})'>
    <svg class="hex-svg" viewBox="0 0 100 115" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="${id}-g" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="${color}"/>
          <stop offset="100%" stop-color="${dark}"/>
        </linearGradient>
      </defs>
      <polygon points="50,5 93,27.5 93,72.5 50,95 7,72.5 7,27.5" fill="url(#${id}-g)" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>
      <text x="50" y="60" text-anchor="middle" font-size="30">${badge.emoji || "🌱"}</text>
      ${first}
    </svg>
    <span class="hex-label">${badge.common_name}</span>
  </div>`;
}

function showBadgeDetail(badge) {
  identifiedPlant = { ...badge, discovery_id: badge.id };
  populateResultStep(badge, false);
  document.getElementById("upload-modal").style.display = "flex";
  showStep("result");
}

function adjustColor(hex, amount) {
  const n = parseInt(hex.slice(1),16);
  const r = Math.max(0,Math.min(255,(n>>16)+amount));
  const g = Math.max(0,Math.min(255,((n>>8)&0xff)+amount));
  const b = Math.max(0,Math.min(255,(n&0xff)+amount));
  return `#${((1<<24)|(r<<16)|(g<<8)|b).toString(16).slice(1)}`;
}

// ── Upload Modal ───────────────────────────────────────────────────────────────
function openUploadModal() {
  selectedFile = null; identifiedPlant = null; plantChatHistory = [];
  document.getElementById("upload-modal").style.display = "flex";
  document.getElementById("preview-img").style.display  = "none";
  document.querySelector(".upload-placeholder").style.display = "flex";
  document.getElementById("btn-identify").disabled = true;
  document.getElementById("file-input").value = "";
  document.getElementById("plant-chat-messages").innerHTML = "";
  showStep("upload");
}
function closeUploadModal() { document.getElementById("upload-modal").style.display="none"; }
function closeAndRefresh()  { closeUploadModal(); loadTree(); loadStreak(); loadBadges(); }
function triggerFileInput() { document.getElementById("file-input").click(); }

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = ev => {
    const img = document.getElementById("preview-img");
    img.src = ev.target.result; img.style.display = "block";
    document.querySelector(".upload-placeholder").style.display = "none";
    document.getElementById("btn-identify").disabled = false;
  };
  reader.readAsDataURL(file);
}

async function submitIdentify() {
  if (!selectedFile) return;
  showStep("loading");
  const formData = new FormData();
  formData.append("image", selectedFile);
  try {
    const res = await fetch("/challenge/identify", {
      method: "POST", headers: authHeaders(), body: formData,
    });
    if (res.status === 401) { window.location.href="/login"; return; }
    if (!res.ok) {
      const err = await res.json().catch(()=>({}));
      alert(err.detail || "Could not identify. Try a clearer photo!");
      showStep("upload"); return;
    }
    const plant = await res.json();
    identifiedPlant = plant;
    plantChatHistory = [];
    document.getElementById("plant-chat-messages").innerHTML = "";
    if (plant.is_first_global) {
      document.getElementById("fd-plant-name").textContent = plant.common_name;
      document.getElementById("fd-points").textContent = `+${plant.points_earned}`;
      showStep("first-discovery");
    } else {
      populateResultStep(plant, false);
      showStep("result");
    }
    loadTree(); loadStreak();
  } catch(err) {
    alert("Network error. Please try again."); showStep("upload");
  }
}

function showResultStep() {
  populateResultStep(identifiedPlant, true); showStep("result");
}

function populateResultStep(plant, showFirstBadge) {
  document.getElementById("result-plant-name").textContent = plant.common_name || plant.common_name;
  document.getElementById("result-sci-name").textContent   = plant.scientific_name;
  document.getElementById("result-points").textContent     = plant.points_earned;
  document.getElementById("result-funfact").textContent    = plant.fun_fact || "A fascinating plant!";
  const pct = Math.round((plant.confidence||0)*100);
  document.getElementById("confidence-fill").style.width   = `${pct}%`;
  document.getElementById("confidence-label").textContent  = `${pct}% confident`;
  document.getElementById("first-badge").style.display     = (showFirstBadge && plant.is_first_global) ? "inline" : "none";
}

// ── Plant Chat ────────────────────────────────────────────────────────────────
async function sendPlantChat() {
  const input = document.getElementById("plant-chat-input");
  const msg = input.value.trim();
  if (!msg || !identifiedPlant) return;
  input.value = "";
  const chatBox = document.getElementById("plant-chat-messages");
  chatBox.innerHTML += `<div class="chat-msg-user"><span>${msg}</span></div>`;
  plantChatHistory.push({ role:"user", content:msg });
  const loadId = "cl-"+Date.now();
  chatBox.innerHTML += `<div id="${loadId}" class="chat-msg-bot"><span>...</span></div>`;
  chatBox.scrollTop = chatBox.scrollHeight;
  try {
    const res = await fetch("/challenge/chat", {
      method:"POST", headers:{...authHeaders(),"Content-Type":"application/json"},
      body: JSON.stringify({ message:msg, plant_name:identifiedPlant.common_name, discovery_id:identifiedPlant.discovery_id||identifiedPlant.id }),
    });
    const data = await res.json();
    document.getElementById(loadId).innerHTML = `<span>${data.response}</span>`;
    plantChatHistory.push({role:"assistant",content:data.response});
    chatBox.scrollTop = chatBox.scrollHeight;
  } catch(e) {
    document.getElementById(loadId).innerHTML = `<span>Error — try again!</span>`;
  }
}

// ── Modal Step Machine ────────────────────────────────────────────────────────
function showStep(name) {
  ["upload","loading","first-discovery","result"].forEach(s => {
    const el = document.getElementById(`step-${s}`);
    if (el) el.style.display = s===name ? "block" : "none";
  });
}

// ── Share Discovery ───────────────────────────────────────────────────────────
function shareDiscovery() {
  if (!identifiedPlant) return;
  const text = `🌱 I discovered ${identifiedPlant.common_name} (${identifiedPlant.scientific_name}) as a FIRST GLOBAL discovery on Krushi Yantra! 🎊`;
  if (navigator.share) { navigator.share({title:"Plant Discovery!",text}); }
  else { navigator.clipboard.writeText(text).then(()=>alert("Copied!")); }
}

// Leaf grow animation CSS
const leafStyle = document.createElement("style");
leafStyle.textContent = `@keyframes leafGrow{from{opacity:0;transform:scale(0.3)}to{opacity:0.92;transform:scale(1)}}`;
document.head.appendChild(leafStyle);
