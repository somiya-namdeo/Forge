"""FastAPI router for Forge Reports module."""
from fastapi import APIRouter, status, Response
from app.schemas.report import ArchitectureReport, ReportGenerationRequest
from app.reports.report_generator import ReportGenerator
from app.reports.export_pdf import PDFExporter

router = APIRouter(prefix="/reports", tags=["Reports"])

report_generator = ReportGenerator()
pdf_exporter = PDFExporter()


@router.post(
    "/generate",
    response_model=ArchitectureReport,
    status_code=status.HTTP_200_OK,
    summary="Generate Architecture Report",
    description="Generate a comprehensive architecture decision report from Forge session data.",
)
def generate_report(request: ReportGenerationRequest) -> ArchitectureReport:
    """Generate synchronous architecture report."""
    request_data = request.model_dump()
    return report_generator.generate_report(request_data)


@router.post(
    "/pdf",
    status_code=status.HTTP_200_OK,
    summary="Generate Architecture Report PDF",
    description="Generate a PDF export of the architecture decision report.",
)
def generate_report_pdf(request: ReportGenerationRequest) -> Response:
    """Generate synchronous PDF architecture report."""
    request_data = request.model_dump()
    report = report_generator.generate_report(request_data)
    pdf_bytes = pdf_exporter.export(report)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="forge_report.pdf"'
        }
    )
