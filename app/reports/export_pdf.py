import io
from app.schemas.report import ArchitectureReport

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
            # Fallback if reportlab fails to load
            return b"%PDF-1.4\n%ReportLab not available. Please install reportlab.\n"
            
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = styles['Heading1']
        title_style.alignment = 1 # Center
        h2_style = styles['Heading2']
        h3_style = styles['Heading3']
        normal_style = styles['Normal']
        
        Story = []
        
        # Header
        Story.append(Paragraph(f"Forge AI: {report.title}", title_style))
        Story.append(Paragraph(f"Generated at: {report.generated_at}", styles['Italic']))
        Story.append(Spacer(1, 12))
        
        # Project Info
        Story.append(Paragraph("1. Project Information", h2_style))
        info_data = [
            ["Project Name", report.project_info.project_name],
            ["Domain", report.project_info.domain],
            ["Scale", report.project_info.scale],
            ["Budget", report.project_info.budget],
            ["Target", report.project_info.deployment_target],
            ["Optimization", report.project_info.optimization_priority],
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
        
        # Architecture Summary
        Story.append(Paragraph("2. Selected Architecture", h2_style))
        arch_data = [["Component", "Selection"]]
        for k, v in report.architecture_summary.components.items():
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
        
        # Metrics
        Story.append(Paragraph("3. Scores & Metrics", h2_style))
        m = report.metrics
        def fmt(val, suffix=""):
            if val is None:
                return "Not Evaluated"
            return f"{val:.2f}{suffix}"
            
        metrics_data = [
            ["Decision Engine Confidence", fmt(m.overall_score)],
            ["Benchmark Score", fmt(m.benchmark_score)],
            ["Evaluation Score", fmt(m.evaluation_score)],
            ["Pass Rate", fmt(m.success_rate, "%")],
            ["Median Latency", fmt(m.median_latency_ms, " ms")],
        ]
        t3 = Table(metrics_data, colWidths=[200, 250])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.grey)
        ]))
        Story.append(t3)
        Story.append(Spacer(1, 20))
        
        # Readiness
        Story.append(Paragraph("4. Deployment Readiness", h2_style))
        Story.append(Paragraph(f"Status: {report.readiness_summary.risk_summary}", normal_style))
        Story.append(Spacer(1, 12))
        if report.deployment_checklist:
            Story.append(Paragraph("Checklist:", h3_style))
            for item in report.deployment_checklist:
                Story.append(Paragraph(f"• <b>{item.category}</b>: {item.task} ({item.criticality})", normal_style))
                Story.append(Paragraph(f"  {item.description}", normal_style))
                Story.append(Spacer(1, 4))
        
        # Build PDF
        doc.build(Story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
