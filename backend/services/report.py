import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import List, Dict


def generate_report(job: Dict, candidates: List[Dict]) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles    = getSampleStyleSheet()
    elements  = []

    # ── Custom styles ──────────────────────────────────────────
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=16,
        spaceAfter=6,
        borderPad=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=3,
        leading=14,
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#666666"),
        spaceAfter=2,
        leading=12,
    )

    # ── Header ─────────────────────────────────────────────────
    elements.append(Paragraph("CV Analysis Report", title_style))
    elements.append(Paragraph(f"Position: {job['title']}", subtitle_style))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width="100%", thickness=1.5,
                               color=colors.HexColor("#1a1a2e")))
    elements.append(Spacer(1, 0.4 * cm))

    # ── Job summary table ───────────────────────────────────────
    elements.append(Paragraph("Job Requirements", section_style))

    skills_str = ", ".join(job.get("required_skills", []))
    job_data = [
        ["Field", "Value"],
        ["Job Title",            job.get("title", "")],
        ["Required Skills",      skills_str or "—"],
        ["Min. Experience",      f"{job.get('experience_years', 0)} years"],
        ["Min. Education",       job.get("education", "").capitalize()],
    ]

    job_table = Table(job_data, colWidths=[5 * cm, 12 * cm])
    job_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0), 10),
        ("BACKGROUND",  (0, 1), (0, -1), colors.HexColor("#f0f0f0")),
        ("FONTNAME",    (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f9f9f9")]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("PADDING",     (0, 0), (-1, -1), 6),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(job_table)
    elements.append(Spacer(1, 0.5 * cm))

    # ── Summary stats ───────────────────────────────────────────
    elements.append(Paragraph("Analysis Summary", section_style))

    total       = len(candidates)
    above_70    = sum(1 for c in candidates if c["final_score"] >= 70)
    above_50    = sum(1 for c in candidates if c["final_score"] >= 50)
    avg_score   = round(sum(c["final_score"] for c in candidates) / total, 1) if total else 0
    top_score   = candidates[0]["final_score"] if candidates else 0

    summary_data = [
        ["Metric", "Value"],
        ["Total Candidates Analyzed", str(total)],
        ["Strong Matches (≥70%)",     str(above_70)],
        ["Acceptable Matches (≥50%)", str(above_50)],
        ["Average Score",             f"{avg_score}%"],
        ["Top Score",                 f"{top_score}%"],
    ]

    summary_table = Table(summary_data, colWidths=[9 * cm, 8 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, 0), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f9f9f9")]),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("FONTSIZE",       (0, 1), (-1, -1), 9),
        ("PADDING",        (0, 0), (-1, -1), 6),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * cm))

    # ── Candidate results ───────────────────────────────────────
    elements.append(Paragraph("Candidate Rankings", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.5,
                               color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 0.3 * cm))

    for i, candidate in enumerate(candidates, start=1):
        score      = candidate["final_score"]
        rec        = candidate.get("recommendation", "")

        # Score color
        if score >= 70:
            score_color = colors.HexColor("#28a745")
        elif score >= 50:
            score_color = colors.HexColor("#ffc107")
        else:
            score_color = colors.HexColor("#dc3545")

        # Candidate header row
        header_data = [[
            f"#{i}  {candidate.get('name', 'Unknown')}",
            f"{score}%"
        ]]
        header_table = Table(header_data, colWidths=[13 * cm, 4 * cm])
        header_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, -1), colors.HexColor("#f5f5f5")),
            ("FONTNAME",    (0, 0), (0, 0),   "Helvetica-Bold"),
            ("FONTNAME",    (1, 0), (1, 0),   "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 11),
            ("TEXTCOLOR",   (1, 0), (1, 0),   score_color),
            ("ALIGN",       (1, 0), (1, 0),   "RIGHT"),
            ("PADDING",     (0, 0), (-1, -1), 7),
            ("ROUNDEDCORNERS", [4]),
        ]))
        elements.append(header_table)

        # Score breakdown table
        breakdown_data = [
            ["Skills", "Experience", "Education", "Semantic", "Recommendation"],
            [
                f"{candidate.get('skill_score', 0)}%",
                f"{candidate.get('experience_score', 0)}%",
                f"{candidate.get('education_score', 0)}%",
                f"{candidate.get('semantic_score', 0)}%",
                rec,
            ]
        ]
        breakdown_table = Table(
            breakdown_data,
            colWidths=[3 * cm, 3 * cm, 3 * cm, 3 * cm, 5 * cm]
        )
        breakdown_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
            ("GRID",        (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
            ("PADDING",     (0, 0), (-1, -1), 5),
        ]))
        elements.append(breakdown_table)

        # Contact info
        email = candidate.get("email", "")
        phone = candidate.get("phone", "")
        if email or phone:
            contact = f"📧 {email}" if email else ""
            if phone:
                contact += f"   📞 {phone}"
            elements.append(Spacer(1, 0.15 * cm))
            elements.append(Paragraph(contact, small_style))

        # Matched / missing skills
        matched = candidate.get("matched_skills", [])
        missing = candidate.get("missing_skills", [])
        if matched:
            elements.append(Paragraph(
                f"<b>Matched:</b> {', '.join(matched)}", small_style))
        if missing:
            elements.append(Paragraph(
                f"<b>Missing:</b> {', '.join(missing)}", small_style))

        # Explanation
        explanation = candidate.get("explanation", "")
        if explanation:
            elements.append(Paragraph(explanation, small_style))

        elements.append(Spacer(1, 0.4 * cm))
        elements.append(HRFlowable(
            width="100%", thickness=0.3,
            color=colors.HexColor("#eeeeee")
        ))
        elements.append(Spacer(1, 0.2 * cm))

    # ── Footer ──────────────────────────────────────────────────
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", thickness=0.5,
                               color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(Paragraph(
        "Generated by CV Matching System — AI-powered candidate ranking",
        ParagraphStyle("Footer", parent=styles["Normal"],
                       fontSize=8, textColor=colors.HexColor("#aaaaaa"),
                       alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()