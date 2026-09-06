"""
SENTINEL v2.0 — Test Document Generator
Generates realistic, court-formatted Indian Police FIR PDFs and Field Intelligence
Surveillance Briefs for testing the ingestion, OCR, and NER pipelines.
"""

import os
import sys

# Ensure backend and project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from backend.config import DATA_DIR

TEST_DOCS_DIR = os.path.join(DATA_DIR, "test_documents")
os.makedirs(TEST_DOCS_DIR, exist_ok=True)

def generate_sample_fir_pdf(output_path: str = None) -> str:
    """Generates a court-standard Jharkhand Police First Information Report PDF."""
    if not output_path:
        output_path = os.path.join(TEST_DOCS_DIR, "SAMPLE_POLICE_FIR_CR2026_0418.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        alignment=1,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=1,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )
    meta_label = ParagraphStyle('MetaLabel', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#1e293b'))
    meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#334155'))
    body_style = ParagraphStyle('BodyStyle', fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#1e293b'))
    section_head = ParagraphStyle('SectionHead', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0369a1'), spaceBefore=8, spaceAfter=4)

    elements = []

    elements.append(Paragraph("JHARKHAND STATE POLICE DEPARTMENT", title_style))
    elements.append(Paragraph("FIRST INFORMATION REPORT (Under Section 154 Cr.P.C.)", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=8))

    meta_data = [
        [Paragraph("1. District: <b>Ranchi</b>", meta_label), Paragraph("2. Police Station: <b>Kotwali PS</b>", meta_label), Paragraph("3. Year: <b>2026</b>", meta_label)],
        [Paragraph("4. FIR No: <b>FIR-2026/0418</b>", meta_label), Paragraph("5. Date & Time: <b>15/01/2026 21:45 IST</b>", meta_label), Paragraph("6. GD Entry: <b>GD-882/26</b>", meta_label)],
        [Paragraph("7. Acts & Sections:", meta_label), Paragraph("<b>IPC Section 384, Section 392, Section 420, Section 120B & Section 25 Arms Act</b>", meta_val), Paragraph("Status: <b>REGISTERED</b>", meta_label)],
        [Paragraph("8. Occurrence Date:", meta_label), Paragraph("<b>15/01/2026 at 19:30 hours</b>", meta_val), Paragraph("Type of Crime: <b>EXTORTION / HAWALA</b>", meta_label)],
        [Paragraph("9. Place of Occurrence:", meta_label), Paragraph("<b>Tower Chowk, Bariatu Road, Ranchi (3.5 km North-East from PS)</b>", meta_val), Paragraph("Jurisdiction: <b>Kotwali Sector 2</b>", meta_label)]
    ]

    t1 = Table(meta_data, colWidths=[180, 230, 130])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("10. COMPLAINANT / INFORMANT DETAILS", section_head))
    comp_data = [
        [Paragraph("Name: <b>Shri Mohan Lal Agarwal</b> (S/o Late Rameshwar Agarwal)", meta_val), Paragraph("Mobile: <b>+91-9431100999</b>", meta_val)],
        [Paragraph("Address: <b>Circular Road, Lalpur, Ranchi, Jharkhand</b>", meta_val), Paragraph("Occupation: <b>Coal Logistics Merchant</b>", meta_val)]
    ]
    t2 = Table(comp_data, colWidths=[350, 190])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffffff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("11. DETAILS OF KNOWN / SUSPECTED / ACCUSED PERSONS", section_head))
    acc_data = [
        [Paragraph("<b>#</b>", meta_label), Paragraph("<b>Accused Name & Aliases</b>", meta_label), Paragraph("<b>Identified Role</b>", meta_label), Paragraph("<b>Associated Handset / Contact</b>", meta_label)],
        [Paragraph("1", meta_val), Paragraph("<b>Vikram Sinha</b> (alias <i>'Vicky Bhai'</i>, R/o Bankmore Dhanbad)", meta_val), Paragraph("Gang Leader / Mastermind", meta_val), Paragraph("<b>+91-9835012345</b>", meta_val)],
        [Paragraph("2", meta_val), Paragraph("<b>Deepak Tiwari</b> (R/o Bariatu, Ranchi)", meta_val), Paragraph("Logistics / Bridge Coordinator", meta_val), Paragraph("<b>+91-9876500001</b>", meta_val)],
        [Paragraph("3", meta_val), Paragraph("<b>Suresh Patel</b> (R/o Jamshedpur)", meta_val), Paragraph("Hawala Cash & Account Mule", meta_val), Paragraph("<b>+91-9123488888</b>", meta_val)]
    ]
    t3 = Table(acc_data, colWidths=[25, 235, 150, 130])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t3)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("12. FIRST INFORMATION STATEMENT & PARTICULARS OF OCCURRENCE", section_head))
    statement_p1 = (
        "On 15/01/2026 at approximately 19:30 hours, the complainant Shri Mohan Lal Agarwal was intercepted near "
        "Tower Chowk in Bariatu, Ranchi by three accused individuals arriving in a White Mahindra Scorpio bearing registration number "
        "<b>JH-01-AB-1234</b> and an escort motorcycle <b>JH-01-XY-9876</b>. "
        "The accused Vikram Sinha drew a country-made firearm and demanded an extortion levy of <b>Rs. 4,85,000</b> (Four Lakh Eighty-Five Thousand Rupees) "
        "threatening violent harm to complainant's family if payment was delayed."
    )
    elements.append(Paragraph(statement_p1, body_style))
    elements.append(Spacer(1, 4))

    statement_p2 = (
        "Under duress, the complainant was coerced into transferring an immediate electronic deposit of <b>Rs. 49,500</b> via IMPS "
        "to Axis Bank Account number <b>918020019283746</b> (IFSC Code: <b>UTIB0000123</b>) standing in the name of accused Suresh Patel. "
        "The accused instructed that the remaining cash balance must be delivered to their safehouse near Ramgarh Highway Bypass. "
        "The accused Deepak Tiwari was observed giving directions to driver and was using mobile phone <b>+91-9876500001</b>. "
        "Tower location logs verify that mobile numbers <b>+91-9835012345</b> and <b>+91-9876500001</b> were active concurrently near Bariatu Tower (TWR-1001)."
    )
    elements.append(Paragraph(statement_p2, body_style))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("13. ACTION TAKEN & INVESTIGATION DIRECTION", section_head))
    action_text = (
        "Case registered under Sections 384, 392, 420, 120B IPC and Section 25 Arms Act. Investigation entrusted to SI A. K. Verma. "
        "Immediate notice issued to Axis Bank for freezing account 918020019283746 u/s 102 Cr.P.C. "
        "CDR logs requisitioned from telecom service provider for cell tower TWR-1001. "
        "Digital evidence copy hashed with SHA-256 for court certification under Section 63 Bharatiya Sakshya Adhiniyam / Section 65B Indian Evidence Act."
    )
    elements.append(Paragraph(action_text, body_style))
    elements.append(Spacer(1, 14))

    sign_data = [
        [Paragraph("Signature of Complainant:<br/><b>Mohan Lal Agarwal</b>", meta_val), Paragraph("Station House Officer / Investigating Officer:<br/><b>Inspector R. K. Sharma (Badge #4092)</b><br/>Kotwali PS, Ranchi District", meta_val)]
    ]
    t_sign = Table(sign_data, colWidths=[270, 270])
    t_sign.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t_sign)

    doc.build(elements)
    print(f"Sample FIR PDF successfully written to: {output_path}")
    return output_path

