from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def create_pdf_report(resume_name: str, role_title: str, result: dict, recommendations: list[dict]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm, title="SkillLens Analysis Report"
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="SkillLensTitle", parent=styles["Title"], alignment=TA_CENTER,
        textColor=colors.HexColor("#2563EB"), spaceAfter=8,
    ))
    styles.add(ParagraphStyle(name="Footnote", parent=styles["BodyText"],
        textColor=colors.HexColor("#475569"), fontSize=8, leading=11))
    story = [
        Paragraph("SkillLens — Resume Skill Gap Analysis", styles["SkillLensTitle"]),
        Paragraph(f"<b>Target role:</b> {escape(role_title)}", styles["BodyText"]),
        Paragraph(f"<b>Resume file:</b> {escape(resume_name)}", styles["BodyText"]),
        Spacer(1, 8),
        Paragraph(
            f"<b>Skill fit score:</b> {result['match_percentage']:.1f}% "
            f"({len(result['matched_skills'])} of {len(result['required_skills'])} required skills matched)",
            styles["Heading2"],
        ),
        Paragraph(f"<b>Match approach:</b> {escape('Keyword + semantic similarity' if result.get('semantic_available') else 'Keyword matching; semantic model unavailable or disabled')}", styles["BodyText"]),
        Spacer(1, 10),
        Paragraph("Matched skills", styles["Heading2"]),
        Paragraph(escape(", ".join(result["matched_skills"]) or "None detected"), styles["BodyText"]),
        Spacer(1, 7),
        Paragraph("Skills to build", styles["Heading2"]),
        Paragraph(escape(", ".join(result["missing_skills"]) or "None detected"), styles["BodyText"]),
        Spacer(1, 10),
        Paragraph("Learning recommendations", styles["Heading2"]),
    ]
    if recommendations:
        rows = [["Skill", "Priority", "Suggested next step"]]
        for item in recommendations:
            rows.append([
                Paragraph(escape(item["skill"]), styles["BodyText"]),
                Paragraph(escape(item["priority"]), styles["BodyText"]),
                Paragraph(escape(item["suggestion"]), styles["BodyText"]),
            ])
        table = Table(rows, colWidths=[34 * mm, 22 * mm, 112 * mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DBEAFE")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No gaps found in the supported skill list.", styles["BodyText"]))
    story += [
        Spacer(1, 14),
        Paragraph(
            "Important: this score is an estimate based on a limited supported skill library. "
            "Semantic similarity may produce false matches. It is not a measure of overall ability "
            "or a prediction of hiring success. Review the results before making decisions.",
            styles["Footnote"],
        ),
    ]
    doc.build(story)
    return buffer.getvalue()
