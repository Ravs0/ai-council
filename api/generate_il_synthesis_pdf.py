import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, KeepTogether, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT

def process_text(text):
    text = text.replace("—", ", ")
    text = text.replace("--", ", ")
    return text

def build_report(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=60, leftMargin=60,
                            topMargin=60, bottomMargin=60)

    styles = getSampleStyleSheet()

    # == TYPEFACE & STYLES ==
    # Legal Journal Style: Times-Roman for body, structured Helvetica for headers.
    
    styles.add(ParagraphStyle(
        name='JournalTitle',
        fontName='Times-Bold',
        fontSize=26,
        leading=32,
        spaceAfter=20,
        textColor=colors.HexColor('#0F2A3F'),
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='JournalSubtitle',
        fontName='Times-Italic',
        fontSize=14,
        leading=18,
        spaceAfter=40,
        textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        spaceBefore=30,
        spaceAfter=15,
        textColor=colors.HexColor('#1E3D59'),
        borderWidth=0,
        borderPadding=0
    ))

    styles.add(ParagraphStyle(
        name='DomainHeader',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        spaceBefore=25,
        spaceAfter=10,
        textColor=colors.HexColor('#8B1E1E'), # Crimson touch
    ))

    styles.add(ParagraphStyle(
        name='BodyJournal',
        fontName='Times-Roman',
        fontSize=11,
        leading=16,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        textColor=colors.black
    ))
    
    styles.add(ParagraphStyle(
        name='BodyJournalBold',
        fontName='Times-Bold',
        fontSize=11,
        leading=16,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        textColor=colors.black
    ))

    styles.add(ParagraphStyle(
        name='QuoteBlock',
        fontName='Times-Italic',
        fontSize=11,
        leading=16,
        leftIndent=25,
        rightIndent=25,
        spaceBefore=15,
        spaceAfter=15,
        textColor=colors.HexColor('#2C3E50'),
        alignment=TA_JUSTIFY
    ))

    styles.add(ParagraphStyle(
        name='PremiseBlock',
        fontName='Times-BoldItalic',
        fontSize=13,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0F2A3F')
    ))

    Story = []

    # ================= COVER =================
    Story.append(Spacer(1, 1.5*inch))
    img_path = "/Users/basilikax/.gemini/antigravity/brain/cf0f0f18-d421-4115-b8d6-0bf83ca2d17e/international_law_cover_1771762776467.png"
    if os.path.exists(img_path):
        img = Image(img_path, width=4*inch, height=4*inch)
        Story.append(img)
    Story.append(Spacer(1, 0.5*inch))
    
    Story.append(Paragraph("ADVERSARIAL SYNTHESIS", styles['JournalSubtitle']))
    Story.append(Paragraph("The Ontological Crisis of International Law", styles['JournalTitle']))
    Story.append(HRFlowable(width="80%", thickness=1, color=colors.HexColor('#0F2A3F'), spaceBefore=20, spaceAfter=20, hAlign='CENTER'))
    Story.append(Paragraph("A Comprehensive 24-Lens Examination of State Compliance and Sovereign Authority", styles['JournalSubtitle']))
    
    Story.append(PageBreak())

    # ================= TARGET PREMISE =================
    Story.append(Paragraph("I. TARGET PREMISE", styles['SectionHeader']))
    
    premise_data = [[Paragraph(process_text('"Given that states never follow rules of international law, do such rules even exist."'), styles['PremiseBlock'])]]
    t = Table(premise_data, colWidths=['100%'])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F6F8')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#B0C4DE')),
        ('TOPPADDING', (0,0), (-1,-1), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    Story.append(t)
    Story.append(Spacer(1, 20))


    # ================= PRE-FLIGHT: SOURCE REGISTRY =================
    Story.append(Paragraph("II. SOURCE REGISTRY & LEGAL LITERATURE", styles['SectionHeader']))
    Story.append(Paragraph(process_text("Directly On-Point (Primary Sources)"), styles['DomainHeader']))
    
    sources = [
        "<b>1. Austin, J. (1832)</b>: <i>The Province of Jurisprudence Determined</i>. The foundational attack: law is a command of a sovereign backed by a sanction. Since there is no global sovereign and no enforceable sanction, international law is not law but positive morality, mere opinion among nations.",
        "<b>2. Hart, H.L.A. (1961)</b>: <i>The Concept of Law</i>, Chapter X. Concedes that international law lacks a centralized legislature and centralized sanctions, but argues it is still a primitive but real legal system operating through decentralized social pressure.",
        "<b>3. ICJ Statute, Article 38(1) (1945)</b>. The formal enumeration of the sources of international law: treaties, custom, general principles, and subsidiary judicial decisions.",
        "<b>4. <i>Nicaragua v United States of America</i> [1986] ICJ Reports 14</b>. The ICJ ruled that the United States violated international law by mining Nicaraguan harbours. The U.S. refused to comply and withdrew from ICJ compulsory jurisdiction, the single most devastating empirical exhibit for the premise."
    ]
    for src in sources:
        Story.append(Paragraph(process_text(src), styles['BodyJournal']))

    Story.append(Paragraph(process_text("Empirical Data & Competing Academic Positions"), styles['DomainHeader']))
    sources2 = [
        "<b>5. Hathaway, O. (2002)</b>: <i>Do Human Rights Treaties Make a Difference?</i>, 111 Yale L.J. 1935. Empirical study finding that ratification of human rights treaties is not correlated with improved human rights practices, and in some cases, countries with worse records ratify more treaties as a form of performative legitimacy.",
        "<b>6. Chayes, A. & Chayes, A.H. (1993)</b>: <i>On Compliance</i>, 47 Int'l Org. 175. Counter-study arguing that the compliance rate with international law is actually remarkably high (estimated 90%+), but this goes unnoticed because violations are dramatic and compliance is invisible.",
        "<b>7. Koskenniemi, M. (2005)</b>: <i>From Apology to Utopia</i>. The definitive critical theory of international law: all international legal arguments oscillate between apology (justifying state power) and utopia (aspiring to norms no state follows).",
        "<b>8. Henkin, L. (1979)</b>: <i>How Nations Behave: Law and Foreign Policy</i>. The classic rebuttal: 'Almost all nations observe almost all principles of international law and almost all of their obligations almost all of the time.'"
    ]
    for src in sources2:
        Story.append(Paragraph(process_text(src), styles['BodyJournal']))

    # ================= PHASE 1: THE 24 LENSES =================
    Story.append(PageBreak())
    Story.append(Paragraph("III. PHASE 1: PARALLEL LENS GENERATION", styles['SectionHeader']))
    Story.append(Paragraph(process_text("Twenty-four sovereign minds, representing specific domains of human intellect, examine the premise rigorously to identify fatal flaws and structural truths."), styles['BodyJournal']))

    def create_lens_block(num, name, verdict, core_arg, evidence, fatal_assumption, weakness):
        content = []
        content.append(Paragraph(f"<b>{num}. {name}</b>", styles['BodyJournalBold']))
        
        # We will put the rest in a slightly indented, shaded table block to look like a legal annotation
        details = f"""
        <b>Verdict:</b> <font color='#8B1E1E'><b>{process_text(verdict)}</b></font><br/>
        <b>Core Argument:</b> {process_text(core_arg)}<br/>
        <b>Evidence Block:</b> {process_text(evidence)}<br/>
        <b>Fatal Assumption Identified:</b> {process_text(fatal_assumption)}<br/>
        <b>Predicted Weakness:</b> {process_text(weakness)}
        """
        p = Paragraph(details, styles['BodyJournal'])
        
        t = Table([[p]], colWidths=['100%'])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FDFEFE')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#D5D8DC')),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        
        return KeepTogether([content[0], Spacer(1, 5), t, Spacer(1, 15)])

    # Domain 1
    Story.append(Paragraph("DOMAIN 1: LAW & GOVERNANCE", styles['DomainHeader']))
    Story.append(create_lens_block(
        "1", "Antonin Scalia (Textualist)", "Reframe.", 
        "The rules exist as text, treaties are signed and published. However, law requires enforceability. If a statute is on the books but no court can compel compliance, it functions as aspiration. International law is text without teeth.", 
        "[Case] Nicaragua v USA (1986). The U.S. ignored a binding judgment without consequence. [Primary] Austin (1832). No sovereign, no sanction, no law.", 
        "Assumes 'never follow' rather than analyzing the presence of institutional compulsion.", 
        "Confuses 'law' with 'effective enforcement'."
    ))
    Story.append(create_lens_block(
        "2", "Ruth Bader Ginsburg (Egalitarian)", "Disagree.", 
        "International law exists and has materially changed the world for women, refugees, and victims of genocide. CEDAW and the Rome Statute have restructured domestic legal systems. Erasing these rules because great powers violate them erases real protections.", 
        "[Academic] Henkin (1979). Nations observe almost all principles almost all of the time. [Statute] ICJ Statute, Art. 38(1).", 
        "Rejects the factual claim that states never follow the law.", 
        "Areas of highest compliance are often those based on mere self-interest, not legal normative force."
    ))
    Story.append(create_lens_block(
        "3", "Carl Schmitt (Sovereign Theorist)", "Agree.", 
        "International law is the language powerful states use to dress their interests in moral costume. The moment any rule becomes inconvenient for the hegemon, it is suspended. Sovereign is he who decides on the exception.", 
        "[Case] Nicaragua v USA (1986). The U.S. vetoed enforcement, proving the sovereign decides when law applies. [Academic] Koskenniemi (2005).", 
        "Rejects the liberal illusion of a rules-based order as anything more than hegemon narrative.", 
        "Reduces all law to pure power, eliminating any normative basis for condemnation."
    ))

    # Domain 2
    Story.append(Paragraph("DOMAIN 2: ECONOMICS & MARKETS", styles['DomainHeader']))
    Story.append(create_lens_block(
        "4", "Milton Friedman (Market Libertarian)", "Reframe.", 
        "International law exists where it serves mutual economic self-interest. WTO law and investment treaties are followed because non-compliance triggers retaliation. The law that 'doesn't exist' is the purely moral kind.", 
        "[Empirical] Chayes & Chayes (1993). Compliance is high precisely in trade law. [Empirical] Hathaway (2002).", 
        "Rejects the premise as too broad, it ignores self-enforcing economic rules.", 
        "Reduces all legal obedience to financial incentive."
    ))
    Story.append(create_lens_block(
        "5", "John Maynard Keynes (Interventionist)", "Disagree.", 
        "International law is the institutional architecture of the post-war economic order. The Bretton Woods system and WTO are the infrastructure of global GDP. Denying them is denying the system itself.", 
        "[Empirical] Chayes & Chayes (1993). The compliance evidence is strongest in precisely the economic institutions he helped create.", 
        "Rejects defining international law narrowly as only humanitarian or security law.", 
        "Proves only that powerful states follow rules when profitable."
    ))
    Story.append(create_lens_block(
        "6", "Ha-Joon Chang (Institutional Economist)", "Agree.", 
        "International law exists as a weapon of the powerful. It forces developing nations to open markets while rich nations maintain subsidies. It exists the way colonial law existed, for the benefit of the colonizer.", 
        "[Academic] Koskenniemi (2005). Apology logic justifies the powerful. [Empirical] Hathaway (2002).", 
        "Recognizes rules exist, but only to regulate the weak.", 
        "Overgeneralizes, some rules genuinely constrain the powerful."
    ))

    # Domain 3
    Story.append(Paragraph("DOMAIN 3: TECHNOLOGY & SYSTEMS", styles['DomainHeader']))
    Story.append(create_lens_block(
        "7", "Norbert Wiener (Cybernetics)", "Reframe.", 
        "Confuses centralized enforcement with existence. In cybernetics, it operates as a decentralized feedback system using reputational and diplomatic signals to influence state behavior without a central controller.", 
        "[Academic] Chayes & Chayes (1993). Managerial compliance treats law as feedback. [Primary] Hart (1961).", 
        "Rejects the Austinian assumption that only centralized command equates to law.", 
        "Feedback systems fail catastrophically against overly powerful deviant actors like the permanent five."
    ))
    Story.append(create_lens_block(
        "8", "Nassim Nicholas Taleb (Antifragility)", "Agree.", 
        "International law is a fragile fair-weather fiction. It shatters the moment a genuine crisis occurs, such as major state conflict. A system that works only when it isn't needed is not a system at all.", 
        "[Case] Nicaragua v USA (1986). System collapsed when tested by a superpower. [Academic] Koskenniemi (2005).", 
        "Rejects compliance statistics as survivorship bias.", 
        "Dismisses the stabilizing effect of law in thousands of mundane interactions."
    ))
    Story.append(create_lens_block(
        "9", "Nick Bostrom (Existential Risk)", "Disagree.", 
        "Existential threats, nuclear, AI, climate, are by definition unsolvable by single states. International law is the only framework operating at scale. Declaring it non-existent is civilizational suicide.", 
        "[Statute] ICJ Statute, Art. 38(1). The architecture exists, capacity must be built.", 
        "Rejects the nihilist conclusion; the existence of the framework is a precondition for survival.", 
        "Confuses 'should exist' with 'does exist'."
    ))

    # Provide summary blocks for the remaining constraints to save space, but keeping the thorough academic tone.
    Story.append(PageBreak())
    Story.append(Paragraph("DOMAIN 4: PHILOSOPHY & ETHICS", styles['DomainHeader']))
    Story.append(create_lens_block(
        "10", "Peter Singer (Utilitarian)", "Disagree.", 
        "Existence in a positivist sense is less important than net human suffering reduction. If the Geneva Conventions save even one civilian, the rules have consequentialist normative existence.", 
        "[Academic] Henkin (1979). Daily compliance prevents massive aggregate suffering.", 
        "Rejects that existence means perfect enforcement.", 
        "Allows massive violations as long as aggregate utility is positive."
    ))
    Story.append(create_lens_block(
        "11", "Immanuel Kant (Deontological)", "Disagree.", 
        "The rules exist as moral imperatives independent of state compliance. A categorical prohibition on genocide is not contingent. A moral law violated a thousand times retains its full binding force. Murder occurs, yet murder is illegal.", 
        "[Primary] ICJ Statute, Art. 38(1) (general principles). Kant's Perpetual Peace.", 
        "Rejects the empiricist reduction of existence to obedience.", 
        "Provides zero institutional mechanism for real-world enforcement."
    ))
    Story.append(create_lens_block(
        "12", "Hannah Arendt (Political Evil)", "Reframe.", 
        "International law exists as the juridical memory of humanity's worst failures. To say it doesn't exist because states violate it is to say the lessons of Auschwitz can be unlearned.", 
        "[Institutional] Rome Statute / ICC. Exists because states cannot be trusted. [Academic] Henkin (1979).", 
        "Rejects realpolitik dismissal; the law constitutes our scar tissue against evil.", 
        "Emotionally devastating but practically weak regarding actual state deterrence."
    ))

    # Combine sociological & psychological lenses concisely but professionally.
    Story.append(Paragraph("DOMAIN 5: SOCIOLOGY & PSYCHOLOGY", styles['DomainHeader']))
    
    soc_text = "<b>Weber (Legitimation System):</b> International law exists as a discursive requirement, violators invoke it to justify their actions. <b>Foucault (Constitutive Discourse):</b> International law produces the categories of sovereignty and statehood; it constitutes the very fields it allegedly fails to regulate. <b>Sen (Capabilities):</b> It provides an argumentative framework for oppressed peoples to articulate rights. <b>Kahneman (Cognitive Realism):</b> The premise relies on availability bias, ignoring thousands of invisible acts of daily compliance. <b>Skinner (Behaviorism):</b> States follow reinforcement schedules mapped by international treaties. <b>Fanon (Structural Psychology):</b> The rules exist, but only to enforce colonial architecture against the powerless."
    Story.append(Paragraph(process_text(soc_text), styles['BodyJournal']))

    Story.append(Paragraph("DOMAIN 6: HISTORY & EPISTEMOLOGY", styles['DomainHeader']))
    hist_text = "<b>Khaldun (Cyclical Decay):</b> International law is the code of a declining Western civilizational order. <b>Kissinger (Realpolitik):</b> The rules exist as tools of statecraft deployed strategically by hegemonies. <b>Césaire (Anti-Colonial):</b> The 'universal' rules were designed by conquerors to regulate the conquered. <b>Popper (Open Society):</b> The absolutist premise is empirically falsifiable by a single act of compliance. <b>Kuhn (Scientific Paradigms):</b> We are in a paradigm crisis where the Westphalian model is failing under anomalies. <b>Meadows (Systems):</b> The system produces order imperfectly, and examining it via binary 'existence' targets the wrong leverage point."
    Story.append(Paragraph(process_text(hist_text), styles['BodyJournal']))


    # ================= PHASE 2: THE GALA =================
    Story.append(PageBreak())
    Story.append(Paragraph("IV. PHASE 2: ADVERSARIAL TOURNAMENT", styles['SectionHeader']))
    Story.append(Paragraph(process_text("In the cross-domain quarterfinals and semifinals, the empiricists collided violently with the critical structuralists. The most profound syntheses emerged when moral imperatives were subjected to power-dynamics audits."), styles['BodyJournal']))

    Story.append(Paragraph("The Quarterfinals", styles['DomainHeader']))
    qf_text = "Kant argued that the rules exist as moral imperatives regardless of compliance, while Kahneman proved that compliance is actually empirically high. Together they formed a devastating two-pronged attack: the premise is both morally incoherent (violation does not negate a rule) and empirically false (compliance is the statistical norm). Conversely, Foucault structurally aligned with Césaire to note that while the rules 'exist', they exist to constitute inherently asymmetrical, colonial power structures."
    Story.append(Paragraph(process_text(qf_text), styles['BodyJournal']))

    Story.append(Paragraph("The Final Hearing: The Grand Synthesis vs. The Realist Bloc", styles['DomainHeader']))
    fh_text = "<b>The Finalist (Grand Synthesis):</b> The premise is factually false (Chayes), cognitively biased (Kahneman), and morally corrupt (Kant). Systemically, international law operates as a real, decentralized coordination mechanism (Wiener/Meadows) that literally constitutes the actors within it (Foucault).<br/><br/><b>The Challenger (Realist Bloc - Schmitt/Taleb/Fanon):</b> The Finalist measures compliance only where states have zero incentive to violate. Against any actor powerful enough to matter, the system collapses (e.g., Nicaragua v. USA). The system is not broken; it is designed to discipline the weak and immunize the permanent five."
    Story.append(Paragraph(process_text(fh_text), styles['BodyJournal']))

    # ================= PHASE 3: THE JUDGMENT =================
    Story.append(Paragraph("V. THE JUDGMENT", styles['SectionHeader']))
    
    Story.append(Paragraph(process_text("MAJORITY OPINION"), styles['DomainHeader']))
    maj_text = "The rules of international law exist. The premise's factual assertion, that states 'never' follow them, is empirically false. Based on overwhelming evidence (Henkin, Chayes), the vast majority of international legal obligations are observed the vast majority of the time. The premise is a cognitive product of availability bias: dramatic violations are vivid, while routine compliance (trade, aviation, diplomacy) is invisible. Furthermore, international law does not merely regulate states; it constitutes them. Without its legal concepts of sovereignty and territorial integrity, the entities that violate it would not exist."
    Story.append(Paragraph(process_text(maj_text), styles['BodyJournal']))
    
    Story.append(Paragraph(process_text("STRONGEST DISSENT"), styles['DomainHeader']))
    dis_text = "The Challenger's irreducible objection demolishes the compliance statistics: Nicaragua v United States (1986) proves that when a great power is subjected to a binding judgment, it can refuse compliance, veto enforcement, and withdraw from jurisdiction with zero legal consequence. Measuring compliance with postal treaties is measuring honesty only when there is nothing to gain from lying. The truly devastating reformulation of the premise is not 'do the rules exist?' but 'do the rules exist for the powerful?', and the empirical answer is No."
    Story.append(Paragraph(process_text(dis_text), styles['BodyJournal']))


    # ================= PHASE 4: FINAL CONCLUSION REPORT =================
    Story.append(PageBreak())
    Story.append(Paragraph("VI. FINAL CONCLUSION REPORT", styles['SectionHeader']))

    conc1 = "The question of whether international law 'exists' given persistent state non-compliance is not merely an academic exercise in positivist jurisprudence, it is a fundamental interrogation of whether normative order is possible beyond the nation-state. The premise embeds a factual claim and derives an ontological conclusion. Both the claim and the conclusion, upon rigorous adversarial examination, prove to be substantially wrong, but the question itself exposes a genuine and devastating structural pathology in the international legal order."
    Story.append(Paragraph(process_text(conc1), styles['BodyJournal']))

    conc2 = "The strongest defense of international law's existence rests on three independent pillars. First, the factual premise is wrong: compliance is empirically overwhelming, concentrated in the vast, invisible machinery of trade, diplomacy, navigation, postal services, and treaty obligations that make globalized civilization operational. Second, the conceptual premise is incoherent: a rule violated does not cease to exist, just as the prohibition on murder is not negated by the occurrence of murder. Third, and most powerfully, international law is not merely a set of rules imposed upon states, it constitutes states. To deny the existence of international law is to deny the conceptual architecture of the very system within which the question is asked."
    Story.append(Paragraph(process_text(conc2), styles['BodyJournal']))

    conc3 = "Nevertheless, the most powerful surviving dissent, anchored by post-colonial and realist critique, remains genuinely unanswered. History proves that when a great power is subjected to a binding ICJ judgment, it can refuse compliance and veto enforcement with zero legal consequence. The compliance statistics measure obedience only in domains where powerful states had no incentive to deviate. Thus, the rules exist, but the Security Council veto and the structural impunity of permanent member nations demonstrate a system designed to discipline the weak while immunizing the strong."
    Story.append(Paragraph(process_text(conc3), styles['BodyJournal']))

    conc4 = "What this adversarial examination reveals systemically is that the international legal order suffers from a fundamental feedback asymmetry. It operates as a functioning decentralized coordination system for the vast majority of routine interactions, but its corrective feedback mechanisms collapse catastrophically when the deviant actor is powerful enough to absorb the diplomatic and reputational costs of non-compliance. This is not a failure of international law as a concept, it is a specific architectural deficiency in the enforcement design inherited from the 1945 settlement."
    Story.append(Paragraph(process_text(conc4), styles['BodyJournal']))
    
    Story.append(Paragraph("Actionable Open Queries", styles['DomainHeader']))
    query_text = "1. What is the empirical compliance rate when disaggregated entirely by the military and economic power index of the state in question?<br/>2. Are there historical analogies of decentralized legal systems that successfully constrained apex predators without centralized policing?<br/>3. As non-state actors operating beyond Westphalian structures accelerate, does this critique become literally true for emerging domains of power?"
    Story.append(Paragraph(process_text(query_text), styles['BodyJournal']))

    # Build the pdf
    doc.build(Story)

if __name__ == '__main__':
    build_report('/Users/basilikax/Library/Containers/com.apple.BKAgentService/Data/Documents/iBooks/Books/Legal/international_law_synthesis_full.pdf')
