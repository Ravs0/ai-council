import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image, PageBreak, KeepTogether, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

def str_to_color(hex_str):
    return colors.HexColor(hex_str)

def draw_border(canvas, doc):
    canvas.saveState()
    canvas.setLineWidth(3)
    # Red, Blue, Green pattern
    # Top border - Red
    canvas.setStrokeColor(colors.red)
    canvas.line(20, letter[1]-20, letter[0]-20, letter[1]-20)
    canvas.line(25, letter[1]-25, letter[0]-25, letter[1]-25)
    # Bottom border - Blue
    canvas.setStrokeColor(colors.blue)
    canvas.line(20, 20, letter[0]-20, 20)
    canvas.line(25, 25, letter[0]-25, 25)
    # Left border - Green
    canvas.setStrokeColor(colors.green)
    canvas.line(20, 20, 20, letter[1]-20)
    canvas.line(25, 25, 25, letter[1]-25)
    # Right border - Dark Blue/Green mix
    canvas.setStrokeColor(colors.teal)
    canvas.line(letter[0]-20, 20, letter[0]-20, letter[1]-20)
    canvas.line(letter[0]-25, 25, letter[0]-25, letter[1]-25)
    canvas.restoreState()

def process_text(text):
    text = text.replace("—", ", ")
    text = text.replace("--", ", ")
    return text

