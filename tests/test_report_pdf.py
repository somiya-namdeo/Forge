import pytest
from app.schemas.report import (
    ArchitectureReport,
    ProjectInfo,
    ArchitectureDetails,
    ArchitectureRationale,
    ReadinessSummary,
    ChecklistItem
)
from app.reports.export_pdf import PDFExporter

def test_pdf_export_generates_valid_pdf():
    # Arrange
    exporter = PDFExporter()
    
    report = ArchitectureReport(
        id="test-report-123",
        title="Architecture Decision Report",
        generated_at="2026-08-29 10:00:00 UTC",
        project_profile=ProjectInfo(
            project_name="Legal AI",
            domain="legal",
            scale="enterprise",
            budget="$1000/mo",
            deployment_target="aws",
            optimization_priority="balanced"
        ),
        architecture=ArchitectureDetails(
            components={
                "llms": "Anthropic Claude",
                "vectordbs": "Qdrant"
            },
            decision_signals={
                "privacy": "true"
            },
            rationale=[
                ArchitectureRationale(category="llms", recommended="Anthropic Claude", reason="Quality"),
                ArchitectureRationale(category="vectordbs", recommended="Qdrant", reason="Scale")
            ]
        ),
        deployment_readiness=ReadinessSummary(
            ready=True,
            pass_count=5,
            warn_count=0,
            risk_summary="All checks passed.",
            overall_confidence=0.9
        ),
        checklist=[
            ChecklistItem(
                id="c-1",
                category="Security",
                task="Enable SSO",
                description="Use SAML for AWS.",
                criticality="Required",
                completed=True
            )
        ],
        cost_breakdown=[],
        estimated_monthly_cost="$500"
    )

    # Act
    pdf_bytes = exporter.export(report)

    # Assert
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000, "PDF size is abnormally small. Possibly a mock output?"
    assert pdf_bytes.startswith(b"%PDF-"), "Output does not have a valid PDF header"
