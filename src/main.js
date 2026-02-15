import './style.css';

const API_BASE = window.location.origin;

const MODELS = ["deepseek", "kimi", "minimax", "reasoner"];
const STAGE_LABELS = [
    "Deconstructing Inquiry...",
    "Drafting Parallel Proposals...",
    "Conducting Blind Peer Review...",
    "Adversarial Defense Phase...",
    "Reconciling Expert Positions...",
    "Polishing Sovereign Protocol...",
    "Finalizing..."
];

// --- Oracle Core ---

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
    const trace = [];

    const startTime = Date.now();
    const updateProgress = (stageIdx, text = null) => {
        document.querySelectorAll('.stage-item').forEach((el, i) => {
            el.classList.remove('active');
            if (i < stageIdx) el.classList.add('done');
        });
        const currentStage = document.getElementById(`s${stageIdx + 1}`);
        if (currentStage) currentStage.classList.add('active');
        document.getElementById('nexus-label').textContent = STAGE_LABELS[stageIdx];
    };

    const addTrace = (stage, model, content) => {
        trace.push({ stage, model, content });
        const entry = document.createElement('div');
        entry.className = 'trace-entry';
        entry.innerHTML = `<div class="trace-stage">${stage}</div><div class="trace-model">${model}</div><div class="trace-content">${content}</div>`;
        document.getElementById('trace-container').appendChild(entry);
    };

    try {
        // STAGE 1: Deconstruction
        updateProgress(0);
        const s1 = await callAPI("deepseek", `Deconstruct this in 4 bullets: essence, assumptions, constraints, criteria.\n\nInquiry: ${msg}`, "Surgical analyst mode.", 400);
        addTrace("Deconstruction", "DeepSeek V3.2", s1);

        // STAGE 2: Parallel Proposals
        updateProgress(1);
        const proposals = await Promise.all(MODELS.map(async (m) => {
            const txt = await callAPI(m, `Brief: ${s1}\n\nQuestion: ${msg}\n\nProvide your best answer (250 words).`, `Analytical mode.`);
            addTrace("Proposal", m.toUpperCase(), txt);
            return { model: m, text: txt };
        }));

        // STAGE 3: Critique
        updateProgress(2);
        const propSummary = proposals.map((p, i) => `Option ${i}: ${p.text.substring(0, 300)}...`).join("\n\n");
        const critiques = await Promise.all(MODELS.map(async (m) => {
            const txt = await callAPI(m, `Review these for: ${msg}\n\n${propSummary}\n\nIdentify 1 flaw and 1 strength for each.`, "Ruthless reviewer.");
            addTrace("Critique", m.toUpperCase(), txt);
            return { model: m, text: txt };
        }));

        // STAGE 4: Defense
        updateProgress(3);
        const cSummary = critiques.map((c, i) => `Peer ${i}: ${c.text.substring(0, 200)}`).join("\n");
        const defenses = await Promise.all(proposals.map(async (p) => {
            const txt = await callAPI(p.model, `Your Proposal: ${p.text.substring(0, 300)}\n\nCritiques:\n${cSummary}\n\nImprove your answer.`, "Refinement mode.");
            addTrace("Defense", p.model.toUpperCase(), txt);
            return { model: p.model, text: txt };
        }));

        // STAGE 5: Reconcile
        updateProgress(4);
        const dBlock = defenses.map(d => `[${d.model}]: ${d.text.substring(0, 400)}`).join("\n\n");
        const s5 = await callAPI("reasoner", `Experts refined positions on: ${msg}\n\n${dBlock}\n\nSynthesize ONE final protocol.`, "Senior Architect.");
        addTrace("Reconciliation", "DeepSeek Reasoner", s5);

        // STAGE 6: Polish
        updateProgress(5);
        const s6 = await callAPI("kimi", `Strip all meta-talk, markdown, and bolding from this text. Clinical prose only.\n\nText:\n${s5}`, "Senior Editor.");
        addTrace("Polish", "Kimi K2.5", s6);

        // Terminate
        updateProgress(6);
        document.getElementById('nexus-animation').style.display = 'none';
        document.getElementById('oracle-result').style.display = 'block';
        document.getElementById('oracle-output').textContent = s6;
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        document.getElementById('result-meta').textContent = `7/7 stages · 4 models · ${elapsed}s`;

    } catch (e) {
        console.error(e);
        alert("Oracle Error: " + e.message);
        document.getElementById('nexus-animation').style.display = 'none';
    }

    btn.disabled = false;
}

// --- Navigation & Misc ---

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

window.onload = () => switchTab('home');

// Expose to global scope for inline onclick handlers
window.runOracle = runOracle;
window.switchTab = switchTab;
window.toggleTrace = toggleTrace;
