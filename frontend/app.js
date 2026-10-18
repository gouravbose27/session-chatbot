// Backend URL. Must match FRONTEND_ORIGIN CORS settings on the backend (page served on localhost:5500).
const API = "http://localhost:8000";
const SESSION_KEY = "session_id";
const UNREACHABLE_MESSAGE = "Can't reach the server. Is the backend running?";

const state = { sessionId: null, turnCount: 0, busy: false, model: null };

const chatEl = document.getElementById("chat");
const inputEl = document.getElementById("message");
const sendBtn = document.getElementById("send");
const newChatBtn = document.getElementById("new-chat");
const modelEl = document.getElementById("model");
const FALLBACK_MODEL = { id: "mistral:ministral-3b-2512", label: "Ministral 3B (lab model)" };

class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function errorText(status, data) {
  if (data && typeof data.detail === "string") {
    return data.detail;
  }
  if (status === 422) {
    return "That message could not be sent. Check its length.";
  }
  return `Server error (${status}).`;
}

async function api(method, path, body) {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(API + path, options);
  } catch {
    throw new ApiError(0, UNREACHABLE_MESSAGE);
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }
  if (!response.ok) {
    throw new ApiError(response.status, errorText(response.status, data));
  }
  return data;
}

// Per-reply metrics are kept in sessionStorage, keyed by message index, because GET /sessions does not return them.
function readMeta(sessionId) {
  try {
    return JSON.parse(sessionStorage.getItem("meta:" + sessionId)) || {};
  } catch {
    return {};
  }
}

function saveMeta(sessionId, index, meta) {
  const all = readMeta(sessionId);
  all[index] = meta;
  sessionStorage.setItem("meta:" + sessionId, JSON.stringify(all));
}

function metaFrom(data) {
  return {
    inputTokens: data.input_tokens,
    outputTokens: data.output_tokens,
    seconds: data.seconds,
    cost: data.cost,
    guardrail: data.guardrail,
  };
}

function formatMetrics(meta) {
  const cost = meta.cost === null ? "cost n/a" : "$" + meta.cost.toFixed(6);
  return `${meta.inputTokens} in / ${meta.outputTokens} out · ${meta.seconds.toFixed(1)} s · ${cost}`;
}

function scrollToEnd() {
  chatEl.scrollTop = chatEl.scrollHeight;
}

function addNote(text, kind) {
  const note = document.createElement("p");
  note.className = "note " + kind;
  note.textContent = text;
  chatEl.append(note);
  scrollToEnd();
}

function addMessage(role, text, meta) {
  const wrap = document.createElement("div");
  wrap.className = "message " + role;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrap.append(bubble);

  if (meta) {
    const metrics = document.createElement("p");
    metrics.className = "metrics";
    metrics.textContent = formatMetrics(meta);
    wrap.append(metrics);

    if (meta.guardrail) {
      const guardrail = document.createElement("p");
      guardrail.className = "guardrail";
      guardrail.textContent = "Guardrail: " + meta.guardrail;
      wrap.append(guardrail);
    }
  }

  chatEl.append(wrap);
  scrollToEnd();
}

function addThinking() {
  const el = document.createElement("p");
  el.className = "thinking";
  el.textContent = "thinking…";
  chatEl.append(el);
  scrollToEnd();
  return el;
}

function resetChat() {
  chatEl.replaceChildren();
}

function setBusy(busy) {
  state.busy = busy;
  inputEl.disabled = busy;
  sendBtn.disabled = busy;
  newChatBtn.disabled = busy;
  modelEl.disabled = busy;
}

async function createSession() {
  const data = await api("POST", "/sessions");
  state.sessionId = data.session_id;
  state.turnCount = 0;
  sessionStorage.setItem(SESSION_KEY, data.session_id);
}

