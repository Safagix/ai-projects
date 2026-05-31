/* ══════════════════════════════════════════════════════════
   Eira Brain Chat — Application Logic
   ══════════════════════════════════════════════════════════ */

(() => {
  "use strict";

  // ── State ──────────────────────────────────────────────
  const state = {
    mode: "query",          // "query" | "write" | "collector"
    sessionId: "default",
    isStreaming: false,
    sessions: [],            // [{id, title, timestamp}]
  };

  // ── DOM Refs ───────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const el = {
    messages:        $("#messages"),
    welcome:         $("#welcome"),
    userInput:       $("#userInput"),
    sendBtn:         $("#sendBtn"),
    menuBtn:         $("#menuBtn"),
    sidebar:         $("#sidebar"),
    newChatBtn:      $("#newChatBtn"),
    sessionList:     $("#sessionList"),
    modelBadge:      $("#modelBadge"),
    currentModel:    $("#currentModel"),
    modeQuery:       $("#modeQuery"),
    modeWrite:       $("#modeWrite"),
    modeCollector:   $("#modeCollector"),
    inputArea:       $("#inputArea"),
    collectorPanel:  $("#collectorPanel"),
    collectorName:   $("#collectorName"),
    collectorDesc:   $("#collectorDesc"),
    collectorCode:   $("#collectorCode"),
    collectorSubmit: $("#collectorSubmit"),
    collectorFeedback: $("#collectorFeedback"),
    writePanel:      $("#writePanel"),
    writeTitle:      $("#writeTitle"),
    writeContent:    $("#writeContent"),
    writeSubmit:     $("#writeSubmit"),
    writeFeedback:   $("#writeFeedback"),
    inputContainer:  $(".input-container"),
    inputModeInd:    $("#inputModeIndicator"),
    ollamaStatus:    $("#ollamaStatus"),
    reindexBtn:      $("#reindexBtn"),
  };

  // ── Init ───────────────────────────────────────────────
  function init() {
    loadSessions();
    bindEvents();
    checkHealth();
    renderStoredMessages();
    autoResize(el.userInput);
  }

  // ── Events ─────────────────────────────────────────────
  function bindEvents() {
    el.sendBtn.addEventListener("click", sendMessage);

    el.userInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    el.userInput.addEventListener("input", () => autoResize(el.userInput));

    el.menuBtn.addEventListener("click", toggleSidebar);
    el.newChatBtn.addEventListener("click", newSession);

    el.modeQuery.addEventListener("click", () => setMode("query"));
    el.modeWrite.addEventListener("click", () => setMode("write"));
    el.modeCollector.addEventListener("click", () => setMode("collector"));

    el.reindexBtn.addEventListener("click", reindex);
    el.collectorSubmit.addEventListener("click", submitCollector);
    el.writeSubmit.addEventListener("click", submitWrite);

    // Welcome chips
    document.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        el.userInput.value = chip.dataset.query;
        autoResize(el.userInput);
        sendMessage();
      });
    });
  }

  // ── Mode Toggle ────────────────────────────────────────
  function setMode(mode) {
    state.mode = mode;
    el.modeQuery.classList.toggle("active", mode === "query");
    el.modeWrite.classList.toggle("active", mode === "write");
    el.modeCollector.classList.toggle("active", mode === "collector");
    el.inputContainer.classList.toggle("write-mode", mode === "write");
    el.inputContainer.classList.toggle("collector-mode", mode === "collector");

    // Hide all containers to prevent overlap
    el.messages.style.display = "none";
    el.inputArea.style.display = "none";
    el.collectorPanel.classList.add("hidden");
    el.writePanel.classList.add("hidden");

    if (mode === "collector") {
      el.collectorPanel.classList.remove("hidden");
      el.inputModeInd.innerHTML =
        '<span class="mode-icon">🧩</span><span class="mode-text">UI/UX Collector — Clasificar y guardar componentes</span>';
      el.collectorName.focus();
    } else if (mode === "write") {
      el.writePanel.classList.remove("hidden");
      el.inputModeInd.innerHTML =
        '<span class="mode-icon">✏️</span><span class="mode-text">Agregar información a Obsidian (07-Ideas)</span>';
      el.writeTitle.focus();
    } else { // "query"
      el.messages.style.display = "";
      el.inputArea.style.display = "";

      // Re-trigger welcome screen check if history is empty
      const messages = loadStoredMessages();
      if (messages.length === 0) {
        renderWelcome();
      } else {
        hideWelcome();
      }

      el.inputModeInd.innerHTML =
        '<span class="mode-icon">🔍</span><span class="mode-text">Buscar en tu base de conocimiento</span>';
      el.userInput.placeholder = "Pregunta algo sobre tu base de conocimiento...";
      el.userInput.focus();
    }
  }

  // ── Collector Submit ───────────────────────────────────
  async function submitCollector() {
    const name = el.collectorName.value.trim();
    const description = el.collectorDesc.value.trim();
    const code = el.collectorCode.value.trim();

    if (!name) {
      showCollectorFeedback("Por favor ingresa un nombre para el componente.", "warning");
      el.collectorName.focus();
      return;
    }
    if (!code) {
      showCollectorFeedback("Por favor pega el código del componente.", "warning");
      el.collectorCode.focus();
      return;
    }

    el.collectorSubmit.disabled = true;
    el.collectorSubmit.classList.add("loading");
    el.collectorSubmit.textContent = "Clasificando...";

    try {
      const resp = await fetch("/api/uiux-collect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description, code }),
      });

      const data = await resp.json();

      if (data.status === "duplicate") {
        showCollectorFeedback(
          `⚠️ Ya existe: "${data.existing_name}". `,
          "warning"
        );
        const forceBtn = document.createElement("button");
        forceBtn.className = "collector-force-btn";
        forceBtn.textContent = "Guardar de todos modos";
        forceBtn.addEventListener("click", () => forceSaveCollector(name, description, code));
        el.collectorFeedback.appendChild(forceBtn);
      } else if (data.status === "saved") {
        showCollectorFeedback(
          `✅ Guardado: "${data.component.name}" · ${data.component.category} · ${data.component.quality_score}/10 · ${data.catalog_count} en catálogo`,
          "success"
        );
        el.collectorName.value = "";
        el.collectorDesc.value = "";
        el.collectorCode.value = "";
        el.collectorName.focus();
      } else if (data.status === "saved_with_warning") {
        showCollectorFeedback(
          `⚠️ Guardado con advertencia: ${data.warning || ""} · Catálogo: ${data.catalog_count} componentes`,
          "warning"
        );
        el.collectorName.value = "";
        el.collectorDesc.value = "";
        el.collectorCode.value = "";
        el.collectorName.focus();
      } else {
        showCollectorFeedback(
          `❌ Error: ${data.message || "Error desconocido"}`,
          "error"
        );
      }
    } catch (err) {
      showCollectorFeedback(`❌ Error de conexión: ${err.message}`, "error");
    }

    el.collectorSubmit.disabled = false;
    el.collectorSubmit.classList.remove("loading");
    el.collectorSubmit.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M2 9l14-7-4 7 4 7-14-7z" fill="currentColor"/>
      </svg>
      Clasificar y Guardar`;
  }

  async function forceSaveCollector(name, description, code) {
    el.collectorSubmit.disabled = true;
    el.collectorSubmit.classList.add("loading");
    el.collectorSubmit.textContent = "Forzando guardado...";

    try {
      const resp = await fetch("/api/uiux-collect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description, code, force: true }),
      });
      const data = await resp.json();

      if (data.status === "saved" || data.status === "saved_with_warning") {
        showCollectorFeedback(
          `✅ Guardado: "${data.component.name}" · ${data.component.category} · ${data.component.quality_score}/10 · ${data.catalog_count} en catálogo`,
          "success"
        );
        el.collectorName.value = "";
        el.collectorDesc.value = "";
        el.collectorCode.value = "";
        el.collectorName.focus();
      } else {
        showCollectorFeedback(
          `❌ Error: ${data.message || "Error desconocido"}`,
          "error"
        );
      }
    } catch (err) {
      showCollectorFeedback(`❌ Error de conexión: ${err.message}`, "error");
    }

    el.collectorSubmit.disabled = false;
    el.collectorSubmit.classList.remove("loading");
    el.collectorSubmit.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M2 9l14-7-4 7 4 7-14-7z" fill="currentColor"/>
      </svg>
      Clasificar y Guardar`;
  }

  function showCollectorFeedback(message, type) {
    el.collectorFeedback.classList.remove("hidden", "success", "warning", "error");
    el.collectorFeedback.classList.add(type);
    el.collectorFeedback.textContent = "";
    el.collectorFeedback.appendChild(document.createTextNode(message));
  }

  // ── Write Submit ───────────────────────────────────────
  async function submitWrite() {
    const title = el.writeTitle.value.trim();
    const content = el.writeContent.value.trim();

    if (!content) {
      showWriteFeedback("Por favor escribe el contenido de la nota.", "error");
      el.writeContent.focus();
      return;
    }

    el.writeSubmit.disabled = true;
    el.writeSubmit.classList.add("loading");
    el.writeSubmit.textContent = "Guardando...";

    try {
      const resp = await fetch("/api/write", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content }),
      });
      const data = await resp.json();

      if (data.filename) {
        showWriteFeedback(
          `✅ Guardado con éxito: "${data.filename}" en "${data.folder}"`,
          "success"
        );
        el.writeTitle.value = "";
        el.writeContent.value = "";
      } else {
        showWriteFeedback(
          `❌ Error: ${data.message || "Error desconocido"}`,
          "error"
        );
      }
    } catch (err) {
      showWriteFeedback(`❌ Error de conexión: ${err.message}`, "error");
    }

    el.writeSubmit.disabled = false;
    el.writeSubmit.classList.remove("loading");
    el.writeSubmit.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z" fill="currentColor"/>
        <path d="M8 4v8M4 8h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      Guardar en Obsidian`;
  }

  function showWriteFeedback(message, type) {
    el.writeFeedback.classList.remove("hidden", "success", "error");
    el.writeFeedback.classList.add(type);
    el.writeFeedback.textContent = message;
  }

  // ── Send Message ───────────────────────────────────────
  async function sendMessage() {
    const text = el.userInput.value.trim();
    if (!text || state.isStreaming) return;

    hideWelcome();
    appendMessage("user", text);
    addStoredMessage({ role: "user", content: text });

    el.userInput.value = "";
    autoResize(el.userInput);
    state.isStreaming = true;
    el.sendBtn.disabled = true;

    // Create assistant message placeholder
    const assistantMsg = appendMessage("assistant", "", { streaming: true });
    const bodyEl = assistantMsg.querySelector(".message-body");

    // Determine if we force write mode. Search wording must keep retrieval
    // active even if the UI was accidentally left in "Agregar".
    const payload = { message: text, session_id: state.sessionId };
    if (state.mode === "write" && !looksLikeSearchRequest(text)) {
      payload.message = `[GUARDAR EN OBSIDIAN] ${text}`;
    }

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let fullText = "";
      let citations = [];
      let modelName = "";
      let category = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = parseSSE(buffer);
        buffer = events.remaining;

        for (const evt of events.parsed) {
          switch (evt.event) {
            case "routing":
              modelName = evt.data.model || "";
              category = evt.data.category || "";
              setModelBadge(modelName, true);
              break;

            case "status":
              showStatus(evt.data.message);
              break;

            case "chunk":
              fullText += evt.data.text;
              bodyEl.innerHTML = renderMarkdown(fullText);
              scrollToBottom();
              break;

            case "error":
              throw new Error(evt.data.message || "Error desconocido del servidor");

            case "audio":
              if (window.playAvatarAudio) {
                window.playAvatarAudio(evt.data.url);
              }
              break;

            case "done":
              citations = evt.data.citations || [];
              modelName = evt.data.model || modelName;
              category = evt.data.category || category;
              break;
          }
        }
      }

      // Finalize
      removeStatus();
      removeTypingIndicator(assistantMsg);
      bodyEl.innerHTML = renderMarkdown(fullText);

      // Add model tag
      const headerEl = assistantMsg.querySelector(".message-header");
      if (modelName) {
        const tag = document.createElement("span");
        tag.className = "message-model-tag";
        tag.textContent = modelName;
        headerEl.appendChild(tag);
      }

      // Add citations
      if (citations.length > 0) {
        const citDiv = document.createElement("div");
        citDiv.className = "citations";
        citDiv.innerHTML = `<div class="citations-label">📚 Fuentes</div>`;
        citations.forEach((c) => {
          const filename = c.path.split(/[/\\]/).pop();
          const ci = document.createElement("span");
          ci.className = "citation-item";
          ci.innerHTML = `📄 ${filename} · <em>${c.heading || "Documento"}</em> <span class="citation-score">${c.score}</span>`;
          ci.title = c.path;
          citDiv.appendChild(ci);
        });
        assistantMsg.appendChild(citDiv);
      }

      addStoredMessage({
        role: "assistant",
        content: fullText,
        model: modelName,
        citations,
      });

      // Update session
      updateSessionTitle(text);
      setModelBadge("Listo", false);

    } catch (err) {
      bodyEl.innerHTML = `<p style="color:var(--accent-rose)">❌ Error: ${err.message}</p>`;
      removeStatus();
      setModelBadge("Error", false);
    }

    state.isStreaming = false;
    el.sendBtn.disabled = false;
    scrollToBottom();
    el.userInput.focus();
  }

  function normalizeText(text) {
    return text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  function looksLikeSearchRequest(text) {
    const normalized = normalizeText(text);
    const markerHit = [
      "busca",
      "buscar",
      "buscame",
      "base de datos",
      "biblioteca",
      "obsidian",
      "fuente",
      "fuentes",
      "que sabes",
      "explica",
      "explicame",
      "resume",
      "resumen",
    ].some((marker) => normalized.includes(marker));

    if (markerHit) return true;

    const domainHits = [
      "template",
      "templates",
      "workflow",
      "workflows",
      "n8n",
      "whatsapp",
      "telegram",
      "google sheets",
      "gmail",
      "slack",
      "webhook",
      "automatizacion",
      "integracion",
    ].filter((term) => normalized.includes(term)).length;

    return domainHits >= 2;
  }

  // ── SSE Parser ─────────────────────────────────────────
  function parseSSE(raw) {
    const parsed = [];
    const normalized = raw.replace(/\r\n/g, "\n");
    const blocks = normalized.split("\n\n");
    const remaining = blocks.pop() || "";

    for (const block of blocks) {
      let currentEvent = "message";
      const dataLines = [];

      for (const line of block.split("\n")) {
        if (line.startsWith("event: ")) {
          currentEvent = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          dataLines.push(line.slice(6));
        }
      }

      if (!dataLines.length) {
        continue;
      }

      try {
        const data = JSON.parse(dataLines.join("\n"));
        parsed.push({ event: currentEvent, data });
      } catch { /* skip malformed */ }
    }

    return { parsed, remaining };
  }

  // ── DOM Helpers ────────────────────────────────────────
  function appendMessage(role, content, opts = {}) {
    const div = document.createElement("div");
    div.className = `message ${role}`;

    const avatar = role === "user" ? "👤" : "🧠";
    const sender = role === "user" ? "Tú" : "Eira Brain";

    div.innerHTML = `
      <div class="message-header">
        <div class="message-avatar">${avatar}</div>
        <span class="message-sender">${sender}</span>
      </div>
      <div class="message-body">${content ? renderMarkdown(content) : ""}</div>
    `;

    if (opts.streaming && !content) {
      const typing = document.createElement("div");
      typing.className = "typing-indicator";
      typing.innerHTML = "<span></span><span></span><span></span>";
      div.querySelector(".message-body").appendChild(typing);
    }

    el.messages.appendChild(div);
    scrollToBottom();
    return div;
  }

  function removeTypingIndicator(msgEl) {
    const ti = msgEl.querySelector(".typing-indicator");
    if (ti) ti.remove();
  }

  function showStatus(text) {
    removeStatus();
    const div = document.createElement("div");
    div.className = "status-msg";
    div.id = "currentStatus";
    div.innerHTML = `<span class="status-dot"></span>${text}`;
    el.messages.appendChild(div);
    scrollToBottom();
  }

  function removeStatus() {
    const existing = document.getElementById("currentStatus");
    if (existing) existing.remove();
  }

  function hideWelcome() {
    if (el.welcome) {
      el.welcome.style.display = "none";
    }
  }

  function scrollToBottom() {
    el.messages.scrollTop = el.messages.scrollHeight;
  }

  function autoResize(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
  }

  // ── Model Badge ────────────────────────────────────────
  function setModelBadge(name, active) {
    el.currentModel.textContent = name;
    el.modelBadge.classList.toggle("active", active);
  }

  // ── Sidebar ────────────────────────────────────────────
  function toggleSidebar() {
    el.sidebar.classList.toggle("hidden");
    el.sidebar.classList.toggle("visible");
  }

  // ── Sessions ───────────────────────────────────────────
  function loadSessions() {
    try {
      state.sessions = JSON.parse(localStorage.getItem("eira_sessions") || "[]");
    } catch { state.sessions = []; }

    if (state.sessions.length === 0) {
      newSession(false);
    } else {
      state.sessionId = state.sessions[0].id;
    }
    renderSessions();
  }

  function saveSessions() {
    localStorage.setItem("eira_sessions", JSON.stringify(state.sessions));
  }

  function messagesKey(sessionId = state.sessionId) {
    return `eira_messages_${sessionId}`;
  }

  function loadStoredMessages(sessionId = state.sessionId) {
    try {
      const messages = JSON.parse(localStorage.getItem(messagesKey(sessionId)) || "[]");
      return Array.isArray(messages) ? messages : [];
    } catch {
      return [];
    }
  }

  function saveStoredMessages(messages, sessionId = state.sessionId) {
    localStorage.setItem(messagesKey(sessionId), JSON.stringify(messages.slice(-80)));
  }

  let _messageBuffer = null;
  let _flushTimer = null;

  function _flushMessages() {
    if (_messageBuffer) {
      saveStoredMessages(_messageBuffer);
      _messageBuffer = null;
    }
    if (_flushTimer) {
      clearTimeout(_flushTimer);
      _flushTimer = null;
    }
  }

  window.addEventListener("beforeunload", _flushMessages);
  window.addEventListener("pagehide", _flushMessages);

  function addStoredMessage(message) {
    if (_messageBuffer === null) {
      _messageBuffer = loadStoredMessages();
    }
    _messageBuffer.push({ ...message, timestamp: Date.now() });
    if (_flushTimer) clearTimeout(_flushTimer);
    _flushTimer = setTimeout(_flushMessages, 5000);
  }

  function renderStoredMessages() {
    const messages = loadStoredMessages();
    el.messages.innerHTML = "";

    if (messages.length === 0) {
      renderWelcome();
      return;
    }

    messages.forEach((message) => {
      const msgEl = appendMessage(message.role, message.content || "");
      if (message.role === "assistant") {
        const headerEl = msgEl.querySelector(".message-header");
        if (message.model) {
          const tag = document.createElement("span");
          tag.className = "message-model-tag";
          tag.textContent = message.model;
          headerEl.appendChild(tag);
        }
        appendCitations(msgEl, message.citations || []);
      }
    });
  }

  function newSession(render = true) {
    const id = "s_" + Date.now();
    state.sessions.unshift({
      id,
      title: "Nueva conversación",
      timestamp: Date.now(),
    });
    state.sessionId = id;
    saveSessions();

    saveStoredMessages([]);
    renderWelcome();

    if (render) renderSessions();
  }

  function renderWelcome() {
    el.messages.innerHTML = `
        <div class="welcome" id="welcome">
          <div class="welcome-icon">
            <svg viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="28" stroke="url(#wg2)" stroke-width="2" opacity="0.5"/>
              <circle cx="32" cy="32" r="18" stroke="url(#wg2)" stroke-width="1.5" opacity="0.3"/>
              <circle cx="32" cy="32" r="8" fill="url(#wg2)" opacity="0.6"/>
              <defs><linearGradient id="wg2" x1="0" y1="0" x2="64" y2="64">
                <stop offset="0%" stop-color="#00f2fe"/>
                <stop offset="100%" stop-color="#9b51e0"/>
              </linearGradient></defs>
            </svg>
          </div>
          <h1 class="welcome-title">Eira Brain</h1>
          <p class="welcome-sub">Tu base de conocimiento personal con IA</p>
          <div class="welcome-chips">
            <button class="chip" data-query="¿Qué herramientas de IA gratuitas tengo documentadas?">🔍 Herramientas IA gratuitas</button>
            <button class="chip" data-query="¿Cuál es mi roadmap como AI Engineer?">🗺️ Mi roadmap</button>
            <button class="chip" data-query="Resume mis notas sobre automatización">⚡ Automatización</button>
            <button class="chip" data-query="¿Qué proyectos tengo documentados?">📁 Mis proyectos</button>
          </div>
        </div>`;
    el.welcome = $("#welcome");

    document.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        el.userInput.value = chip.dataset.query;
        autoResize(el.userInput);
        sendMessage();
      });
    });
  }

  function updateSessionTitle(firstMessage) {
    const session = state.sessions.find((s) => s.id === state.sessionId);
    if (session && session.title === "Nueva conversación") {
      session.title = firstMessage.slice(0, 50) + (firstMessage.length > 50 ? "…" : "");
      saveSessions();
      renderSessions();
    }
  }

  function renderSessions() {
    el.sessionList.innerHTML = state.sessions.map((s) => `
      <div class="session-item ${s.id === state.sessionId ? "active" : ""}" data-id="${s.id}">
        <span class="session-icon">💬</span>
        <span class="session-title">${escapeHtml(s.title)}</span>
      </div>
    `).join("");

    el.sessionList.querySelectorAll(".session-item").forEach((item) => {
      item.addEventListener("click", () => {
        state.sessionId = item.dataset.id;
        renderSessions();
        renderStoredMessages();
      });
    });
  }

  function appendCitations(messageEl, citations) {
    if (!citations.length) return;

    const citDiv = document.createElement("div");
    citDiv.className = "citations";
    citDiv.innerHTML = `<div class="citations-label">📚 Fuentes</div>`;
    citations.forEach((c) => {
      const filename = c.path.split(/[/\\]/).pop();
      const ci = document.createElement("span");
      ci.className = "citation-item";
      ci.innerHTML = `📄 ${filename} · <em>${c.heading || "Documento"}</em> <span class="citation-score">${c.score}</span>`;
      ci.title = c.path;
      citDiv.appendChild(ci);
    });
    messageEl.appendChild(citDiv);
  }

  // ── Health Check ───────────────────────────────────────
  async function checkHealth() {
    try {
      const resp = await fetch("/api/health");
      const data = await resp.json();
      if (data.status === "ok") {
        const models = data.ollama?.models || [];
        el.ollamaStatus.textContent = `✅ ${models.length} modelos`;
        el.ollamaStatus.title = models.join(", ");
      } else {
        el.ollamaStatus.textContent = "⚠️ Sin conexión";
      }
    } catch {
      el.ollamaStatus.textContent = "❌ Offline";
    }
  }

  // ── Reindex ────────────────────────────────────────────
  async function reindex() {
    el.reindexBtn.classList.add("loading");
    el.reindexBtn.textContent = "Indexando...";
    try {
      const resp = await fetch("/api/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paths: [] }),
      });
      const data = await resp.json();
      el.reindexBtn.innerHTML = `✅ ${data.documents} docs, ${data.chunks} chunks`;
      setTimeout(() => {
        el.reindexBtn.innerHTML = `
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M1 8a7 7 0 0113.06-3.5M15 8a7 7 0 01-13.06 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M14 1v3.5h-3.5M2 15v-3.5h3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Re-indexar`;
      }, 3000);
    } catch (err) {
      el.reindexBtn.textContent = "❌ Error";
    }
    el.reindexBtn.classList.remove("loading");
  }

  // ── Markdown Renderer (lightweight) ────────────────────
  function renderMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);

    // Code blocks (``` ... ```)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
      return `<pre><code class="lang-${lang}">${code.trim()}</code></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    // Italic
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Headers
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

    // Blockquotes
    html = html.replace(/^&gt; (.+)$/gm, "<blockquote>$1</blockquote>");

    // Unordered lists
    html = html.replace(/^[-*] (.+)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>\n?)+/g, "<ul>$&</ul>");

    // Ordered lists
    html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

    // Line breaks → paragraphs
    html = html.replace(/\n\n/g, "</p><p>");
    html = html.replace(/\n/g, "<br>");
    html = `<p>${html}</p>`;

    // Clean up
    html = html.replace(/<p><\/p>/g, "");
    html = html.replace(/<p>(<h[123]>)/g, "$1");
    html = html.replace(/(<\/h[123]>)<\/p>/g, "$1");
    html = html.replace(/<p>(<pre>)/g, "$1");
    html = html.replace(/(<\/pre>)<\/p>/g, "$1");
    html = html.replace(/<p>(<ul>)/g, "$1");
    html = html.replace(/(<\/ul>)<\/p>/g, "$1");
    html = html.replace(/<p>(<blockquote>)/g, "$1");
    html = html.replace(/(<\/blockquote>)<\/p>/g, "$1");

    return html;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // ── Boot ───────────────────────────────────────────────
  init();
})();
