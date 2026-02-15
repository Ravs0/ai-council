import './style.css';

const API_BASE = window.location.origin;

const MODELS = ["deepseek", "kimi", "minimax", "reasoner"];
const MODEL_NAMES = {
    deepseek: "DeepSeek V3.2",
    kimi: "Kimi K2.5",
    minimax: "Minimax M2.1",
    reasoner: "DeepSeek Reasoner"
};
const STAGE_LABELS = [
    "Deconstructing Inquiry...",
    "Drafting Parallel Proposals...",
    "Conducting Blind Peer Review...",
    "Adversarial Defense Phase...",
    "Reconciling Expert Positions...",
    "Polishing Sovereign Protocol...",
    "Finalizing..."
];

const PERSONAS = {
    leibowitz: {
        name: "Samuel Leibowitz",
        role: "Trial Strategist",
        system: "You are Samuel Leibowitz, the legendary defense attorney. Analyze everything through the lens of courtroom strategy, logical fallacies, and persuasive argumentation. Be incisive and direct."
    },
    parfit: {
        name: "Derek Parfit",
        role: "Moral Philosopher",
        system: "You are Derek Parfit, author of Reasons and Persons. Analyze through personal identity, moral reasoning, and reductionist philosophy. Be precise and thought-provoking."
    },
    richelieu: {
        name: "Cardinal Richelieu",
        role: "Statecraft & Power",
        system: "You are Cardinal Richelieu, master of statecraft. Analyze through the lens of power dynamics, institutional control, and political strategy. Be calculating and pragmatic."
    }
};

let selectedPersona = null;
let selectedModel = null;

// ─── API CALL ────────────────────────────────────────────────────────────────