async function loadSession(sessionId) {
  const data = await api("GET", "/sessions/" + encodeURIComponent(sessionId));
  state.sessionId = sessionId;
  state.turnCount = Math.floor(data.messages.length / 2);
  resetChat();
  const meta = readMeta(sessionId);
  data.messages.forEach((msg, index) => {
    addMessage(msg.role, msg.content, msg.role === "assistant" ? meta[index] : null);
  });
}

function fillModels(providers, defaultId) {
  modelEl.replaceChildren();
  for (const group of providers) {
    const optgroup = document.createElement("optgroup");
    optgroup.label = group.provider;
    for (const model of group.models) {
      optgroup.append(new Option(model.label, model.id));
    }
    modelEl.append(optgroup);
  }
  modelEl.value = defaultId;
  // An empty value means the backend uses its default model.
  state.model = modelEl.value || null;
}

async function loadModels() {
  try {
    const data = await api("GET", "/models");
    fillModels(data.providers, data.default);
  } catch {
    // The session start below shows the connection error, so only the fallback is set here.
    fillModels([{ provider: "Mistral", models: [FALLBACK_MODEL] }], FALLBACK_MODEL.id);
  }
}

async function start() {
  await loadModels();
  const saved = sessionStorage.getItem(SESSION_KEY);
  if (saved) {
    try {
      await loadSession(saved);
      return;
    } catch (error) {
      if (error.status !== 404) {
        // Keep the saved id so the next send retries it.
        state.sessionId = saved;
        addNote(error.message, "error");
        return;
      }
      addNote("The server was restarted, so a new chat was started.", "info");
    }
  }
  try {
    await createSession();
  } catch (error) {
    addNote(error.message, "error");
  }
}

async function ensureSession() {
  if (!state.sessionId) {
    await createSession();
  }
}

function postChat(text) {
  return api("POST", "/chat", { session_id: state.sessionId, message: text, model: state.model });
}

async function chatWithRecovery(text) {
  try {
    return await postChat(text);
  } catch (error) {
    if (error.status !== 404) {
      throw error;
    }
    await createSession();
    addNote("The server was restarted, so a new chat was started. Sending your message again.", "info");
    return postChat(text);
  }
}

function recordReply(data) {
  const meta = metaFrom(data);
  addMessage("assistant", data.reply, meta);
  // Blocked replies are not saved, so the turn count does not grow and no metrics are stored for them.
  if (data.turns_in_memory > state.turnCount) {
    saveMeta(state.sessionId, 2 * data.turns_in_memory - 1, meta);
    state.turnCount = data.turns_in_memory;
  }
}

async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || state.busy) {
    return;
  }

  setBusy(true);
  inputEl.value = "";
  addMessage("user", text, null);
  const thinking = addThinking();

  try {
    await ensureSession();
    const data = await chatWithRecovery(text);
    thinking.remove();
    recordReply(data);
  } catch (error) {
    thinking.remove();
    addNote(error.message, "error");
    if (!inputEl.value) {
      inputEl.value = text;
    }
  } finally {
    setBusy(false);
    inputEl.focus();
  }
}

async function newChat() {
  if (state.busy) {
    return;
  }

  setBusy(true);
  const oldId = state.sessionId;
  resetChat();
  try {
    if (oldId) {
      try {
        await api("DELETE", "/sessions/" + encodeURIComponent(oldId));
      } catch (error) {
        if (error.status !== 404) {
          addNote(error.message, "error");
        }
      }
      sessionStorage.removeItem("meta:" + oldId);
    }
    state.sessionId = null;
    sessionStorage.removeItem(SESSION_KEY);
    await createSession();
  } catch (error) {
    addNote(error.message, "error");
  } finally {
    setBusy(false);
    inputEl.focus();
  }
}

inputEl.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    sendMessage();
  }
});
sendBtn.addEventListener("click", sendMessage);
newChatBtn.addEventListener("click", newChat);
modelEl.addEventListener("change", () => {
  state.model = modelEl.value || null;
});

start();
