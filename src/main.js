import './style.css';

const API_BASE = window.location.origin;

const MODELS = ["deepseek", "kimi", "minimax", "reasoner"];
const MODEL_LABELS = {
    deepseek: "DeepSeek V3.2",
    kimi: "Kimi K2.5",
    minimax: "MiniMax M2.1",
    reasoner: "DeepSeek Reasoner"
};

const STAGE_LABELS_FULL = [
    "Deconstructing Inquiry...",
    "Drafting Parallel Proposals...",
    "Conducting Blind Peer Review...",
    "Adversarial Defense Phase...",
    "Reconciling Expert Positions...",
    "Polishing Sovereign Protocol...",
    "Finalizing..."
];

const STAGE_LABELS_SWIFT = [
    "Framing Core Question...",
    "Drafting Dual Strategies...",
    "Reconciling for Action...",
    "Finalizing..."
];

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

const state = {
    personas: {},
    selectedPersona: null,
    selectedDirectModel: "deepseek",
    councilHistory: [],
    directHistoryByModel: {
        deepseek: [],
        kimi: [],
        minimax: [],
        reasoner: []
    },
    oracleBusy: false
};

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
        if (!res.ok || data.error) {
            throw new Error(data.error || `Request failed (${res.status})`);
        }

        return data.text || "";
    } catch (err) {
        if (err.name === "AbortError") {
            throw new Error("Provider timeout. Retry or use Swift mode.");
        }
        throw err;
    } finally {
        clearTimeout(timeout);
    }
}

function appendBubble(containerId, role, content, meta = "") {
    const container = document.getElementById(containerId);
    const bubble = document.createElement("div");
    bubble.className = `bubble ${role}`;

    if (meta) {
        const metaEl = document.createElement("div");
        metaEl.className = "bubble-meta";
        metaEl.textContent = meta;
        bubble.appendChild(metaEl);
    }

    const contentEl = document.createElement("div");
    contentEl.textContent = content;
    bubble.appendChild(contentEl);

    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

function clearChat(containerId, text) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    appendBubble(containerId, "ai", text);
}

function switchTab(id) {
    document.querySelectorAll(".nav-link").forEach((el) => el.classList.remove("active"));
    document.querySelectorAll(`.nav-link[data-tab=\"${id}\"]`).forEach((el) => el.classList.add("active"));
    document.querySelectorAll(".tab-content").forEach((el) => el.classList.remove("active"));
    const target = document.getElementById(`tab-${id}`);
    if (target) target.classList.add("active");
}

function toggleTrace() {
    const el = document.getElementById("trace-container");
    el.style.display = el.style.display === "none" ? "block" : "none";
}

function oracleMode() {
    const explicit = document.getElementById("oracle-mode").value;
    if (explicit === "swift") return "swift";
    if (explicit === "full") return "full";
    return window.matchMedia("(max-width: 900px)").matches ? "swift" : "full";
}

function updateProgress(stageIdx, labels) {
    document.querySelectorAll(".stage-item").forEach((el, i) => {
        el.classList.remove("active");
        if (i < stageIdx) el.classList.add("done");
    });
    const currentStage = document.getElementById(`s${stageIdx + 1}`);
    if (currentStage) currentStage.classList.add("active");
    document.getElementById("nexus-label").textContent = labels[stageIdx] || "Processing...";
}

function addTrace(stage, model, content) {
    const entry = document.createElement("div");
    entry.className = "trace-entry";

    const stageEl = document.createElement("div");
    stageEl.className = "trace-stage";
    stageEl.textContent = stage;

    const modelEl = document.createElement("div");
    modelEl.className = "trace-model";
    modelEl.textContent = model;

    const contentEl = document.createElement("div");
    contentEl.className = "trace-content";
    contentEl.textContent = content;

    entry.appendChild(stageEl);
    entry.appendChild(modelEl);
    entry.appendChild(contentEl);
    document.getElementById("trace-container").appendChild(entry);
}

function markOracleDone(elapsed, mode, stageCount, modelCount) {
    document.getElementById("nexus-animation").style.display = "none";
    document.getElementById("oracle-result").style.display = "block";
    document.getElementById("result-meta").textContent = `${stageCount}/${stageCount} stages · ${modelCount} models · ${elapsed}s · ${mode.toUpperCase()}`;
}

