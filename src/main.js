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

async function runOracle() {
    const input = document.getElementById('oracle-input');
    const msg = input.value.trim();
    if (!msg) return;

    const btn = document.getElementById('oracle-run-btn');
    btn.disabled = true;

    document.getElementById('stage-tracker').style.display = 'flex';
    document.getElementById('nexus-animation').style.display = 'flex';
    document.getElementById('oracle-result').style.display = 'none';
    document.getElementById('trace-container').innerHTML = '';

    const startTime = Date.now();

    const updateProgress = (idx) => {
        document.querySelectorAll('.stage-item').forEach((el, i) => {
            el.classList.remove('active');
            if (i < idx) el.classList.add('done');
        });
        const s = document.getElementById(`s${idx + 1}`);
        if (s) s.classList.add('active');
        document.getElementById('nexus-label').textContent = STAGE_LABELS[idx];

        // Update engine roles
        const roles = [
            { deepseek: 'Analyzing', kimi: 'Standby', reasoner: 'Standby', minimax: 'Standby' },
            { deepseek: 'Proposing', kimi: 'Proposing', reasoner: 'Proposing', minimax: 'Proposing' },
            { deepseek: 'Reviewing', kimi: 'Reviewing', reasoner: 'Reviewing', minimax: 'Reviewing' },
            { deepseek: 'Defending', kimi: 'Defending', reasoner: 'Defending', minimax: 'Defending' },
            { deepseek: 'Standby', kimi: 'Standby', reasoner: 'Reconciling', minimax: 'Standby' },
            { deepseek: 'Standby', kimi: 'Polishing', reasoner: 'Standby', minimax: 'Standby' },
            { deepseek: 'Done', kimi: 'Done', reasoner: 'Done', minimax: 'Done' },
        ];
        if (idx < roles.length) {
            const r = roles[idx];
            ['deepseek', 'kimi', 'reasoner', 'minimax'].forEach(k => {
                const roleEl = document.getElementById(`role-${k}`);
                const nodeEl = document.getElementById(`node-${k}`);
                if (roleEl) roleEl.textContent = r[k];
                if (nodeEl) nodeEl.classList.toggle('active', r[k] !== 'Standby' && r[k] !== 'Done');
            });
        }
    };

    const addTrace = (stage, model, content) => {
        const entry = document.createElement('div');
        entry.className = 'trace-entry';
        entry.innerHTML = `<div class="trace-stage">${stage}</div><div class="trace-model">${model}</div><div class="trace-content">${content.substring(0, 500)}...</div>`;
        document.getElementById('trace-container').appendChild(entry);
    };

    try {
        // S1: Deconstruct
        updateProgress(0);
        const s1 = await callAPI("deepseek",
            `Deconstruct: ${msg}\n\n4 bullets: essence, assumptions, constraints, success criteria.`,
            "Surgical analyst.", 400);
        addTrace("Deconstruction", "DeepSeek V3.2", s1);

        // S2: Proposals (sequential to avoid parallel timeout issues)
        updateProgress(1);
        const proposals = [];
        for (const m of MODELS) {
            const txt = await callAPI(m,
                `Brief: ${s1.substring(0, 300)}\n\nQuestion: ${msg}\n\nBest answer in 200 words.`,
                "Expert mode.", 500);
            addTrace("Proposal", MODEL_NAMES[m], txt);
            proposals.push({ model: m, text: txt });
        }

        // S3: Critique (sequential)
        updateProgress(2);
        const propSum = proposals.map((p, i) => `${chr(i)}: ${p.text.substring(0, 250)}`).join("\n\n");
        const critiques = [];
        for (const m of MODELS) {
            const txt = await callAPI(m,
                `Review for: ${msg}\n\n${propSum}\n\n1 flaw, 1 strength each. 100 words.`,
                "Ruthless reviewer.", 300);
            addTrace("Critique", MODEL_NAMES[m], txt);
            critiques.push({ model: m, text: txt });
        }

        // S4: Defense (sequential)
        updateProgress(3);
        const cSum = critiques.map((c, i) => `Peer ${chr(i)}: ${c.text.substring(0, 150)}`).join("\n");
        const defenses = [];
        for (const p of proposals) {
            const txt = await callAPI(p.model,
                `Your proposal: ${p.text.substring(0, 250)}\n\nCritiques:\n${cSum}\n\nImprove. 200 words.`,
                "Refinement mode.", 500);
            addTrace("Defense", MODEL_NAMES[p.model], txt);
            defenses.push({ model: p.model, text: txt });
        }

        // S5: Reconcile
        updateProgress(4);
        const dBlock = defenses.map(d => `[${MODEL_NAMES[d.model]}]: ${d.text.substring(0, 350)}`).join("\n\n");
        const s5 = await callAPI("reasoner",
            `Refined positions on: ${msg}\n\n${dBlock}\n\nSynthesize ONE final protocol. 400 words.`,
            "Senior Consensus Architect.", 800);
        addTrace("Reconciliation", "DeepSeek Reasoner", s5);

        // S6: Polish
        updateProgress(5);
        const s6 = await callAPI("kimi",
            `Strip all meta-talk, markdown, bolding. Clinical prose only.\n\n${s5}`,
            "Senior Editor. Output clean text ONLY.", 1000);
        addTrace("Polish", "Kimi K2.5", s6);

        // Done
        updateProgress(6);
        document.getElementById('nexus-animation').style.display = 'none';
        document.getElementById('oracle-result').style.display = 'block';
        document.getElementById('oracle-output').textContent = s6;
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('result-meta').textContent = `7/7 stages · 4 models · ${elapsed}s`;

    } catch (e) {
        console.error(e);
        document.getElementById('nexus-animation').style.display = 'none';
        document.getElementById('oracle-result').style.display = 'block';
        document.getElementById('oracle-output').textContent = `Error: ${e.message}`;
        document.getElementById('result-meta').textContent = 'Protocol interrupted';
    }

    btn.disabled = false;
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
