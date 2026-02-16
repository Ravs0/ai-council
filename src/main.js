import "./style.css";
import tolkeSystemPrompt from "./prompts/tolke-system-prompt.txt?raw";

const API_BASE = window.location.origin;

const MODELS = ["deepseek", "kimi", "minimax", "reasoner", "gemini-flash", "gemini-pro"];
const ORACLE_PROPOSAL_MODELS = ["deepseek", "kimi", "reasoner", "gemini-flash"];
const MODEL_LABELS = {
    deepseek: "DeepSeek V3.2",
    kimi: "Kimi K2.5",
    minimax: "MiniMax M2.1",
    reasoner: "DeepSeek Reasoner",
    "gemini-flash": "Gemini 3 Flash",
    "gemini-pro": "Gemini 2.5 Pro"
};

const FALLBACK_PERSONAS = {
    leibowitz: {
        name: "Samuel Leibowitz",
        role: "Trial Strategist",
        preferred_model: "deepseek",
        system_prompt: "You are Samuel Leibowitz in peak form. Reconstruct facts first, separate evidence from inference, and produce courtroom-ready strategy in concise language."
    },
    richelieu: {
        name: "Cardinal Richelieu",
        role: "Statecraft Architect",
        preferred_model: "reasoner",
        system_prompt: "You are Cardinal Richelieu advising on strategy through raison d'etat. Map actors, leverage, sequencing, betrayal points, and concrete options."
    },
    parfit: {
        name: "Derek Parfit",
        role: "Moral and Personal Identity Analyst",
        preferred_model: "reasoner",
        system_prompt: "You are Derek Parfit. Clarify terms, test claims with counterexamples, and separate prudential from moral reasons."
    }
};

const SHARED_STYLE_ADDON = "Be concrete, direct, and simple. If the user avoids the point, call it out clearly and bring focus back.";

const state = {
    mode: "direct",
    personas: {},
    selectedDirectModel: "deepseek",
    selectedTolkeModel: "gemini-flash",
    selectedPersona: "leibowitz",
    histories: {},
    lastOracleTrace: []
};

function modeTitle(mode) {
    if (mode === "oracle") return "Oracle";
    if (mode === "council") return "Council";
    if (mode === "tolke") return "Tolke";
    return "Direct";
}

function currentKey() {
    if (state.mode === "oracle") return "oracle";
    if (state.mode === "direct") return `direct:${state.selectedDirectModel}`;
    if (state.mode === "tolke") return `tolke:${state.selectedTolkeModel}`;
    return `council:${state.selectedPersona}`;
}

function ensureHistory(key) {
    if (!state.histories[key]) state.histories[key] = [];
    return state.histories[key];
}

function appendMessage(key, role, content, meta = "") {
    const history = ensureHistory(key);
    history.push({ role, content, meta, ts: Date.now() });
}

function clearNode(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
}

function renderFeed() {
    const key = currentKey();
    const feed = document.getElementById("chat-feed");
    clearNode(feed);

    const history = ensureHistory(key);
    if (!history.length) {
        appendMessage(key, "assistant", `${modeTitle(state.mode)} ready. Send a message to start.`, "System");
    }

    ensureHistory(key).forEach((item) => {
        const bubble = document.createElement("div");
        bubble.className = `msg ${item.role === "user" ? "user" : "assistant"}`;

        if (item.meta) {
            const meta = document.createElement("div");
            meta.className = "msg-meta";
            meta.textContent = item.meta;
            bubble.appendChild(meta);
        }

        const body = document.createElement("div");
        body.textContent = item.content;
        bubble.appendChild(body);
        feed.appendChild(bubble);
    });

    feed.scrollTop = feed.scrollHeight;
    renderTracePanel();
}

function renderTracePanel() {
    const wrap = document.getElementById("oracle-trace-wrap");
    const trace = document.getElementById("oracle-trace");
    clearNode(trace);

    if (state.mode !== "oracle" || !state.lastOracleTrace.length) {
        wrap.classList.add("hidden");
        return;
    }

    state.lastOracleTrace.forEach((t) => {
        const item = document.createElement("div");
        item.className = "trace-item";

        const h = document.createElement("div");
        h.className = "trace-head";
        h.textContent = `${t.stage} · ${t.model}`;

        const b = document.createElement("div");
        b.className = "trace-body";
        b.textContent = t.content;

        item.appendChild(h);
        item.appendChild(b);
        trace.appendChild(item);
    });

    wrap.classList.remove("hidden");
}

function setMode(mode) {
    state.mode = mode;
    document.querySelectorAll(".mode-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.mode === mode);
    });

    document.querySelectorAll(".context-group").forEach((g) => {
        g.classList.toggle("hidden", g.dataset.for !== mode);
    });

    const modeLabel = document.getElementById("mode-label");
    if (modeLabel) modeLabel.textContent = modeTitle(mode);

    const input = document.getElementById("chat-input");
    if (mode === "oracle") input.placeholder = "Ask Oracle a high-stakes question...";
    else if (mode === "council") input.placeholder = "Ask the selected persona...";
    else if (mode === "tolke") input.placeholder = "Talk to Tolke...";
    else input.placeholder = "Type your message...";

    renderFeed();
}

