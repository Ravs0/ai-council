import json
import logging
import concurrent.futures
import re
from api.llm_utils import LLMClient

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_json(res_text):
    try:
        # Strip markdown code fences that DeepSeek Reasoner wraps around JSON
        cleaned = re.sub(r'```(?:json)?\s*', '', res_text)
        cleaned = cleaned.strip()
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            return json.loads(json_match.group(0))
        # Handle lists if necessary
        list_match = re.search(r'\[[\s\S]*\]', cleaned)
        if list_match:
            return json.loads(list_match.group(0))
    except json.JSONDecodeError:
        pass
    return {}

class ResearchAgent:
    def __init__(self):
        self.client = LLMClient()
        # Fast model for planning/searching (saves ~60% of time)
        self.planning_model = "deepseek"
        self.search_model   = "deepseek"
        # Heavyweight reasoner only for the tournament and final report
        self.drafting_model  = "reasoner"

    # ==========================================
    # PHASE -1: INTENT EXTRACTION
    # ==========================================
    def extract_intent(self, query):
        prompt = f"""
            PHASE -1: QUESTION INTENT ENGINE
            Analyze this query: "{query}"

            Deconstruct the query using these four stages:
            1. Surface Parsing: (e.g., Normative, Ontological, Causal)
            2. Structural Analysis: Identify the anchor word and grammatical assumption.
            3. Intention Extraction: What is the unstated assumption?
            4. The God Voice: What is the question avoiding asking directly?

            Return strictly a JSON object:
            {{
                "surface_type": "...",
                "anchor_word": "...",
                "unstated_assumption": "...",
                "avoided_question": "...",
                "reframed_question": "..."
            }}
        """
        logging.info("Running Phase -1: Intent Extraction...")
        response = self.client.call_model(self.planning_model, prompt, system="You are the Intent Engine. Return valid JSON only.", max_tokens=1000)
        data = extract_json(response)
        if not data: data = {"reframed_question": query}
        return data

    # ==========================================
    # PHASE 0: PREMISE DECONSTRUCTION (SOCRATES)
    # ==========================================
    def deconstruct_premise(self, query, intent_data):
        prompt = f"""
            PHASE 0: PREMISE DECONSTRUCTION
            Original Premise: "{query}"
            Reframed Question: "{intent_data.get('reframed_question', '')}"
            Avoided Question: "{intent_data.get('avoided_question', '')}"

            Use [Step-by-Step Thinking] to break down the hidden assumptions, biases, and flaws.
            Then output a heavily deconstructed, maximally contentious, scientifically neutral "Deconstructed Premise" that sets the stage for a vicious 24-mind adversarial tournament.

            Return JSON:
            {{
                "socrates_critique": "...",
                "deconstructed_premise": "..."
            }}
        """
        logging.info("Running Phase 0: Premise Deconstruction (Socrates)...")
        response = self.client.call_model(self.planning_model, prompt, system="You are Socrates. Return valid JSON.", max_tokens=800)
        data = extract_json(response)
        if not data: data = {"deconstructed_premise": query}
        return data

    # ==========================================
    # PHASE 1A: COLLECTIVE SHADOW PROTOCOL
    # ==========================================
    def shadow_protocol(self, deconstructed_premise):
        prompt = f"""
            PHASE 1A: COLLECTIVE SHADOW PROTOCOL
            Premise: "{deconstructed_premise}"

            Identify the Dominant Paradigm, its Core Assumptions, the God Voice Risk (what 24 randomly selected minds would converge around in an unchallenging manner), and assign a "Shadow-Breaker" persona from history/academia whose specific worldview would attack the unstated assumptions of that paradigm.

            Return JSON:
            {{
                "dominant_paradigm": "...",
                "core_assumptions": "...",
                "god_voice_risk": "...",
                "shadow_breaker_persona": "...",
                "shadow_breaker_rationale": "..."
            }}
        """
        logging.info("Running Phase 1A: Collective Shadow Protocol...")
        response = self.client.call_model(self.planning_model, prompt, system="You are the Shadow Protocol. Return valid JSON.", max_tokens=800)
        return extract_json(response)

    # ==========================================
    # PRE-FLIGHT: SOURCES & SIP
    # ==========================================
    def plan_research(self, deconstructed_premise, jurisdiction):
        prompt = f"""
            You are a Senior Research Strategist. 
            Analyze this deconstructed premise: "{deconstructed_premise}" for jurisdiction: "{jurisdiction}".
            Break this issue down into 3-5 distinct, mutually exclusive search vectors.
            Return JSON: {{"topics": ["..."], "rationale": "..."}}
        """
        logging.info("Generating research plan...")
        response = self.client.call_model(self.planning_model, prompt, system="Return valid JSON only.", max_tokens=800)
        data = extract_json(response)
        if data and data.get("topics"):
            return data
        # Fallback: generate sensible short search topics from the premise
        logging.warning("Plan parsing failed. Generating fallback search topics from premise keywords.")
        words = deconstructed_premise.split()
        short = ' '.join(words[:15]) if len(words) > 15 else deconstructed_premise
        return {"topics": [
            f"AI agent liability contract formation {jurisdiction}",
            f"electronic agent UETA ESIGN contract law",
            f"strict liability vs negligence autonomous systems",
            f"agency law principal liability for AI actions",
            f"academic debate AI legal personhood"
        ]}

    def perform_search(self, topic, jurisdiction):
        prompt = f"""
            PERFORM FOCUSED LEGAL RESEARCH.
            Search Focus: "{topic}" (Jurisdiction: "{jurisdiction}")
            GOAL: Find 3-5 high-quality legal sources/citations (cases, statutes, core academic texts).
            Return JSON format: {{"sources": [{{"name": "...", "citation": "...", "principle": "..."}}]}}
        """
        logging.info(f"Searching topic: {topic}")
        response = self.client.call_model(self.search_model, prompt, system="Return valid JSON only.", max_tokens=1500)
        data = extract_json(response)
        return data.get("sources", []) if data else []

    def interrogate_source(self, source, query):
        prompt = f"""
            SOURCE INTERROGATION PROTOCOL (SIP)
            Target Query: "{query}"
            Source: "{source.get('name')} - {source.get('citation')} - {source.get('principle')}"

            Evaluate this source strictly:
            1. Positional Bias: Institutional standing/funding bias.
            2. Structural Blind Spot: Architecturally incapable of noticing.
            3. The Challenger: A credible opponent to its core finding.

            Return JSON:
            {{ "positional_bias": "...", "structural_blind_spot": "...", "challenger": "...", "evidence_level": 1-5 }}
        """
        logging.info(f"Interrogating source: {source.get('name', 'Unknown')}")
        response = self.client.call_model(self.search_model, prompt, system="Return valid JSON only.", max_tokens=800)
        interrogation = extract_json(response)
        if interrogation:
            source.update(interrogation)
            source["sip_status"] = "Success"
        else:
            source["sip_status"] = "Failed"
        return source

    # ==========================================
    # PHASE 1B: ROSTER & PARALLEL GENERATION
    # ==========================================
    def select_roster(self, deconstructed_premise, shadow_data):
        prompt = f"""
            PHASE 1B: DYNAMIC ROSTER SELECTION
            Deconstructed Premise: "{deconstructed_premise}"
            Shadow-Breaker Assigned: "{shadow_data.get('shadow_breaker_persona')}"

            Draft the 24 most relevant intellectual heavyweights/historical personas to debate this thesis across 8 domains (Law, Economics, Philosophy, Sociology, Tech, Science, History, Psychology). Include the Shadow-Breaker. 

            Return JSON list:
            {{ "roster": [{{"name": "...", "domain": "...", "core_axiom": "..."}}] }} (exactly 24 items)
        """
        logging.info("Selecting dynamically drafted 24-mind roster...")
        response = self.client.call_model(self.planning_model, prompt, system="Return exact JSON only. No markdown, no explanation.", max_tokens=3000)
        data = extract_json(response)
        roster = data.get("roster", []) if isinstance(data, dict) else []
        if len(roster) >= 10:
            return roster[:24]
        
        # Hardcoded fallback roster from ROSTER.md (24 thinkers across 8 domains)
        logging.warning("Roster LLM parse failed. Using hardcoded fallback roster.")
        return [
            {"name": "Antonin Scalia", "domain": "Law", "core_axiom": "Law means exactly what its text said when enacted."},
            {"name": "Ruth Bader Ginsburg", "domain": "Law", "core_axiom": "The Constitution must evolve to dismantle structural inequalities."},
            {"name": "Richard Posner", "domain": "Law", "core_axiom": "Legal rules should maximize economic efficiency."},
            {"name": "Milton Friedman", "domain": "Economics", "core_axiom": "Free markets are the most efficient allocators."},
            {"name": "Ha-Joon Chang", "domain": "Economics", "core_axiom": "Free markets are a myth; all markets are structured by state rules."},
            {"name": "Karl Marx", "domain": "Economics", "core_axiom": "Capitalism extracts surplus value from labor until structural contradictions force revolution."},
            {"name": "Norbert Wiener", "domain": "Technology", "core_axiom": "Systems are governed by feedback loops."},
            {"name": "Nassim Nicholas Taleb", "domain": "Technology", "core_axiom": "Systems must be antifragile — gaining from disorder."},
            {"name": "Nick Bostrom", "domain": "Technology", "core_axiom": "Misaligned AI is the absolute existential threat."},
            {"name": "Peter Singer", "domain": "Philosophy", "core_axiom": "Morality demands impartial maximization of preference satisfaction."},
            {"name": "Immanuel Kant", "domain": "Philosophy", "core_axiom": "Act only on maxims that can be universalized."},
            {"name": "Hannah Arendt", "domain": "Philosophy", "core_axiom": "Evil thrives in bureaucratic thoughtlessness."},
            {"name": "Max Weber", "domain": "Sociology", "core_axiom": "Modernity is defined by the iron cage of rational calculation."},
            {"name": "Michel Foucault", "domain": "Sociology", "core_axiom": "Truth is a product of power."},
            {"name": "Bruno Latour", "domain": "Sociology", "core_axiom": "Non-humans possess agency and shape social networks."},
            {"name": "Daniel Kahneman", "domain": "Psychology", "core_axiom": "Human decision-making is fundamentally flawed by heuristics."},
            {"name": "B.F. Skinner", "domain": "Psychology", "core_axiom": "Behavior is solely determined by environmental reinforcement."},
            {"name": "Frantz Fanon", "domain": "Psychology", "core_axiom": "Colonialism inflicts structural sociogeny."},
            {"name": "Ibn Khaldun", "domain": "History", "core_axiom": "Civilizations rise and fall based on social cohesion."},
            {"name": "Henry Kissinger", "domain": "History", "core_axiom": "Order must take precedence over justice."},
            {"name": "Aimé Césaire", "domain": "History", "core_axiom": "Colonialism is a boomerang that rots the colonizer."},
            {"name": "Karl Popper", "domain": "Science", "core_axiom": "A theory is only scientific if it can be proven false."},
            {"name": "Thomas Kuhn", "domain": "Science", "core_axiom": "Science operates in paradigms that shift through revolutions."},
            {"name": "Alan Turing", "domain": "Science", "core_axiom": "Any system that can simulate logic gates can compute anything computable."}
        ]

    def generate_persona_argument(self, persona, deconstructed_premise, sources):
        sources_text = json.dumps(sources, indent=2)
        prompt = f"""
            PHASE 1: CONCURRENT PERSONA GENERATION
            You are the Sovereign Mind of {persona.get('name')} (Domain: {persona.get('domain')}).
            Core Axiom: {persona.get('core_axiom')}
            
            Deconstructed Premise: "{deconstructed_premise}"
            SIP-INTERROGATED AUTHORITY AVAILABLE:
            {sources_text}

            Execute CEV Pipeline:
            1. CEV Verdict: Agree / Disagree / Reframe.
            2. Core Argument: 2-3 sentences max.
            3. Evidence Block: Cite at least 1-2 real sources from the authority list, noting methodology or bias/challenger.
            4. Fatal Assumption Identified: Hidden flaw in the premise.
            5. Predicted Weakness: What other personas will attack about this.

            Return JSON:
            {{
                "name": "{persona.get('name')}",
                "verdict": "...",
                "core_argument": "...",
                "evidence_block": "...",
                "fatal_assumption": "...",
                "predicted_weakness": "..."
            }}
        """
        logging.info(f"Generating argument for persona: {persona.get('name')}")
        response = self.client.call_model(self.search_model, prompt, system="You are the specified Persona. Return valid JSON only.", max_tokens=1000)
        data = extract_json(response)
        return data if data else {"name": persona.get('name'), "error": "Generation failed"}

    # ==========================================
    # PHASE 2 & 3: TOURNAMENT & JUDGMENT
    # ==========================================
    def run_tournament(self, deconstructed_premise, arguments):
        args_text = json.dumps(arguments, indent=2)
        prompt = f"""
            PHASE 2 & 3: ADVERSARIAL TOURNAMENT & JUDGMENT

            Deconstructed Premise: "{deconstructed_premise}"
            24 Persona Arguments:
            {args_text}

            Act as the Chief Justice. Synthesize the 4-round tournament (Domain Internals -> Quarterfinals -> Semifinals -> The Final).
            You must document:
            1. The Finalist vs. The Challenger (the final 2 surviving arguments).
            2. Ghost Notes: The strongest standalone citations or points from defeated personas that survive as caveats.
            3. Majority Opinion: The empirically strongest, conceptually robust synthesis.
            4. Strongest Dissent: The irreducible objection from the Challenger.
            5. Evidence Scorecard & Systemic Blind Spots.

            Return JSON:
            {{
                "ghost_notes": ["...", "..."],
                "majority_opinion": "...",
                "strongest_dissent": "...",
                "evidence_scorecard": "...",
                "blind_spots": "..."
            }}
        """
        logging.info("Running Phase 2 & 3: Adversarial Tournament & Chief Justice Judgment...")
        response = self.client.call_model(self.drafting_model, prompt, system="You are the Chief Justice. Return valid JSON only.", max_tokens=3000)
        return extract_json(response)

    # ==========================================
    # PHASE 4: FINAL LATOURIAN REPORT
    # ==========================================
    def draft_final_report(self, query, deconstructed_premise, judgment, sources):
        source_text = json.dumps(sources, indent=2)
        judgment_text = json.dumps(judgment, indent=2)
        
        prompt = f"""
            PHASE 4: FINAL CONCLUSION REPORT (LATOURIAN)
            
            Target Premise: "{query}"
            Deconstructed Premise: "{deconstructed_premise}"
            
            Tournament Judgment:
            {judgment_text}

            SIP Sources:
            {source_text}
            
            INSTRUCTIONS - LATOURIAN ANTI-REDUCTIONISM RULE:
            You must map the non-human and systemic interdependencies (the cascade effect) of your answer. No single human/actor exists in isolation. Describe the interconnected 'Actor-Network Theory' config.
            
            STRUCTURE AS A SINGLE AUTONOMOUS PROSE DOCUMENT (600-800 Words):
            Include narrative flow: The Premise, The Landscape of Disagreement, The Strongest Case For, The Decisive Rebuttal, The Irreducible Dissent, Systemic Implications, Open Questions.
            
            NO JSON. NO BULLET POINTS. Use Ghost Notes as inline citations. Include explicit [GAP: ...] or [WEAK LINK: ...] tags to enforce the Anti-Bluff Mechanism where proof is missing.
        """
        logging.info("Drafting Phase 4: Final Latourian Conclusion Report...")
        return self.client.call_model(self.drafting_model, prompt, system="You are a senior adversarial legal synthesis engine.", max_tokens=4000)

    # ==========================================
    # MAIN EXECUTION PIPELINE
    # ==========================================
    def run(self, query, jurisdiction="United States"):
        # 1. Phase -1: Intent
        intent_data = self.extract_intent(query)
        
        # 2. Phase 0: Deconstruction
        socrates_data = self.deconstruct_premise(query, intent_data)
        deconstructed_premise = socrates_data.get("deconstructed_premise", query)
        logging.info(f"Deconstructed Premise: {deconstructed_premise}")

        # 3. Phase 1A: Shadow Protocol
        shadow_data = self.shadow_protocol(deconstructed_premise)

        # 4. Pre-Flight: Plan & Search
        plan = self.plan_research(deconstructed_premise, jurisdiction)
        topics = plan.get("topics", [])
        
        raw_sources = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_topic = {executor.submit(self.perform_search, topic, jurisdiction): topic for topic in topics}
            for future in concurrent.futures.as_completed(future_to_topic):
                data = future.result()
                if isinstance(data, list): raw_sources.extend(data)

        # 5. Pre-Flight: SIP Interrogation
        logging.info(f"Collected {len(raw_sources)} raw sources. Initiating SIP phase...")
        sip_sources = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_src = {executor.submit(self.interrogate_source, src, deconstructed_premise): src for src in raw_sources}
            for future in concurrent.futures.as_completed(future_to_src):
                sip_sources.append(future.result())

        # 6. Phase 1B: Roster Selection
        roster = self.select_roster(deconstructed_premise, shadow_data)
        if not roster: 
            logging.error("Failed to generate roster. Falling back to simple roster logic.")
            roster = [{"name": "Generic Scholar", "domain": "Law", "core_axiom": "Reason"}]

        # 7. Phase 1C: Parallel Generation (24 Minds)
        logging.info("Initiating 24-persona concurrent generation...")
        arguments = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # We pass sip_sources so they can use the interrogated biases
            future_to_persona = {executor.submit(self.generate_persona_argument, persona, deconstructed_premise, sip_sources): persona for persona in roster}
            for future in concurrent.futures.as_completed(future_to_persona):
                arguments.append(future.result())

        # 8. Phase 2 & 3: Tournament & Judgment
        judgment = self.run_tournament(deconstructed_premise, arguments)

        # 9. Phase 4: Final Latourian Report
        final_report = self.draft_final_report(query, deconstructed_premise, judgment, sip_sources)
        return final_report

if __name__ == "__main__":
    agent = ResearchAgent()
    q = "Liability of AI agents in contract formation"
    print(agent.run(q))
