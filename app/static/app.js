const state = {
  sessionId: crypto.randomUUID(),
  messages: [],
  sessions: [],
};

const $ = (id) => document.getElementById(id);

const dbp = new Promise((resolve, reject) => {
  const req = indexedDB.open("nexus-db", 1);
  req.onupgradeneeded = () => {
    const db = req.result;
    if (!db.objectStoreNames.contains("sessions")) db.createObjectStore("sessions", { keyPath: "id" });
    if (!db.objectStoreNames.contains("prefs")) db.createObjectStore("prefs", { keyPath: "key" });
  };
  req.onsuccess = () => resolve(req.result);
  req.onerror = () => reject(req.error);
});

async function idbPut(store, value) {
  const db = await dbp;
  return new Promise((res, rej) => {
    const tx = db.transaction(store, "readwrite");
    tx.objectStore(store).put(value);
    tx.oncomplete = res;
    tx.onerror = () => rej(tx.error);
  });
}

async function idbGetAll(store) {
  const db = await dbp;
  return new Promise((res, rej) => {
    const tx = db.transaction(store, "readonly");
    const req = tx.objectStore(store).getAll();
    req.onsuccess = () => res(req.result || []);
    req.onerror = () => rej(req.error);
  });
}

function renderMessages() {
  const wrap = $("messages");
  wrap.innerHTML = "";
  state.messages.forEach((m) => {
    const div = document.createElement("div");
    div.className = `msg ${m.role}`;
    div.textContent = m.content;
    wrap.appendChild(div);
  });
  wrap.scrollTop = wrap.scrollHeight;
}

async function saveLocalSession() {
  await idbPut("sessions", { id: state.sessionId, updatedAt: Date.now(), messages: state.messages });
  await loadSessions();
}

async function loadSessions() {
  state.sessions = (await idbGetAll("sessions")).sort((a, b) => b.updatedAt - a.updatedAt);
  const q = $("searchChats").value.toLowerCase();
  const list = $("sessionList");
  list.innerHTML = "";
  state.sessions
    .filter((s) => !q || JSON.stringify(s.messages).toLowerCase().includes(q))
    .forEach((s) => {
      const el = document.createElement("div");
      el.className = "session-item";
      el.textContent = s.messages?.[0]?.content?.slice(0, 48) || "New chat";
      el.onclick = () => {
        state.sessionId = s.id;
        state.messages = s.messages || [];
        renderMessages();
      };
      list.appendChild(el);
    });
}

async function send() {
  const text = $("prompt").value.trim();
  if (!text) return;
  state.messages.push({ role: "user", content: text });
  $("prompt").value = "";
  renderMessages();

  const payload = {
    session_id: state.sessionId,
    user_id: $("userId").value.trim() || null,
    model: $("modelSelect").value,
    temperature: Number($("temperature").value || 0.7),
    messages: state.messages,
  };

  const r = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await r.json();
  if (!r.ok) {
    state.messages.push({ role: "assistant", content: data.detail || "Request failed" });
  } else {
    state.sessionId = data.session_id;
    state.messages.push({ role: "assistant", content: data.output_text });
  }
  renderMessages();
  await saveLocalSession();
}

function bind() {
  $("sendBtn").onclick = send;
  $("prompt").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });
  $("newChat").onclick = () => {
    state.sessionId = crypto.randomUUID();
    state.messages = [];
    renderMessages();
  };
  $("clearBtn").onclick = () => {
    state.messages = [];
    renderMessages();
    saveLocalSession();
  };
  $("searchChats").oninput = loadSessions;
  $("exportBtn").onclick = () => {
    const blob = new Blob([JSON.stringify({ sessionId: state.sessionId, messages: state.messages }, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `nexus-${state.sessionId}.json`;
    a.click();
  };
  $("themeSelect").onchange = (e) => {
    document.documentElement.dataset.theme = e.target.value;
    idbPut("prefs", { key: "theme", value: e.target.value });
  };
}

async function boot() {
  bind();
  const prefs = await idbGetAll("prefs");
  const theme = prefs.find((p) => p.key === "theme")?.value;
  if (theme) {
    document.documentElement.dataset.theme = theme;
    $("themeSelect").value = theme;
  }
  await loadSessions();
  const health = await fetch("/api/health").then((r) => r.json());
  state.messages.push({ role: "assistant", content: `Nexus ready. Gemini: ${health.gemini}, Firebase: ${health.firebase}` });
  renderMessages();
}

boot();
