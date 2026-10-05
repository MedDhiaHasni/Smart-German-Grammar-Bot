/* ─────────────────────────────────────────────────────────
   Der Tutor — frontend logic
   Handles: session mgmt, sending messages, streaming SSE tokens,
   welcome hero + suggestion cards.
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

// Saved copy of the welcome hero so "New Chat" can restore it.
const welcomeEl = document.getElementById("welcome");
const heroHTML = welcomeEl ? welcomeEl.outerHTML : "";

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

/* Small markdown-ish renderer: bold + inline code + colored articles. */
function renderText(raw, colorArticles = true) {
  let s = escapeHtml(raw);
  s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
  if (colorArticles) {
    s = s.replace(
      /\b(der|die|das)\b/gi,
      (m) => `<span class="art art-${m.toLowerCase()}">${m}</span>`
    );
  }
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

  appendMessage("user", renderText(text, false));
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
  let data = null;

  for (const line of lines) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data = line.slice(5);
  }

  if (event === "done") return;

  // The server sends every payload JSON-encoded, so spaces are preserved.
  let payload = "";
  if (data !== null) {
    try {
      payload = JSON.parse(data);
    } catch {
      // Fallback: remove only the single SSE separator space
      payload = data.replace(/^ /, "");
    }
  }

  if (event === "error") {
    throw new Error(payload || "stream error");
  }

  if (payload) {
    onChunk(payload);
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

/* ─── Suggestion cards (welcome hero) ────────────────── */

function bindSuggestions() {
  // Event delegation, so it keeps working after the hero is restored.
  els.messages.addEventListener("click", (e) => {
    const card = e.target.closest(".suggest");
    if (card) sendMessage(card.dataset.prompt);
  });
}

/* ─── New chat ───────────────────────────────────────── */

function bindNewChat() {
  els.newChatBtn.addEventListener("click", async () => {
    if (state.streaming) return;
    if (state.sessionId) {
      fetch(`${API}/session/${state.sessionId}`, { method: "DELETE" }).catch(() => {});
    }
    // Bring the welcome hero back instead of a plain message.
    els.messages.innerHTML = heroHTML;
    els.messages.scrollTop = 0;
    await createSession();
  });
}

/* ─── Boot ───────────────────────────────────────────── */

(async function init() {
  bindComposer();
  bindModeButtons();
  bindSuggestions();
  bindNewChat();
  await createSession();
  setStatus("Online", "online");
})();