def generate_sample_intel_report_pdf(output_path: str = None) -> str:
    """Generates a field intelligence surveillance report PDF."""
    if not output_path:
        output_path = os.path.join(TEST_DOCS_DIR, "SAMPLE_INTELLIGENCE_SURVEILLANCE_REPORT.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', fontName='Helvetica-Bold', fontSize=14, alignment=1, textColor=colors.HexColor('#0f172a'), spaceAfter=4)
    subtitle_style = ParagraphStyle('SubStyle', fontName='Helvetica-Bold', fontSize=9, alignment=1, textColor=colors.HexColor('#dc2626'), spaceAfter=8)
    meta_label = ParagraphStyle('MetaLabel', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#1e293b'))
    meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#334155'))
    body_style = ParagraphStyle('BodyStyle', fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#1e293b'))
    section_head = ParagraphStyle('SectionHead', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0369a1'), spaceBefore=8, spaceAfter=4)

    elements = []

    elements.append(Paragraph("SPECIAL TASK FORCE // CRIMINAL INTELLIGENCE BUREAU", title_style))
    elements.append(Paragraph("CONFIDENTIAL // LAW ENFORCEMENT SENSITIVE // CODE: OPERATION COAL-NET", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#dc2626'), spaceAfter=8))

    meta_data = [
        [Paragraph("Document ID: <b>INTEL-2026-STF-088</b>", meta_label), Paragraph("Date: <b>16/01/2026</b>", meta_label), Paragraph("Classification: <b>TOP SECRET // CID</b>", meta_label)],
        [Paragraph("Source: <b>HUMINT + CDR Intercept</b>", meta_label), Paragraph("Lead Analyst: <b>Dep. SP K. S. Murthy</b>", meta_label), Paragraph("Target Syndicate: <b>Dhanbad Extortion Syndicate</b>", meta_label)],
    ]
    t1 = Table(meta_data, colWidths=[180, 180, 180])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef2f2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#fca5a5')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("1. OPERATIONAL BRIEFING & SUSPECT SYNDICATE TOPOLOGY", section_head))
    briefing = (
        "Technical SIGINT monitoring and field surveillance by STF Team Delta confirmed that the inter-state syndicate "
        "headed by target <b>Vikram Sinha</b> has reactivated illicit extortion operations across Bokaro, Dhanbad, and Ranchi. "
        "Surveillance indicates that suspect Vikram Sinha operates through an intermediary cut-out, identified as <b>Deepak Tiwari</b>, "
        "who controls logistics and safehouse arrangements in Bariatu. "
        "Financial laundering is managed through <b>Suresh Patel</b>, using front accounts in Axis Bank and HDFC Bank."
    )
    elements.append(Paragraph(briefing, body_style))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("2. TELECOM HARDWARE & BURNER IMEI ANALYSIS", section_head))
    telecom = (
        "Signal analysis identified burner device IMEI <b>860492040192834</b> rotating across multiple SIM identities. "
        "The handset was first active with SIM <b>+91-9876500001</b> near Bariatu Tower (TWR-1001), subsequently appearing with "
        "SIM <b>+91-9876500002</b> at Doranda Tower (TWR-1002). "
        "35 high-frequency pre-incident calls were recorded between this handset and target Vikram Sinha's primary line <b>+91-9835012345</b>."
    )
    elements.append(Paragraph(telecom, body_style))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("3. NOCTURNAL CO-LOCATION & MOVEMENT RECONNAISSANCE", section_head))
    coloc = (
        "On the night of 15/01/2026 between 02:15 AM and 02:45 AM, cell tower triangulation detected a critical co-location event. "
        "Target Vikram Sinha and co-conspirator <b>Anita Devi</b> were registered within a 350-meter radius at Ormanjhi Junction Tower. "
        "Field units spotted vehicle <b>JH-01-AB-1234</b> departing northwards along NH-33 towards Ramgarh. "
        "A second vehicle, registration <b>DL-02-CD-5678</b>, was observed escorting cash courier Suresh Patel."
    )
    elements.append(Paragraph(coloc, body_style))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("4. FINANCIAL HAWALA MULE TRAILS & STRUCTURING", section_head))
    financial = (
        "Financial intelligence from FIU-IND flagged recurring structured deposits. "
        "A fund loop of <b>Rs. 1,98,000</b> was dispersed in tranches of <b>Rs. 49,500</b> through Axis Bank account "
        "<b>918020019283746</b> (holder Suresh Patel) and HDFC Bank account <b>50100234567890</b>. "
        "This structuring systematically avoids mandatory Income Tax PAN reporting."
    )
    elements.append(Paragraph(financial, body_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Report submitted by: Special Task Force Surveillance Unit • Verification SHA-256 Chain Sealed", meta_val))

    doc.build(elements)
    print(f"Sample Intel Report PDF successfully written to: {output_path}")
    return output_path

if __name__ == "__main__":
    p1 = generate_sample_fir_pdf()
    p2 = generate_sample_intel_report_pdf()
    print("Test PDFs generated:")
    print("1.", p1)
    print("2.", p2)