async function callAPI(model, prompt, system = "", maxTokens = 700, timeoutMs = 22000) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const res = await fetch(`${API_BASE}/api/call`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model, prompt, system, max_tokens: maxTokens }),
            signal: controller.signal
        });
        const data = await res.json();
        if (!res.ok || data.error) throw new Error(data.error || `Request failed (${res.status})`);
        return data.text || "";
    } catch (err) {
        if (err.name === "AbortError") throw new Error("Provider timeout. Retry with Swift mode.");
        throw err;
    } finally {
        clearTimeout(timeout);
    }
}

async function callWithFallback(primaryModel, fallbackModel, prompt, system, maxTokens, timeoutMs = 22000) {
    try {
        const text = await callAPI(primaryModel, prompt, system, maxTokens, timeoutMs);
        return { model: primaryModel, text };
    } catch (_e) {
        const text = await callAPI(fallbackModel, prompt, system, maxTokens, timeoutMs);
        return { model: fallbackModel, text };
    }
}

async function runOracle(userText) {
    const key = currentKey();
    const modePref = document.getElementById("oracle-mode").value;
    const mode = modePref === "auto" ? (window.matchMedia("(max-width: 900px)").matches ? "swift" : "full") : modePref;
    const trace = [];

    const addTrace = (stage, model, content) => {
        trace.push({ stage, model, content });
    };

    if (mode === "swift") {
        const s1 = await callAPI("deepseek", `Create a concise problem frame with objective, constraints, and success criteria.\n\nQuestion: ${userText}`, "Precision analyst mode.", 280);
        addTrace("Frame", MODEL_LABELS.deepseek, s1);

        const draftModels = ["deepseek", "gemini-flash"];
        const draftResults = await Promise.allSettled(
            draftModels.map((m) => callAPI(m, `Brief: ${s1}\n\nQuestion: ${userText}\n\nReturn a practical answer in <=160 words.`, "Analytical mode.", 340))
        );

        const drafts = [];
        draftResults.forEach((r, i) => {
            if (r.status === "fulfilled") {
                drafts.push({ model: draftModels[i], text: r.value });
                addTrace("Draft", MODEL_LABELS[draftModels[i]], r.value);
            }
        });

        if (!drafts.length) throw new Error("All draft models failed.");

        const payload = drafts.map((d) => `[${d.model}] ${d.text}`).join("\n\n");
        const merged = await callWithFallback(
            "gemini-pro",
            "reasoner",
            `Unify these responses into one action-ready answer for: ${userText}\n\n${payload}\n\nOutput: clear steps + risk note.`,
            "Senior synthesizer.",
            520
        );
        addTrace("Merge", MODEL_LABELS[merged.model], merged.text);

        state.lastOracleTrace = trace;
        appendMessage(key, "assistant", merged.text, `Oracle · ${mode.toUpperCase()}`);
        return;
    }

    const s1 = await callAPI("deepseek", `Deconstruct this in 4 bullets: essence, assumptions, constraints, criteria.\n\nInquiry: ${userText}`, "Surgical analyst mode.", 320);
    addTrace("Deconstruction", MODEL_LABELS.deepseek, s1);

    const proposalResults = await Promise.allSettled(
        ORACLE_PROPOSAL_MODELS.map((m) => callAPI(m, `Brief: ${s1}\n\nQuestion: ${userText}\n\nProvide your best answer (<=180 words).`, "Analytical mode.", 420))
    );

    const proposals = [];
    proposalResults.forEach((r, i) => {
        if (r.status === "fulfilled") {
            proposals.push({ model: ORACLE_PROPOSAL_MODELS[i], text: r.value });
            addTrace("Proposal", MODEL_LABELS[ORACLE_PROPOSAL_MODELS[i]], r.value);
        }
    });

    if (proposals.length < 2) throw new Error("Not enough proposal responses.");

    const summary = proposals.map((p, i) => `Option ${i + 1} (${p.model}): ${p.text.slice(0, 260)}`).join("\n\n");
    const critiqueResults = await Promise.allSettled(
        proposals.map((p) => callAPI(p.model, `Review these options for question: ${userText}\n\n${summary}\n\nGive one flaw and one strength per option.`, "Ruthless reviewer.", 360))
    );
    const critiques = critiqueResults.filter((c) => c.status === "fulfilled").map((c) => c.value).join("\n\n");
    if (!critiques) throw new Error("Critique stage failed.");
    addTrace("Critique", "Council", critiques);

    const defenseResults = await Promise.allSettled(
        proposals.map((p) => callAPI(p.model, `Your proposal: ${p.text}\n\nCritiques:\n${critiques}\n\nImprove the answer with stronger logic and clearer action.`, "Refinement mode.", 430))
    );
    const defensePayload = defenseResults
        .map((d, i) => (d.status === "fulfilled" ? `[${proposals[i].model}] ${d.value}` : ""))
        .filter(Boolean)
        .join("\n\n");
    if (!defensePayload) throw new Error("Defense stage failed.");
    addTrace("Defense", "Council", defensePayload);

    const recon = await callWithFallback(
        "gemini-pro",
        "reasoner",
        `Experts refined positions on: ${userText}\n\n${defensePayload}\n\nSynthesize one final protocol with priorities and risks.`,
        "Senior architect.",
        620
    );
    addTrace("Reconciliation", MODEL_LABELS[recon.model], recon.text);

    const polished = await callAPI("kimi", `Improve readability and remove meta-talk from this response.\n\nText:\n${recon.text}`, "Senior editor.", 620);
    addTrace("Polish", MODEL_LABELS.kimi, polished);

    state.lastOracleTrace = trace;
    appendMessage(key, "assistant", polished, "Oracle · FULL");
}

