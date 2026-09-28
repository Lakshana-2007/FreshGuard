"""
reports.py — FreshGuard Professional PDF Report Generator
Generates PDF reports for food freshness assessment using ReportLab.
"""

import json
from io import BytesIO
from datetime import datetime, timezone
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# FreshGuard Color System
PRIMARY = colors.HexColor("#0f172a")      # Slate 900
EMERALD = colors.HexColor("#059669")      # Emerald 600
TEXT_MAIN = colors.HexColor("#1e293b")    # Slate 800
TEXT_MUTED = colors.HexColor("#64748b")   # Slate 500
BG_LIGHT = colors.HexColor("#f8fafc")     # Slate 50
BORDER_COLOR = colors.HexColor("#e2e8f0") # Slate 200

# Classification status badge colors
STATUS_COLORS: Dict[str, Dict[str, Any]] = {
    "Fresh": {"text": colors.HexColor("#166534"), "bg": colors.HexColor("#dcfce7"), "border": colors.HexColor("#86efac")},
    "Good": {"text": colors.HexColor("#3f6212"), "bg": colors.HexColor("#ecfccb"), "border": colors.HexColor("#bef264")},
    "Acceptable": {"text": colors.HexColor("#854d0e"), "bg": colors.HexColor("#fef9c3"), "border": colors.HexColor("#fde047")},
    "Near Spoilage": {"text": colors.HexColor("#9a3412"), "bg": colors.HexColor("#ffedd5"), "border": colors.HexColor("#fdba74")},
    "Spoiled": {"text": colors.HexColor("#991b1b"), "bg": colors.HexColor("#fee2e2"), "border": colors.HexColor("#fca5a5")},
}


def _safe_json_loads(data: Any) -> Dict[str, Any]:
    if not data:
        return {}
    if isinstance(data, dict):
        return data
    try:
        return json.loads(str(data))
    except Exception:
        return {}