async function runOracle() {
    if (state.oracleBusy) return;

    const input = document.getElementById("oracle-input");
    const msg = input.value.trim();
    if (!msg) return;

    const mode = oracleMode();
    const stageLabels = mode === "full" ? STAGE_LABELS_FULL : STAGE_LABELS_SWIFT;

    const btn = document.getElementById("oracle-run-btn");
    state.oracleBusy = true;
    btn.disabled = true;

    document.getElementById("stage-tracker").style.display = "flex";
    document.getElementById("nexus-animation").style.display = "flex";
    document.getElementById("oracle-result").style.display = "none";
    document.getElementById("trace-container").style.display = "none";
    document.getElementById("trace-container").innerHTML = "";

    const startedAt = Date.now();

    try {
        if (mode === "swift") {
            updateProgress(0, stageLabels);
            const s1 = await callAPI("deepseek", `Create a concise problem frame with objective, constraints, and success criteria.\n\nQuestion: ${msg}`, "Precision analyst mode.", 280);
            addTrace("Frame", MODEL_LABELS.deepseek, s1);

            updateProgress(1, stageLabels);
            const draftModels = ["deepseek", "kimi"];
            const draftResults = await Promise.allSettled(
                draftModels.map((m) => callAPI(m, `Brief: ${s1}\n\nQuestion: ${msg}\n\nReturn a practical answer in <=160 words.`, "Analytical mode.", 340))
            );

            const drafts = [];
            draftResults.forEach((res, idx) => {
                if (res.status === "fulfilled" && res.value) {
                    drafts.push({ model: draftModels[idx], text: res.value });
                    addTrace("Draft", MODEL_LABELS[draftModels[idx]], res.value);
                }
            });

            if (!drafts.length) throw new Error("All draft models timed out. Retry once or switch model keys.");

            updateProgress(2, stageLabels);
            const payload = drafts.map((d) => `[${d.model}] ${d.text}`).join("\n\n");
            const merged = await callAPI("reasoner", `Unify these responses into one action-ready answer for: ${msg}\n\n${payload}\n\nOutput: clear steps + risk note.`, "Senior synthesizer.", 520);
            addTrace("Merge", MODEL_LABELS.reasoner, merged);

            updateProgress(3, stageLabels);
            document.getElementById("oracle-output").textContent = merged;
            markOracleDone(((Date.now() - startedAt) / 1000).toFixed(1), mode, 4, drafts.length + 1);
            return;
        }

        updateProgress(0, stageLabels);
        const s1 = await callAPI("deepseek", `Deconstruct this in 4 bullets: essence, assumptions, constraints, criteria.\n\nInquiry: ${msg}`, "Surgical analyst mode.", 320);
        addTrace("Deconstruction", MODEL_LABELS.deepseek, s1);

        updateProgress(1, stageLabels);
        const proposals = await Promise.allSettled(
            MODELS.map((m) => callAPI(m, `Brief: ${s1}\n\nQuestion: ${msg}\n\nProvide your best answer (<=180 words).`, "Analytical mode.", 420))
        );
        const liveProposals = [];
        proposals.forEach((res, idx) => {
            if (res.status === "fulfilled") {
                liveProposals.push({ model: MODELS[idx], text: res.value });
                addTrace("Proposal", MODEL_LABELS[MODELS[idx]], res.value);
            }
        });

        if (liveProposals.length < 2) {
            throw new Error("Not enough model responses in full mode. Use Swift mode for lower latency.");
        }

        updateProgress(2, stageLabels);
        const propSummary = liveProposals.map((p, i) => `Option ${i + 1} (${p.model}): ${p.text.slice(0, 260)}`).join("\n\n");
        const critiques = await Promise.allSettled(
            liveProposals.map((p) => callAPI(p.model, `Review these options for question: ${msg}\n\n${propSummary}\n\nGive one flaw and one strength per option.`, "Ruthless reviewer.", 360))
        );
        const critiqueText = critiques.filter((c) => c.status === "fulfilled").map((c) => c.value).join("\n\n");
        if (!critiqueText) throw new Error("Critique stage failed. Retry or switch to Swift mode.");
        addTrace("Critique", "Council", critiqueText);

        updateProgress(3, stageLabels);
        const defenses = await Promise.allSettled(
            liveProposals.map((p) => callAPI(p.model, `Your proposal: ${p.text}\n\nCritiques:\n${critiqueText}\n\nImprove the answer with stronger logic and clearer action.`, "Refinement mode.", 430))
        );
        const defensePayload = defenses
            .map((d, i) => (d.status === "fulfilled" ? `[${liveProposals[i].model}] ${d.value}` : ""))
            .filter(Boolean)
            .join("\n\n");
        if (!defensePayload) throw new Error("Defense stage failed. Retry in Swift mode.");
        addTrace("Defense", "Council", defensePayload);

        updateProgress(4, stageLabels);
        const s5 = await callAPI("reasoner", `Experts refined positions on: ${msg}\n\n${defensePayload}\n\nSynthesize one final protocol with priorities and risks.`, "Senior architect.", 620);
        addTrace("Reconciliation", MODEL_LABELS.reasoner, s5);

        updateProgress(5, stageLabels);
        const s6 = await callAPI("kimi", `Improve readability and remove meta-talk from this response.\n\nText:\n${s5}`, "Senior editor.", 620);
        addTrace("Polish", MODEL_LABELS.kimi, s6);

        updateProgress(6, stageLabels);
        document.getElementById("oracle-output").textContent = s6;
        markOracleDone(((Date.now() - startedAt) / 1000).toFixed(1), mode, 7, liveProposals.length);
    } catch (e) {
        document.getElementById("nexus-animation").style.display = "none";
        document.getElementById("oracle-result").style.display = "block";
        document.getElementById("oracle-output").textContent = `Oracle error: ${e.message}`;
    } finally {
        state.oracleBusy = false;
        btn.disabled = false;
    }
}

