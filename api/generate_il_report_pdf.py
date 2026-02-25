import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

def create_report(filename):
    # Set up the document
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()

    # Define custom styles
    styles.add(ParagraphStyle(
        name='CoverTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=28,
        spaceAfter=20,
        textColor=colors.HexColor('#1F3A52'),
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=14,
        spaceAfter=30,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='ReportHeading1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        spaceAfter=15,
        spaceBefore=25,
        textColor=colors.HexColor('#1F3A52'),
        bottomPadding=5
    ))

    styles.add(ParagraphStyle(
        name='ReportHeading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#2A4F70')
    ))

    styles.add(ParagraphStyle(
        name='BodyJustify',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        spaceAfter=14,
        alignment=TA_JUSTIFY,
        textColor=colors.black
    ))
    
    styles.add(ParagraphStyle(
        name='HighlightBox',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=18,
        spaceAfter=20,
        spaceBefore=20,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#1F3A52'),
        borderPadding=10,
        backColor=colors.HexColor('#F4F7FA'),
        borderColor=colors.HexColor('#B0C4DE'),
        borderWidth=1
    ))

    Story = []

    # ================= COVER PAGE =================
    Story.append(Spacer(1, 2*inch))
    
    img_path = "/Users/basilikax/.gemini/antigravity/brain/cf0f0f18-d421-4115-b8d6-0bf83ca2d17e/international_law_cover_1771762776467.png"
    if os.path.exists(img_path):
        img = Image(img_path, width=4*inch, height=4*inch)
        Story.append(img)
    
    Story.append(Spacer(1, 0.5*inch))
    Story.append(Paragraph("Adversarial Synthesis Report", styles['CoverTitle']))
    Story.append(Paragraph("An Inquiry into the Existence and Efficacy of International Law", styles['CoverSubtitle']))
    Story.append(Paragraph("Prepared via the 24-Lens Synthesis Engine", styles['CoverSubtitle']))
    Story.append(PageBreak())

    # Helper function to remove em dashes and process highlights
    def process_text(text):
        # Remove em dashes and replace with commas or spaces
        text = text.replace("—", ",")
        text = text.replace("--", ",")
        return text

    # ================= TARGET PREMISE =================
    Story.append(Paragraph("Target Premise", styles['ReportHeading1']))
    premise_text = process_text("Given that states never follow rules of international law, do such rules even exist.")
    Story.append(Paragraph(f'"{premise_text}"', styles['HighlightBox']))

    # ================= PRE-FLIGHT: SOURCE REGISTRY =================
    Story.append(Paragraph("Pre-Flight: Source Registry", styles['ReportHeading1']))
    Story.append(Paragraph("Directly On-Point (Primary Sources)", styles['ReportHeading2']))
    sources1 = [
        "<b>1. Austin, J. (1832)</b>: <i>The Province of Jurisprudence Determined</i>. The foundational attack: law is a command of a sovereign backed by a sanction. Since there is no global sovereign and no enforceable sanction, international law is not law but positive morality, mere opinion among nations.",
        "<b>2. Hart, H.L.A. (1961)</b>: <i>The Concept of Law</i>, Chapter X. Concedes that international law lacks a centralized legislature and centralized sanctions, but argues it is still a primitive but real legal system operating through decentralized social pressure.",
        "<b>3. ICJ Statute, Article 38(1) (1945)</b>. The formal enumeration of the sources of international law: treaties, custom, general principles, and subsidiary judicial decisions.",
        "<b>4. <i>Nicaragua v United States of America</i> [1986] ICJ Reports 14</b>. The ICJ ruled that the United States violated international law by mining Nicaraguan harbours. The U.S. refused to comply and withdrew from ICJ compulsory jurisdiction, the single most devastating empirical exhibit for the premise."
    ]
    for src in sources1:
        Story.append(Paragraph(process_text(src), styles['BodyJustify']))

    Story.append(Paragraph("Empirical Data & Competing Academics", styles['ReportHeading2']))
    sources2 = [
        "<b>5. Hathaway, O. (2002)</b>: <i>Do Human Rights Treaties Make a Difference?</i> Empirical study finding that ratification of human rights treaties is <b>not</b> correlated with improved practices.",
        "<b>6. Chayes, A. & Chayes, A.H. (1993)</b>: <i>On Compliance</i>. Counter-study arguing that the compliance rate is actually remarkably high (estimated 90%+), but this goes unnoticed because violations are dramatic.",
        "<b>7. Koskenniemi, M. (2005)</b>: <i>From Apology to Utopia</i>. The definitive critical theory: international law structurally oscillates between justifying state power and aspiring to utopian norms.",
        "<b>8. Henkin, L. (1979)</b>: <i>How Nations Behave</i>. The classic rebuttal: <b>'Almost all nations observe almost all principles of international law... almost all of the time.'</b>"
    ]
    for src in sources2:
        Story.append(Paragraph(process_text(src), styles['BodyJustify']))

    # ================= THE 24 LENSES =================
    Story.append(PageBreak())
    Story.append(Paragraph("Phase 1 & 2: Adversarial Examination", styles['ReportHeading1']))
    intro_phase2 = "Across eight domains, 24 sovereign minds dissected the premise. The fundamental fault line was not constitutional versus philosophical, but empiricist versus structuralist. Those working with compliance data overwhelmingly rejected the premise, while post-colonial and realist frameworks acknowledged the rules' textual existence but argued they function asymmetrically, binding the weak while advising the strong."
    Story.append(Paragraph(process_text(intro_phase2), styles['BodyJustify']))

    Story.append(Paragraph("Key Confrontations", styles['ReportHeading2']))

    conf1 = "<b>The Law & Governance Confrontation:</b> Antonin Scalia identified international law as 'text without teeth', whereas Ruth Bader Ginsburg countered that conventions like CEDAW have restructured domestic legal systems across dozens of countries. Carl Schmitt agreed with the premise, asserting that international law is simply the language that powerful states use to dress their interests in moral costume."
    Story.append(Paragraph(process_text(conf1), styles['BodyJustify']))

    conf2 = "<b>The Structural & Sociological Take:</b> Michel Foucault delivered a devastating reframe: international law <i>produces</i> states, sovereignty, and borders. Without it, the very entities that 'violate' it would not exist in their current form. Aimé Césaire contributed that international law was born in colonial violence, and its existence today is fundamentally an extension of that colonial architecture, enforcing rules asymmetrically."
    Story.append(Paragraph(process_text(conf2), styles['BodyJustify']))

    conf3 = "<b>The Psychological Realism:</b> Daniel Kahneman annihilated the factual foundation of the premise: 'states never follow international law' is a classic <i>availability heuristic</i>. We remember dramatic violations, but ignore thousands of daily instances of compliance in trade, aviation, and postal treaties."
    Story.append(Paragraph(process_text(conf3), styles['BodyJustify']))
    
    Story.append(PageBreak())

    # ================= THE JUDGMENT =================
    Story.append(Paragraph("Phase 3: The Judgment", styles['ReportHeading1']))
    
    Story.append(Paragraph("Majority Opinion", styles['ReportHeading2']))
    majority = "The rules of international law exist. The premise's factual assertion, that states 'never' follow them, is empirically false. Based on overwhelming evidence, the vast majority of international legal obligations are observed the vast majority of the time. The premise is a cognitive product of availability bias. Furthermore, international law does not merely regulate states; it constitutes them. Without its legal concepts of sovereignty and territorial integrity, the entities that violate it would not exist in their current form."
    Story.append(Paragraph(process_text(majority), styles['BodyJustify']))
    
    Story.append(Paragraph("Strongest Dissent (The Realist Bloc)", styles['ReportHeading2']))
    dissent = "The Challenger's irreducible objection demolishes the compliance statistics: <i>Nicaragua v United States</i> (1986) proves that when a great power is subjected to a binding judgment, it can refuse compliance, veto enforcement, and withdraw from jurisdiction with zero legal consequence. Measuring compliance with postal treaties and aviation routes is like measuring honesty only when there is nothing to gain from lying. The truly devastating reformulation of the premise is not 'do the rules exist?' but <b>'do the rules exist for the powerful?'</b>, and the empirical answer is No."
    Story.append(Paragraph(process_text(dissent), styles['BodyJustify']))
    
    # ================= FINAL CONCLUSION REPORT =================
    Story.append(Paragraph("Phase 4: Final Conclusion Report", styles['ReportHeading1']))
    
    conc1 = "The question of whether international law 'exists' given persistent state non-compliance is a fundamental interrogation of whether normative order is possible beyond the nation-state. The premise embeds a factual claim and derives an ontological conclusion. Both, upon rigorous adversarial examination, prove to be substantially wrong, but the question itself exposes a genuine and devastating structural pathology in the international legal order."
    Story.append(Paragraph(process_text(conc1), styles['BodyJustify']))
    
    conc2 = "The strongest defense rests on three pillars. First, compliance is empirically overwhelming, concentrated in the vast machinery of trade, diplomacy, and aviation. Second, morally, a rule violated does not cease to exist, just as the prohibition on murder is not negated by the occurrence of murder. Third, international law <i>constitutes</i> states. A state invoking 'sovereign right' to violate international law is using international law in the very act of defying it."
    Story.append(Paragraph(process_text(conc2), styles['BodyJustify']))

    conc3 = "However, the most powerful surviving dissent remains genuinely unanswered. The Security Council veto, the ICC's selective prosecutions, and the structural impunity of powerful nations demonstrate a system designed to discipline the weak while immunizing the strong. The international legal order suffers from a fundamental <b>feedback asymmetry</b>. It operates as a functioning decentralized coordination system for routine interactions, but its corrective feedback mechanisms collapse catastrophically when the deviant actor is powerful enough to absorb the costs of non-compliance."
    Story.append(Paragraph(process_text(conc3), styles['BodyJustify']))

    # Build the pdf
    doc.build(Story)

if __name__ == '__main__':
    create_report('/Users/basilikax/Library/Containers/com.apple.BKAgentService/Data/Documents/iBooks/Books/Legal/international_law_report.pdf')