def generate_freshness_pdf_report(analysis: Any, user: Any) -> bytes:
    """
    Generates a PDF freshness report for the given FreshnessAnalysis and User.
    Returns raw PDF bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    style_brand = ParagraphStyle(
        "BrandName",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=EMERALD,
    )
    style_tagline = ParagraphStyle(
        "BrandTagline",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=TEXT_MUTED,
    )
    style_title = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        alignment=2, # Right aligned header title
    )
    style_subtitle = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT_MUTED,
        alignment=2,
    )
    style_section_h2 = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=8,
        spaceAfter=4,
    )
    style_body = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_MAIN,
    )
    style_body_bold = ParagraphStyle(
        "BodyTextBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=TEXT_MAIN,
    )
    style_disclaimer = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=TEXT_MUTED,
    )

    story = []

    # -------------------------------------------------------------------------
    # A. Header Block
    # -------------------------------------------------------------------------
    report_id = f"FG-RPT-{analysis.id:06d}" if getattr(analysis, "id", None) else "FG-RPT-000000"
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    header_left = [
        Paragraph("🌿 FreshGuard", style_brand),
        Paragraph("AI-Powered Food Freshness Platform", style_tagline),
    ]
    header_right = [
        Paragraph("Food Freshness Assessment Report", style_title),
        Paragraph(f"<b>Report ID:</b> {report_id} &bull; <b>Generated:</b> {now_str}", style_subtitle),
    ]

    header_table = Table([[header_left, header_right]], colWidths=[3.25 * inch, 4.25 * inch])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=EMERALD, spaceBefore=0, spaceAfter=12))

    # -------------------------------------------------------------------------
    # B. Metadata / Food Information
    # -------------------------------------------------------------------------
    user_name = getattr(user, "full_name", "Authenticated User")
    user_email = getattr(user, "email", "N/A")
    user_role = getattr(user, "role", "consumer").replace("_", " ").title()
    item_name = getattr(analysis, "item_name", None) or "Unspecified Food Item"
    created_at = getattr(analysis, "created_at", None)
    scan_date_str = created_at.strftime("%Y-%m-%d %H:%M UTC") if created_at else now_str

    info_data = [
        [
            Paragraph("<b>Food Type / Classification:</b>", style_body),
            Paragraph(str(item_name), style_body_bold),
            Paragraph("<b>Analysis ID:</b>", style_body),
            Paragraph(str(getattr(analysis, "id", "N/A")), style_body),
        ],
        [
            Paragraph("<b>User / Inspector:</b>", style_body),
            Paragraph(f"{user_name} ({user_role})", style_body),
            Paragraph("<b>User Email:</b>", style_body),
            Paragraph(user_email, style_body),
        ],
        [
            Paragraph("<b>Raw Model Class:</b>", style_body),
            Paragraph(str(getattr(analysis, "predicted_class", "N/A")), style_body),
            Paragraph("<b>Scan Timestamp:</b>", style_body),
            Paragraph(scan_date_str, style_body),
        ],
    ]

    info_table = Table(info_data, colWidths=[1.8 * inch, 2.2 * inch, 1.3 * inch, 2.2 * inch])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # C. AI Assessment Results Summary
    # -------------------------------------------------------------------------
    story.append(Paragraph("AI Assessment Overview", style_section_h2))

    classification = getattr(analysis, "classification", "Acceptable")
    badge_cfg = STATUS_COLORS.get(classification, STATUS_COLORS["Acceptable"])
    quality_score = int(getattr(analysis, "quality_score", 0))
    confidence_pct = f"{float(getattr(analysis, 'confidence', 0.0)) * 100:.1f}%"
    spoilage_pct = f"{float(getattr(analysis, 'spoilage_probability', 0.0)) * 100:.1f}%"

    style_status_badge = ParagraphStyle(
        "StatusBadge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=16,
        textColor=badge_cfg["text"],
        alignment=1, # Center
    )
    style_metric_val = ParagraphStyle(
        "MetricVal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=PRIMARY,
        alignment=1,
    )
    style_metric_lbl = ParagraphStyle(
        "MetricLbl",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=TEXT_MUTED,
        alignment=1,
    )

    kpi_data = [
        [
            Paragraph("FRESHNESS STATUS", style_metric_lbl),
            Paragraph("QUALITY SCORE", style_metric_lbl),
            Paragraph("MODEL CONFIDENCE", style_metric_lbl),
            Paragraph("SPOILAGE PROBABILITY", style_metric_lbl),
        ],
        [
            Paragraph(classification.upper(), style_status_badge),
            Paragraph(f"{quality_score} / 100", style_metric_val),
            Paragraph(confidence_pct, style_metric_val),
            Paragraph(spoilage_pct, style_metric_val),
        ],
    ]

    kpi_table = Table(kpi_data, colWidths=[1.9 * inch, 1.8 * inch, 1.9 * inch, 1.9 * inch])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 1), badge_cfg["bg"]),
        ("BOX", (0, 0), (0, 1), 1, badge_cfg["border"]),
        ("BACKGROUND", (1, 0), (-1, -1), BG_LIGHT),
        ("BOX", (1, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # D. Visual Analysis Breakdown (OpenCV Metrics)
    # -------------------------------------------------------------------------
    story.append(Paragraph("Visual Analysis Metrics (OpenCV Computer Vision)", style_section_h2))

    color_metrics = _safe_json_loads(getattr(analysis, "color_metrics", None))
    texture_metrics = _safe_json_loads(getattr(analysis, "texture_metrics", None))

    dom_hex = color_metrics.get("dominant_color_hex", "N/A")
    discoloration = f"{float(color_metrics.get('discoloration_index', 0.0)) * 100:.1f}%"
    browning = f"{float(color_metrics.get('browning_index', 0.0)) * 100:.1f}%"
    dark_spots = f"{float(color_metrics.get('dark_spot_ratio', 0.0)) * 100:.1f}%"
    saturation = f"{float(color_metrics.get('mean_saturation', 0.0)) * 100:.1f}%"
    brightness = f"{float(color_metrics.get('mean_brightness', 0.0)):.1f} / 255"

    uniformity = f"{float(texture_metrics.get('texture_uniformity', 0.0)) * 100:.1f}%"
    roughness = f"{float(texture_metrics.get('surface_roughness', 0.0)):.2f}"
    contrast = f"{float(texture_metrics.get('local_contrast', 0.0)):.2f}"

    metrics_headers = [
        Paragraph("<b>Colour & Surface Feature</b>", style_body_bold),
        Paragraph("<b>Measured Value</b>", style_body_bold),
        Paragraph("<b>Texture & Structural Metric</b>", style_body_bold),
        Paragraph("<b>Measured Value</b>", style_body_bold),
    ]

    metrics_rows = [
        metrics_headers,
        [
            Paragraph("Dominant Colour Hex", style_body),
            Paragraph(f"<code>{dom_hex}</code>", style_body),
            Paragraph("Texture Uniformity", style_body),
            Paragraph(uniformity, style_body),
        ],
        [
            Paragraph("Discoloration Index", style_body),
            Paragraph(discoloration, style_body),
            Paragraph("Surface Roughness", style_body),
            Paragraph(roughness, style_body),
        ],
        [
            Paragraph("Browning Index", style_body),
            Paragraph(browning, style_body),
            Paragraph("Local Contrast Variance", style_body),
            Paragraph(contrast, style_body),
        ],
        [
            Paragraph("Dark Spot Ratio", style_body),
            Paragraph(dark_spots, style_body),
            Paragraph("Feature Status", style_body),
            Paragraph("Extracted cleanly via OpenCV", style_body),
        ],
        [
            Paragraph("Mean Saturation", style_body),
            Paragraph(saturation, style_body),
            Paragraph("Mean Brightness", style_body),
            Paragraph(brightness, style_body),
        ],
    ]

    metrics_table = Table(metrics_rows, colWidths=[2.1 * inch, 1.65 * inch, 2.1 * inch, 1.65 * inch])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BG_LIGHT),
        ("LINEBELOW", (0, 0), (-1, 0), 1, PRIMARY),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # E. Interpretation Section
    # -------------------------------------------------------------------------
    story.append(Paragraph("Assessment Interpretation & Methodology", style_section_h2))

    interp_text = (
        f"The visual analysis for <b>{item_name}</b> resulted in a quality score of <b>{quality_score}/100</b> "
        f"with a predicted freshness category of <b>{classification}</b> (Confidence: {confidence_pct}, "
        f"Spoilage Risk: {spoilage_pct}).<br/>"
        "<b>Visual Assessment Note:</b> This assessment uses non-invasive visual feature extraction "
        "including HSV colour space distribution, browning index metrics, surface texture uniformity, "
        "and MobileNetV2 deep neural network classification. The visual score is a transparent weighted synthesis "
        "of predicted class probability, surface discoloration, and texture smoothness."
    )
    story.append(Paragraph(interp_text, style_body))
    story.append(Spacer(1, 6))

    system_note = (
        "<b>System Capability Scope:</b> FreshGuard evaluates overall visual condition, color fidelity, "
        "and surface degradation. The system does not claim to detect internal mold, internal bruising, "
        "or mechanical damage using dedicated trained detectors."
    )
    story.append(Paragraph(system_note, style_body))
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # F. Disclaimer Section
    # -------------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_COLOR, spaceBefore=0, spaceAfter=8))
    disclaimer_text = (
        "<b>Official Disclaimer:</b> This report is an automated AI-assisted visual assessment produced by "
        "FreshGuard. It is intended for monitoring, inventory quality sorting, and shelf-life tracking purposes. "
        "It should not replace official laboratory analysis or professional food safety inspection by regulatory authorities."
    )
    story.append(Paragraph(disclaimer_text, style_disclaimer))

    # Build PDF document
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