function renderPersonaList() {
    const container = document.getElementById("council-persona-list");
    container.innerHTML = "";

    Object.entries(state.personas).forEach(([id, p]) => {
        const button = document.createElement("button");
        button.className = `selector-btn ${state.selectedPersona === id ? "active" : ""}`;
        button.type = "button";
        button.innerHTML = `<span class=\"selector-title\">${p.name}</span><span class=\"selector-sub\">${p.role}</span>`;
        button.onclick = () => {
            state.selectedPersona = id;
            renderPersonaList();
            clearChat("council-chat-history", `Connected to ${p.name}. Ask your question.`);
            document.getElementById("council-status").textContent = `Linked: ${p.name}`;
        };
        container.appendChild(button);
    });
}

function renderModelList() {
    const container = document.getElementById("chat-model-list");
    container.innerHTML = "";

    MODELS.forEach((m) => {
        const button = document.createElement("button");
        button.className = `selector-btn ${state.selectedDirectModel === m ? "active" : ""}`;
        button.type = "button";
        button.innerHTML = `<span class=\"selector-title\">${MODEL_LABELS[m]}</span><span class=\"selector-sub\">Direct channel</span>`;
        button.onclick = () => {
            state.selectedDirectModel = m;
            renderModelList();
            redrawDirectHistory();
        };
        container.appendChild(button);
    });
}

function redrawDirectHistory() {
    const container = document.getElementById("chat-history");
    container.innerHTML = "";
    const history = state.directHistoryByModel[state.selectedDirectModel] || [];

    if (!history.length) {
        appendBubble("chat-history", "ai", `Connected to ${MODEL_LABELS[state.selectedDirectModel]}.`);
        return;
    }

    history.forEach((item) => appendBubble("chat-history", item.role, item.content, item.meta || ""));
}

async function sendCouncilMessage() {
    const input = document.getElementById("council-input");
    const text = input.value.trim();
    if (!text) return;
    if (!state.selectedPersona) {
        alert("Select a persona first.");
        return;
    }

    input.value = "";
    appendBubble("council-chat-history", "user", text);

    const persona = state.personas[state.selectedPersona];
    document.getElementById("council-status").textContent = "Thinking...";

    const historyTail = state.councilHistory.slice(-6).map((m) => `${m.role.toUpperCase()}: ${m.content}`).join("\n");
    const prompt = historyTail ? `${historyTail}\nUSER: ${text}` : text;

    try {
        const response = await callAPI(persona.preferred_model || "deepseek", prompt, persona.system_prompt, 620);
        appendBubble("council-chat-history", "ai", response, persona.name);

        state.councilHistory.push({ role: "user", content: text });
        state.councilHistory.push({ role: "ai", content: response });
        state.councilHistory = state.councilHistory.slice(-20);

        document.getElementById("council-status").textContent = `Ready: ${persona.name}`;
    } catch (e) {
        appendBubble("council-chat-history", "ai", `Error: ${e.message}`, "System");
        document.getElementById("council-status").textContent = "Error";
    }
}

async function sendDirectMessage() {
    const input = document.getElementById("chat-input");
    const text = input.value.trim();
    if (!text) return;

    const model = state.selectedDirectModel;
    input.value = "";
    appendBubble("chat-history", "user", text);
    state.directHistoryByModel[model].push({ role: "user", content: text });

    const history = state.directHistoryByModel[model].slice(-8);
    const prompt = history.map((h) => `${h.role.toUpperCase()}: ${h.content}`).join("\n");

    try {
        const reply = await callAPI(model, prompt, "Direct answer mode. Be concise but complete.", 700);
        state.directHistoryByModel[model].push({ role: "ai", content: reply, meta: MODEL_LABELS[model] });
        redrawDirectHistory();
    } catch (e) {
        appendBubble("chat-history", "ai", `Error: ${e.message}`, "System");
    }
}

async function loadPersonas() {
    try {
        const res = await fetch(`${API_BASE}/data/council_personas.json`);
        if (res.ok) {
            state.personas = await res.json();
        } else {
            state.personas = FALLBACK_PERSONAS;
        }
    } catch (_e) {
        state.personas = FALLBACK_PERSONAS;
    }
    state.selectedPersona = Object.keys(state.personas)[0] || null;
}

window.runOracle = runOracle;
window.switchTab = switchTab;
window.toggleTrace = toggleTrace;
window.sendCouncilMessage = sendCouncilMessage;
window.sendDirectMessage = sendDirectMessage;

window.addEventListener("DOMContentLoaded", async () => {
    switchTab("home");
    renderModelList();
    redrawDirectHistory();

    await loadPersonas();
    renderPersonaList();
    const firstPersona = state.personas[state.selectedPersona];
    if (firstPersona) {
        clearChat("council-chat-history", `Connected to ${firstPersona.name}. Ask your question.`);
        document.getElementById("council-status").textContent = `Linked: ${firstPersona.name}`;
    }
});
