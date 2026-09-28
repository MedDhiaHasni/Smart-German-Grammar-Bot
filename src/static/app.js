/* ─────────────────────────────────────────────────────────
   Der Tutor — frontend logic
   Handles: session mgmt, sending messages, streaming SSE tokens.
   ───────────────────────────────────────────────────────── */

const API = "";  // same origin

const els = {
  messages:      document.getElementById("messages"),
  input:         document.getElementById("input"),
  composer:      document.getElementById("composer"),
  sendBtn:       document.getElementById("send-btn"),
  sessionId:     document.getElementById("session-id"),
  statusLabel:   document.getElementById("status-label"),
  statusDot:     document.getElementById("status-dot"),
  modeLabel:     document.getElementById("current-mode-label"),
  modeBtns:      document.querySelectorAll(".mode-btn"),
  newChatBtn:    document.getElementById("new-chat-btn"),
};

let state = {
  sessionId: null,
  mode: "general",
  streaming: false,
};

/* ─── Utilities ──────────────────────────────────────── */

function setStatus(text, kind /* "online" | "streaming" | "error" */) {
  els.statusLabel.textContent = text;
  els.statusDot.className = "dot" + (kind ? " " + kind : "");
}

function shortId(id) { return id ? id.slice(0, 8) : "—"; }

function escapeHtml(s) {
  return s
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

/* Very small markdown-ish renderer: bold + inline code. */
function renderText(raw) {
  let s = escapeHtml(raw);
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
  return s;
}

function appendMessage(role, html, opts = {}) {
  const wrap = document.createElement("div");
  wrap.className = `msg msg-${role}`;
  if (opts.error) wrap.classList.add("msg-error");

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.innerHTML = html;
  wrap.appendChild(bubble);
  els.messages.appendChild(wrap);
  els.messages.scrollTop = els.messages.scrollHeight;
  return bubble;
}

/* ─── Session management ─────────────────────────────── */

async function createSession() {
  try {
    const r = await fetch(`${API}/session/new`, { method: "POST" });
    const j = await r.json();
    state.sessionId = j.session_id;
    state.mode = j.mode;
    els.sessionId.textContent = shortId(j.session_id);
  } catch (e) {
    setStatus("Offline — could not reach server", "error");
    console.error(e);
  }
}

/* ─── Mode switching ─────────────────────────────────── */

function bindModeButtons() {
  els.modeBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      if (state.streaming) return;

      els.modeBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      state.mode = btn.dataset.mode;
      els.modeLabel.textContent = btn.textContent.trim();

      appendMessage(
        "assistant",
        `<p>Mode switched to <strong>${btn.textContent.trim()}</strong>. Ready when you are.</p>`
      );
    });
  });
}

/* ─── Streaming send ─────────────────────────────────── */

async function sendMessage(text) {
  if (!text.trim() || state.streaming) return;
  if (!state.sessionId) await createSession();

  appendMessage("user", renderText(text));
  els.input.value = "";
  els.input.style.height = "auto";

  const bubble = appendMessage("assistant", "");
  bubble.classList.add("cursor");
  state.streaming = true;
  els.sendBtn.disabled = true;
  setStatus("Der Tutor is thinking…", "streaming");

  const accumulated = { value: "" };

  try {
    const res = await fetch(`${API}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: state.sessionId,
        message: text,
        mode: state.mode,
      }),
    });

    if (!res.ok || !res.body) {
      throw new Error(`HTTP ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const frames = buffer.split("\n\n");
      buffer = frames.pop();

      for (const frame of frames) {
        handleSseFrame(frame, bubble, accumulated, (chunk) => {
          accumulated.value += chunk;
        });
      }
    }

    bubble.classList.remove("cursor");
    bubble.innerHTML =
      renderText(accumulated.value) || "<p><em>(empty reply)</em></p>";
    setStatus("Online", "online");
  } catch (err) {
    console.error(err);
    bubble.classList.remove("cursor");
    bubble.parentElement.classList.add("msg-error");
    bubble.innerHTML = `<p><strong>Error:</strong> ${escapeHtml(err.message)}</p>`;
    setStatus("Error", "error");
  } finally {
    state.streaming = false;
    els.sendBtn.disabled = false;
    els.messages.scrollTop = els.messages.scrollHeight;
  }
}

function handleSseFrame(frame, bubble, accumulated, onChunk) {
  // A frame may have multiple "event:"/"data:" lines. We only care about data.
  const lines = frame.split("\n");
  let event = "message";
  const dataParts = [];

  for (const line of lines) {
    if (line.startsWith("event:"))  event = line.slice(6).trim();
    if (line.startsWith("data:"))   dataParts.push(line.slice(5).trimStart());
  }

  const data = dataParts.join("\n");

  if (event === "done") return;
  if (event === "error") {
    throw new Error(data || "stream error");
  }

  if (data) {
    onChunk(data);
    // Render the *accumulated* text so we never lose earlier tokens.
    bubble.innerHTML = renderText(accumulated.value);
  }
}

/* ─── Input handling ─────────────────────────────────── */

function bindComposer() {
  els.composer.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(els.input.value);
  });

  els.input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(els.input.value);
    }
  });

  // Auto-grow textarea
  els.input.addEventListener("input", () => {
    els.input.style.height = "auto";
    els.input.style.height = Math.min(els.input.scrollHeight, 160) + "px";
  });
}

/* ─── New chat ───────────────────────────────────────── */

function bindNewChat() {
  els.newChatBtn.addEventListener("click", async () => {
    if (state.streaming) return;
    if (state.sessionId) {
      fetch(`${API}/session/${state.sessionId}`, { method: "DELETE" }).catch(() => {});
    }
    els.messages.innerHTML = "";
    appendMessage(
      "assistant",
      `<p>New session started. What would you like to practice? 🎓</p>`
    );
    await createSession();
  });
}

/* ─── Boot ───────────────────────────────────────────── */

(async function init() {
  bindComposer();
  bindModeButtons();
  bindNewChat();
  await createSession();
  setStatus("Online", "online");
})();