def build_report(filename):
    # minimal margins to use all space, but leave room for borders
    doc = BaseDocTemplate(filename, pagesize=letter,
                          rightMargin=40, leftMargin=40,
                          topMargin=40, bottomMargin=40)

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='test', frames=frame, onPage=draw_border)
    doc.addPageTemplates([template])

    styles = getSampleStyleSheet()

    # == TYPEFACE & STYLES ==
    # Times New Roman, 12pt, 1.5 spacing (18pt leading)
    
    styles.add(ParagraphStyle(
        name='MainTitle',
        fontName='Times-Bold',
        fontSize=24,
        leading=28,
        spaceAfter=15,
        textColor=colors.darkblue,
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        fontName='Times-Italic',
        fontSize=14,
        leading=21, # 1.5 of 14
        spaceAfter=20,
        textColor=colors.darkred,
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Times-Bold',
        fontSize=16,
        leading=24,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.darkgreen,
    ))
    
    styles.add(ParagraphStyle(
        name='DomainTitle',
        fontName='Times-Bold',
        fontSize=14,
        leading=21,
        spaceBefore=10,
        spaceAfter=5,
        textColor=colors.darkblue,
    ))

    styles.add(ParagraphStyle(
        name='Body_1_5',
        fontName='Times-Roman',
        fontSize=12,
        leading=18, # 1.5 spacing
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        textColor=colors.black
    ))

    Story = []

    # Title
    Story.append(Paragraph("ADVERSARIAL SYNTHESIS REPORT", styles['MainTitle']))
    Story.append(Paragraph("Given that states never follow rules of international law, do such rules even exist.", styles['SubTitle']))

    # Text blocks to use
    Story.append(Paragraph("I. PRE-FLIGHT: SOURCE REGISTRY", styles['SectionHeader']))
    reg_text = "<b>Primary Sources:</b> Austin's <i>The Province of Jurisprudence Determined</i> (1832) argues law is a sovereign command backed by sanction; lacking this, international law is 'positive morality.' Hart's <i>The Concept of Law</i> (1961) sees it as a primitive legal system with decentralized pressure. ICJ Statute, Article 38(1) codifies its formal sources. <i>Nicaragua v USA</i> (1986) ICJ Reports 14 provides the most devastating empirical exhibit, as the US ignored a binding ruling with zero legal consequences.<br/><b>Empirical Data & Competing Positions:</b> Hathaway (2002) finds human rights treaty ratification does not correlate with improved practices, but rather serves performative legitimacy. Conversely, Chayes & Chayes (1993) argue compliance is actually 90%+, primarily in trade and diplomacy. Koskenniemi (2005) theorizes the apology-to-utopia structural oscillation of international law, while Henkin (1979) asserts that 'almost all nations observe almost all principles of international law almost all of the time.'"
    Story.append(Paragraph(process_text(reg_text), styles['Body_1_5']))

    Story.append(Paragraph("II. PHASE 1: DOMAIN-BASED ADVERSARIAL GENERATION", styles['SectionHeader']))
    
    Story.append(Paragraph("Domain 1: Law & Governance", styles['DomainTitle']))
    d1 = "The textualist lens views international law as 'text without teeth,' arguing that law requires enforceability, and statutes without compulsion are mere aspiration. Egalitarians strongly disagree, observing that conventions like CEDAW and the Rome Statute have restructured domestic legal systems globally, providing real protections that vulnerable people depend on daily. The sovereign theorist counters that international law is simply the language powerful states use to dress their interests in moral costume, suspending rules whenever inconvenient for the hegemon."
    Story.append(Paragraph(process_text(d1), styles['Body_1_5']))

    Story.append(Paragraph("Domain 2: Economics & Markets", styles['DomainTitle']))
    d2 = "Market Libertarians note that international law exists purely where it serves mutual economic self-interest, such as WTO law and investment treaties, which are followed religiously due to retaliatory costs. Interventionists argue that Bretton Woods and the WTO are the institutional architecture of global GDP, not mere suggestions. However, Institutional Economists highlight that these rules operate as asymmetric weapons of the powerful, forcing developing nations to open markets while rich nations maintain subsidies, existing the way colonial law existed for the colonizer."
    Story.append(Paragraph(process_text(d2), styles['Body_1_5']))

    Story.append(Paragraph("Domain 3: Technology & Systems", styles['DomainTitle']))
    d3 = "Cybernetics reframes international law not as a centralized command, but as a decentralized feedback system using reputational and relational costs to influence behavior. Antifragility theory attacks this, arguing the system shatters during genuine crises, becoming a 'fair-weather fiction.' Existential Risk theorists insist that for global threats like nuclear war and misaligned AGI, international law is the only functional governance framework, making its existence a prerequisite for civilizational survival."
    Story.append(Paragraph(process_text(d3), styles['Body_1_5']))

    Story.append(Paragraph("Domain 4: Philosophy & Ethics", styles['DomainTitle']))
    d4 = "Utilitarians argue that if these rules reduce net human suffering, they possess consequentialist value regardless of perfect enforcement. Deontologists maintain that moral imperatives, such as the prohibition on genocide, are independent of state compliance; a moral law violated a thousand times retains its binding force. Political Evil analysts view international law as the juridical memory of humanity's worst failures, arguing that denying its existence means the lessons of atrocities like Auschwitz can be unlearned."
    Story.append(Paragraph(process_text(d4), styles['Body_1_5']))

    Story.append(Paragraph("Domain 5: Sociology & Psychology", styles['DomainTitle']))
    d5 = "Bureaucratic sociology views international law as a legitimation system where violators invoke legal language to justify actions. Biopolitics reframes it entirely, arguing international law produces the very categories of 'state' and 'sovereignty' that violate it. Cognitively, dual-process theory destroys the premise's factual foundation as a product of 'availability bias', we remember dramatic invasions but ignore the thousands of daily instances of compliance in aviation and postal treaties. Behaviorists see it as a reinforcement schedule, while structural psychologists view it as a colonial tool enforcing oppression disguised as universal rules."
    Story.append(Paragraph(process_text(d5), styles['Body_1_5']))

    Story.append(Paragraph("Domain 6: History & Epistemology", styles['DomainTitle']))
    d6 = "Cyclical history diagnoses international law as the code of a decaying Western civilizational order. Realpolitik treats the rules as tools of statecraft invoked strategically, not authoritative constraints. Anti-colonial critiques emphasize that the 'universal' rules were designed by European empires to regulate colonization. Epistemologically, Open Society logic finds the premise unfalsifiable, while Systems Thinking shifts the focus from 'existence' to system behavior, arguing that although imperfect, the system does produce order."
    Story.append(Paragraph(process_text(d6), styles['Body_1_5']))

    Story.append(Paragraph("III. THE GALA: ADVERSARIAL TOURNAMENT", styles['SectionHeader']))
    gala1 = "In the quarterfinals, Kant's argument that rules exist as moral imperatives combined with Kahneman's proof of high empirical compliance to form a devastating two-pronged attack: the premise is both morally incoherent and empirically false. Concurrently, Foucault and Césaire synthesized to note that while the rules exist, they inherently constitute asymmetrical colonial power structures."
    Story.append(Paragraph(process_text(gala1), styles['Body_1_5']))

    gala2 = "<b>The Final Hearing:</b> The Grand Synthesis argued the premise is factually false (Chayes), cognitively biased (Kahneman), and morally corrupt (Kant). Systemically, international law operates as a real, decentralized coordination mechanism (Wiener/Meadows) that literally constitutes the actors within it (Foucault). The Realist Bloc countered that measuring compliance in frictionless domains is irrelevant; against any actor powerful enough to matter, the system collapses. It is designed to discipline the weak and immunize the permanent five."
    Story.append(Paragraph(process_text(gala2), styles['Body_1_5']))
    
    Story.append(Paragraph("IV. THE JUDGMENT", styles['SectionHeader']))
    maj = "<b>Majority Opinion:</b> The rules of international law exist. The premise's factual assertion, that states 'never' follow them, is empirically false. Based on overwhelming evidence (Henkin, Chayes), the vast majority of international legal obligations are observed the vast majority of the time. The premise is a cognitive product of availability bias: dramatic violations are vivid, while routine compliance is invisible. Furthermore, international law constitutes states. Without its legal concepts of sovereignty and territorial integrity, the entities that violate it would not exist."
    Story.append(Paragraph(process_text(maj), styles['Body_1_5']))

    diss = "<b>Strongest Dissent (The Realist Bloc):</b> The Challenger's irreducible objection demolishes the compliance statistics: Nicaragua v United States (1986) proves that when a great power is subjected to a binding judgment, it can refuse compliance, veto enforcement, and withdraw from jurisdiction with zero legal consequence. The truly devastating reformulation of the premise is not 'do the rules exist?' but 'do the rules exist for the powerful?', and the empirical answer is No."
    Story.append(Paragraph(process_text(diss), styles['Body_1_5']))

    Story.append(Paragraph("V. FINAL CONCLUSION REPORT", styles['SectionHeader']))
    conc1 = "The question of whether international law 'exists' given persistent state non-compliance is not merely an academic exercise, it is a fundamental interrogation of whether normative order is possible beyond the nation-state. The strongest defense of international law's existence rests on three independent pillars. First, compliance is empirically overwhelming in the machinery of trade, diplomacy, and aviation. Second, conceptually, a rule violated does not cease to exist. Third, and most powerfully, international law recursively constitutes the states themselves."
    Story.append(Paragraph(process_text(conc1), styles['Body_1_5']))

    conc2 = "However, the most powerful surviving dissent remains genuinely unanswered. History proves that when a great power is subjected to a binding ICJ judgment, it can refuse compliance and veto enforcement with zero legal consequence. The compliance statistics measure obedience only in domains where powerful states had no incentive to deviate. Thus, the rules exist, but the Security Council veto and the structural impunity of permanent member nations demonstrate a system designed to discipline the weak while immunizing the strong."
    Story.append(Paragraph(process_text(conc2), styles['Body_1_5']))

    conc3 = "What this adversarial examination reveals systemically is that the international legal order suffers from a fundamental feedback asymmetry. It operates as a functioning decentralized coordination system for the vast majority of routine interactions, but its corrective feedback mechanisms collapse catastrophically when the deviant actor is powerful enough to absorb the diplomatic and reputational costs of non-compliance. This is not a failure of international law as a concept, it is a specific architectural deficiency in the enforcement design inherited from the 1945 settlement."
    Story.append(Paragraph(process_text(conc3), styles['Body_1_5']))

    doc.build(Story)

if __name__ == '__main__':
    build_report('/Users/basilikax/Library/Containers/com.apple.BKAgentService/Data/Documents/iBooks/Books/Legal/international_law_synthesis_v3.pdf')
