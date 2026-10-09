"""PDF Report Generator for Smart AI Resume Analyzer using ReportLab."""
import io
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.main import DISCLAIMER


def generate_pdf_report(report: dict, job_title: str = "Target Position") -> bytes:
    """Generate a clean, professional PDF report as bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom Styles (Dark / Professional Theme for PDF)
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e1b4b"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )

    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#312e81"),
        spaceBefore=10,
        spaceAfter=5,
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#334155"),
    )

    bold_body = ParagraphStyle(
        "BoldBodyText",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-10,
        spaceAfter=3,
    )

    elements = []

    # Title & Header
    filename = os.path.basename(report.get("filename", "Resume"))
    elements.append(Paragraph("Resume Analysis Report", title_style))
    elements.append(Paragraph(f"Target Role: <b>{job_title}</b> &nbsp;|&nbsp; Resume File: {filename}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#6366f1"), spaceAfter=10))

    # Metric Cards Table
    matched_count = len(report.get("matched_skills", []))
    total_job_skills = len(report.get("job_skills", []))
    sections_count = len(report.get("sections", []))

    metric_data = [
        [
            Paragraph("<b>Compatibility Score</b>", body_style),
            Paragraph("<b>Skill Coverage</b>", body_style),
            Paragraph("<b>Matched Skills</b>", body_style),
            Paragraph("<b>Recognized Sections</b>", body_style),
        ],
        [
            Paragraph(f"<font size=13 color='#4338ca'><b>{report.get('score', 0)}/100</b></font>", body_style),
            Paragraph(f"<font size=13 color='#4338ca'><b>{report.get('skill_coverage', 0)}%</b></font>", body_style),
            Paragraph(f"<font size=13 color='#16a34a'><b>{matched_count}/{total_job_skills}</b></font>", body_style),
            Paragraph(f"<font size=13 color='#4338ca'><b>{sections_count}</b></font>", body_style),
        ],
    ]

    metric_table = Table(metric_data, colWidths=[130, 130, 130, 130])
    metric_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    elements.append(metric_table)
    elements.append(Spacer(1, 10))

    # Score Explanation
    elements.append(Paragraph("What Does Your Score Mean?", h2_style))
    exp_text = (
        f"The <b>Compatibility Score ({report.get('score', 0)}/100)</b> measures total textual alignment between "
        f"your resume and the job description using TF-IDF vector cosine similarity. Meanwhile, <b>Skill Coverage ({report.get('skill_coverage', 0)}%)</b> "
        f"measures the percentage of explicit required skills found in your document. In this analysis, "
        f"you matched {matched_count} of {total_job_skills} required skills. Discrepancies between these metrics "
        f"occur because the job description contains broader context, responsibilities, and phrasing that extend beyond the skill list alone."
    )
    elements.append(Paragraph(exp_text, body_style))
    elements.append(Spacer(1, 8))

    # Skills Breakdown
    elements.append(Paragraph("Skills Match Analysis", h2_style))

    additional_skills = [s for s in report.get("resume_skills", []) if s not in report.get("job_skills", [])]
    matched_str = ", ".join(report.get("matched_skills", [])) if report.get("matched_skills") else "None"
    missing_str = ", ".join(report.get("missing_skills", [])) if report.get("missing_skills") else "No missing required skills."
    additional_str = ", ".join(additional_skills) if additional_skills else "None"

    skills_data = [
        [Paragraph("<b>Category</b>", bold_body), Paragraph("<b>Skills Identified</b>", bold_body)],
        [Paragraph("<font color='#16a34a'><b>Matched Required Skills</b></font>", body_style), Paragraph(matched_str, body_style)],
        [Paragraph("<font color='#d97706'><b>Missing Required Skills</b></font>", body_style), Paragraph(missing_str, body_style)],
        [Paragraph("<font color='#2563eb'><b>Additional Skills Found</b></font>", body_style), Paragraph(additional_str, body_style)],
    ]

    skills_table = Table(skills_data, colWidths=[140, 380])
    skills_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])
    )
    elements.append(skills_table)
    elements.append(Spacer(1, 8))

    # Strengths
    elements.append(Paragraph("What Your Resume Does Well", h2_style))
    if report.get("strengths"):
        for strength in report["strengths"]:
            elements.append(Paragraph(f"• {strength}", bullet_style))
    else:
        elements.append(Paragraph("No specific strengths detected.", body_style))
    elements.append(Spacer(1, 8))

    # Recommendations
    elements.append(Paragraph("Recommended Improvements", h2_style))
    if report.get("recommendations"):
        for idx, rec in enumerate(report["recommendations"], 1):
            elements.append(Paragraph(f"<b>Step {idx}:</b> {rec}", bullet_style))
    else:
        elements.append(Paragraph("No critical improvements needed.", body_style))
    elements.append(Spacer(1, 10))

    # Summary Footer
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#6366f1"), spaceAfter=6))
    summary_text = (
        f"<b>Your Resume Analysis Summary:</b> Your resume contains {matched_count} of {total_job_skills} required job skills "
        f"({report.get('skill_coverage', 0)}% coverage) with a compatibility score of {report.get('score', 0)}/100. "
        f"Review the recommended improvements above to optimize your experience wording prior to submission."
    )
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<i>Disclaimer: {DISCLAIMER}</i>", ParagraphStyle("Disc", parent=body_style, fontSize=8, textColor=colors.HexColor("#64748b"))))

    doc.build(elements)
    return buffer.getvalue()