async function sendMessage() {
    const input = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const text = input.value.trim();
    if (!text) return;

    const key = currentKey();
    appendMessage(key, "user", text);
    input.value = "";
    renderFeed();

    sendBtn.disabled = true;

    try {
        if (state.mode === "oracle") {
            await runOracle(text);
        } else if (state.mode === "council") {
            const persona = state.personas[state.selectedPersona];
            const historyTail = ensureHistory(key).slice(-8).map((m) => `${m.role.toUpperCase()}: ${m.content}`).join("\n");
            const prompt = historyTail ? `${historyTail}\nUSER: ${text}` : text;
            const response = await callAPI(
                persona.preferred_model || "deepseek",
                prompt,
                `${persona.system_prompt}\n\n${SHARED_STYLE_ADDON}`,
                720
            );
            appendMessage(key, "assistant", response, persona.name);
        } else if (state.mode === "tolke") {
            const historyTail = ensureHistory(key).slice(-10).map((m) => `${m.role.toUpperCase()}: ${m.content}`).join("\n");
            const prompt = historyTail ? `${historyTail}\nUSER: ${text}` : text;
            const model = state.selectedTolkeModel;
            const response = await callAPI(model, prompt, tolkeSystemPrompt, 900);
            appendMessage(key, "assistant", response, `Tolke · ${MODEL_LABELS[model]}`);
        } else {
            const model = state.selectedDirectModel;
            const historyTail = ensureHistory(key).slice(-8).map((m) => `${m.role.toUpperCase()}: ${m.content}`).join("\n");
            const prompt = historyTail ? `${historyTail}\nUSER: ${text}` : text;
            const response = await callAPI(model, prompt, `Direct answer mode. Be concise but complete.\n${SHARED_STYLE_ADDON}`, 700);
            appendMessage(key, "assistant", response, MODEL_LABELS[model]);
        }
    } catch (e) {
        appendMessage(key, "assistant", `Error: ${e.message}`, "System");
    } finally {
        sendBtn.disabled = false;
        renderFeed();
    }
}

function fillModelSelect(id, selected) {
    const select = document.getElementById(id);
    clearNode(select);
    MODELS.forEach((m) => {
        const option = document.createElement("option");
        option.value = m;
        option.textContent = MODEL_LABELS[m];
        if (m === selected) option.selected = true;
        select.appendChild(option);
    });
}

function fillPersonaSelect() {
    const select = document.getElementById("council-persona");
    clearNode(select);

    Object.entries(state.personas).forEach(([id, p]) => {
        const option = document.createElement("option");
        option.value = id;
        option.textContent = `${p.name} · ${p.role}`;
        if (id === state.selectedPersona) option.selected = true;
        select.appendChild(option);
    });
}

async function loadPersonas() {
    try {
        const res = await fetch(`${API_BASE}/data/council_personas.json`);
        if (!res.ok) {
            state.personas = FALLBACK_PERSONAS;
        } else {
            state.personas = await res.json();
        }
    } catch (_e) {
        state.personas = FALLBACK_PERSONAS;
    }

    if (!state.personas[state.selectedPersona]) {
        state.selectedPersona = Object.keys(state.personas)[0] || "leibowitz";
    }
}

function wireEvents() {
    document.querySelectorAll(".mode-btn").forEach((btn) => {
        btn.addEventListener("click", () => setMode(btn.dataset.mode));
    });

    document.getElementById("send-btn").addEventListener("click", sendMessage);
    document.getElementById("chat-input").addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    document.getElementById("direct-model").addEventListener("change", (e) => {
        state.selectedDirectModel = e.target.value;
        renderFeed();
    });

    document.getElementById("tolke-model").addEventListener("change", (e) => {
        state.selectedTolkeModel = e.target.value;
        renderFeed();
    });

    document.getElementById("council-persona").addEventListener("change", (e) => {
        state.selectedPersona = e.target.value;
        renderFeed();
    });

    document.getElementById("new-chat-btn").addEventListener("click", () => {
        const key = currentKey();
        state.histories[key] = [];
        if (state.mode === "oracle") state.lastOracleTrace = [];
        renderFeed();
    });
}

async function init() {
    await loadPersonas();
    fillModelSelect("direct-model", state.selectedDirectModel);
    fillModelSelect("tolke-model", state.selectedTolkeModel);
    fillPersonaSelect();
    wireEvents();
    setMode("direct");
}

init();
