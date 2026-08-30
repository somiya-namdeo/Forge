import io
from app.schemas.report import ArchitectureReport

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFExporter:
    """Exporter for generating styled PDF reports from ArchitectureReport."""

    def export(self, report: ArchitectureReport) -> bytes:
        """Export ArchitectureReport object into binary PDF content."""
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("ReportLab is not installed. Cannot generate PDF.")
            
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        
        title_style = styles['Heading1']
        title_style.alignment = 1
        h2_style = styles['Heading2']
        styles['Heading3']
        normal_style = styles['Normal']
        
        Story = []
        
        Story.append(Paragraph(f"Forge AI: {report.title}", title_style))
        Story.append(Paragraph(f"Generated at: {report.generated_at}", styles['Italic']))
        Story.append(Spacer(1, 12))
        
        Story.append(Paragraph("1. Project Profile", h2_style))
        info_data = [
            ["Project Name", report.project_profile.project_name],
            ["Domain", report.project_profile.domain],
            ["Scale", report.project_profile.scale],
            ["Budget", report.project_profile.budget],
            ["Target", report.project_profile.deployment_target],
            ["Optimization", report.project_profile.optimization_priority],
        ]
        t = Table(info_data, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        Story.append(t)
        Story.append(Spacer(1, 20))
        
        Story.append(Paragraph("2. Architecture Components", h2_style))
        arch_data = [["Category", "Selection"]]
        for k, v in report.architecture.components.items():
            arch_data.append([k.replace("_", " ").title(), str(v)])
            
        t2 = Table(arch_data, colWidths=[150, 300])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        Story.append(t2)
        Story.append(Spacer(1, 20))
        
        Story.append(Paragraph("3. Decision Signals / Constraints", h2_style))
        sig_data = []
        for k, v in report.architecture.decision_signals.items():
            sig_data.append([k.replace("_", " ").title(), str(v)])
        if not sig_data: sig_data = [["None", "-"]]
        t_sig = Table(sig_data, colWidths=[150, 300])
        t_sig.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        Story.append(t_sig)
        Story.append(Spacer(1, 20))
        
        Story.append(Paragraph("4. Why This Architecture", h2_style))
        for item in report.architecture.rationale:
            Story.append(Paragraph(f"<b>{item.category.title()} ({item.recommended}):</b> {item.reason}", normal_style))
            Story.append(Spacer(1, 6))
        Story.append(Spacer(1, 14))
        
        doc.build(Story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