async function callAPI(model, prompt, system = "", maxTokens = 1000) {
    const res = await fetch(`${API_BASE}/api/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model, prompt, system, max_tokens: maxTokens })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    return data.text;
}

// ─── ORACLE PROTOCOL ─────────────────────────────────────────────────────────

// ─── ORACLE PROTOCOL (OPTIMIZED) ─────────────────────────────────────────────

async function runOracle() {
    const input = document.getElementById('oracle-input');
    const msg = input.value.trim();
    if (!msg) return;

    const btn = document.getElementById('oracle-run-btn');
    btn.disabled = true;

    // UI Reset
    document.getElementById('stage-tracker').style.display = 'flex';
    document.getElementById('nexus-animation').style.display = 'flex';
    document.getElementById('oracle-result').style.display = 'none';
    document.getElementById('trace-container').innerHTML = '';

    const startTime = Date.now();

    // FAST TRACK MODELS (No Reasoner here - too slow)
    // We use DeepSeek V3, Kimi, Minimax for proposal/critique/defense loops.
    const FAST_MODELS = ["deepseek", "kimi", "minimax"];

    const updateProgress = (idx, labelOverride = null) => {
        document.querySelectorAll('.stage-item').forEach((el, i) => {
            el.classList.remove('active');
            if (i < idx) el.classList.add('done');
        });
        const s = document.getElementById(`s${idx + 1}`);
        if (s) s.classList.add('active');

        const label = labelOverride || STAGE_LABELS[idx];
        document.getElementById('nexus-label').textContent = label;

        // Update Grid Status
        ['deepseek', 'kimi', 'minimax', 'reasoner'].forEach(k => {
            const node = document.getElementById(`node-${k}`);
            const role = document.getElementById(`role-${k}`);
            if (!node || !role) return;

            // Visual Logic
            if (idx === 0 && k === 'deepseek') { role.textContent = 'Analyst'; node.classList.add('active'); }
            else if ((idx === 1 || idx === 3) && FAST_MODELS.includes(k)) { role.textContent = 'Active'; node.classList.add('active'); }
            else if (idx === 2 && FAST_MODELS.includes(k)) { role.textContent = 'Reviewing'; node.classList.add('active'); }
            else if (idx === 4 && k === 'reasoner') { role.textContent = 'Judge'; node.classList.add('active'); }
            else if (idx === 5 && k === 'kimi') { role.textContent = 'Editor'; node.classList.add('active'); }
            else { role.textContent = 'Standby'; node.classList.remove('active'); }
        });
    };

    const addTrace = (stage, model, content) => {
        const entry = document.createElement('div');
        entry.className = 'trace-entry';
        const preview = content.length > 500 ? content.substring(0, 500) + "..." : content;
        entry.innerHTML = `<div class="trace-stage">${stage}</div><div class="trace-model">${model}</div><div class="trace-content">${preview}</div>`;
        document.getElementById('trace-container').appendChild(entry);
    };

    try {
        // ── STAGE 1: DECONSTRUCTION (DeepSeek V3) ──
        updateProgress(0);
        const s1 = await callAPI("deepseek",
            `Refine this inquiry into 3 robust pillars: Core Question, Hidden Variables, Required Constraints.\n\nInquiry: ${msg}`,
            "Strategic Analyst.", 400);
        addTrace("Deconstruction", "DeepSeek V3", s1);

        // ── STAGE 2: PARALLEL PROPOSALS (Fast Models) ──
        updateProgress(1);
        // Execute in PARALLEL because these are fast models (<10s each).
        const propResults = await Promise.allSettled(FAST_MODELS.map(m =>
            callAPI(m, `Context: ${s1}\n\nQuestion: ${msg}\n\nPropose a direct solution (200 words).`, "Expert Consultant.", 500)
        ));

        const proposals = propResults.map((r, i) => {
            const model = FAST_MODELS[i];
            const txt = r.status === 'fulfilled' ? r.value : "[Network Failure]";
            addTrace("Proposal", MODEL_NAMES[model], txt);
            return { model, text: txt };
        });

        // ── STAGE 3: BLIND CRITIQUE (Fast Models) ──
        updateProgress(2);
        const pSummary = proposals.map((p, i) => `Option ${chr(i)}: ${p.text.substring(0, 300)}`).join("\n\n");

        // Parallel Critique
        const critResults = await Promise.allSettled(FAST_MODELS.map(m =>
            callAPI(m, `Analyze these options for: ${msg}\n\n${pSummary}\n\nIdentify the single biggest flaw in each. Be ruthless.`, "Red Team.", 400)
        ));

        const critiques = critResults.map((r, i) => {
            const model = FAST_MODELS[i];
            const txt = r.status === 'fulfilled' ? r.value : "No critique.";
            addTrace("Critique", MODEL_NAMES[model], txt);
            return { model, text: txt };
        });

        // ── STAGE 4: DEFENSE (Fast Models) ──
        updateProgress(3);
        const cSummary = critiques.map((c, i) => `Critic ${chr(i)}: ${c.text.substring(0, 200)}`).join("\n");

        // Parallel Defense
        const defResults = await Promise.allSettled(proposals.map(p =>
            callAPI(p.model, `Your original proposal: ${p.text.substring(0, 300)}\n\nCritiques received:\n${cSummary}\n\nUpdate your solution to address these flaws.`, "Resilient Architect.", 600)
        ));

        const defenses = defResults.map((r, i) => {
            const txt = r.status === 'fulfilled' ? r.value : "Defense failed.";
            addTrace("Defense", MODEL_NAMES[proposals[i].model], txt);
            return { model: proposals[i].model, text: txt };
        });

        // ── STAGE 5: RECONCILIATION (DeepSeek Reasoner - The Heavy Lifter) ──
        updateProgress(4);
        const dBlock = defenses.map(d => `[${MODEL_NAMES[d.model]}]: ${d.text}`).join("\n\n");

        // This is the ONLY slow call allowed. 60s max.
        const s5 = await callAPI("reasoner",
            `Experts have debated on: ${msg}\n\nFinal Positions:\n${dBlock}\n\nSynthesize the absolute TRUTH. One cohesive protocol. No "Option A/B". Just the answer.`,
            "Supreme Judge.", 1000);
        addTrace("Reconciliation", "DeepSeek Reasoner", s5);

        // ── STAGE 6: POLISH (Kimi) ──
        updateProgress(5);
        const s6 = await callAPI("kimi",
            `Rewrite this text to be clinically precise, authoritative, and stripped of all meta-commentary ("Here is the answer"). Just the raw protocol.\n\nText:\n${s5}`,
            "Chief Editor.", 1000);
        addTrace("Polish", "Kimi K2.5", s6);

        // ── DONE ──
        updateProgress(6, "Protocol Complete");
        document.getElementById('nexus-animation').style.display = 'none';
        document.getElementById('oracle-result').style.display = 'block';
        document.getElementById('oracle-output').textContent = s6;

        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('result-meta').textContent = `7/7 stages · 4 models · ${elapsed}s`;

    } catch (e) {
        console.error(e);
        document.getElementById('nexus-animation').style.display = 'none';
        alert(`Oracle Error: ${e.message}`);
    } finally {
        btn.disabled = false;
    }
}

function chr(i) { return String.fromCharCode(65 + i); }

// ─── COUNCIL HALL ─────────────────────────────────────────────────────────────

function initCouncil() {
    const list = document.getElementById('council-persona-list');
    if (!list) return;
    list.innerHTML = '';
    Object.entries(PERSONAS).forEach(([key, p]) => {
        const div = document.createElement('div');
        div.className = 'persona-item';
        div.innerHTML = `<strong>${p.name}</strong><br><small>${p.role}</small>`;
        div.onclick = () => {
            selectedPersona = key;
            list.querySelectorAll('.persona-item').forEach(el => el.classList.remove('active'));
            div.classList.add('active');
            const status = document.getElementById('council-status');
            if (status) status.textContent = p.name;
        };
        list.appendChild(div);
    });
}

async function sendCouncilMessage() {
    if (!selectedPersona) { alert('Select a persona first.'); return; }
    const input = document.getElementById('council-input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    const chat = document.getElementById('council-chat-history');
    chat.innerHTML += `<div class="bubble user">${msg}</div>`;
    chat.innerHTML += `<div class="bubble ai" id="council-loading">Thinking...</div>`;
    chat.scrollTop = chat.scrollHeight;

    try {
        const persona = PERSONAS[selectedPersona];
        const reply = await callAPI("deepseek", msg, persona.system, 1500);
        document.getElementById('council-loading').outerHTML = `<div class="bubble ai"><strong>${persona.name}:</strong><br>${reply}</div>`;
    } catch (e) {
        document.getElementById('council-loading').outerHTML = `<div class="bubble ai">Error: ${e.message}</div>`;
    }
    chat.scrollTop = chat.scrollHeight;
}

// ─── DIRECT UPLINK ────────────────────────────────────────────────────────────

function initDirect() {
    const list = document.getElementById('chat-model-list');
    if (!list) return;
    list.innerHTML = '';
    MODELS.forEach(m => {
        const div = document.createElement('div');
        div.className = 'persona-item';
        div.innerHTML = `<strong>${MODEL_NAMES[m]}</strong>`;
        div.onclick = () => {
            selectedModel = m;
            list.querySelectorAll('.persona-item').forEach(el => el.classList.remove('active'));
            div.classList.add('active');
        };
        list.appendChild(div);
    });
}

async function sendDirectMessage() {
    if (!selectedModel) { alert('Select a model first.'); return; }
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    const chat = document.getElementById('chat-history');
    chat.innerHTML += `<div class="bubble user">${msg}</div>`;
    chat.innerHTML += `<div class="bubble ai" id="direct-loading">Processing...</div>`;
    chat.scrollTop = chat.scrollHeight;

    try {
        const reply = await callAPI(selectedModel, msg, "You are a helpful, precise assistant.", 2000);
        document.getElementById('direct-loading').outerHTML = `<div class="bubble ai">${reply}</div>`;
    } catch (e) {
        document.getElementById('direct-loading').outerHTML = `<div class="bubble ai">Error: ${e.message}</div>`;
    }
    chat.scrollTop = chat.scrollHeight;
}

// ─── NAVIGATION ───────────────────────────────────────────────────────────────

function switchTab(id) {
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    document.querySelectorAll(`.nav-link[data-tab="${id}"]`).forEach(el => el.classList.add('active'));
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    const target = document.getElementById(`tab-${id}`);
    if (target) target.classList.add('active');
}

function toggleTrace() {
    const el = document.getElementById('trace-container');
    el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

// ─── INIT ─────────────────────────────────────────────────────────────────────

window.onload = () => {
    switchTab('home');
    initCouncil();
    initDirect();
};

// Expose to global scope for inline onclick handlers
window.runOracle = runOracle;
window.switchTab = switchTab;
window.toggleTrace = toggleTrace;
window.sendCouncilMessage = sendCouncilMessage;
window.sendDirectMessage = sendDirectMessage;
