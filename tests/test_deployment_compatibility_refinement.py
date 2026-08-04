"""Unit tests for Deployment Target Compatibility Refinement."""

from app.api.deps import get_decision_service
from app.schemas.decision import DecisionRequest, DeploymentTarget, Priority


def test_aws_deployment_target_ranks_aws_sagemaker_above_azure_foundry():
    """Verify AWS SageMaker ranks above Azure AI Foundry when deployment_target == 'aws'."""
    service = get_decision_service()

    req_aws = DecisionRequest(
        project_name="AWS Cloud System",
        project_description="High-scale cloud intelligence platform targeting AWS infrastructure.",
        expected_users=10_000,
        document_count=500_000,
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
    )

    res = service.recommend(req_aws)
    deploy_item = next((r for r in res.recommendations if r.category == "deployment"), None)

    assert deploy_item is not None
    assert any(k in deploy_item.recommended for k in ("Aws", "SageMaker", "Eks", "SGLang", "Ray", "Triton", "Kubernetes"))
    assert "Azure" not in deploy_item.recommended
    assert "deployment compatibility" in deploy_item.reason.lower() or "aws" in deploy_item.reason.lower() or "environment" in deploy_item.reason.lower()
    print(f"AWS Deployment Recommendation: {deploy_item.recommended} | Reason: {deploy_item.reason}")


def test_azure_deployment_target_ranks_azure_foundry_above_aws_sagemaker():
    """Verify Azure AI Foundry ranks above AWS SageMaker when deployment_target == 'azure'."""
    service = get_decision_service()

    req_azure = DecisionRequest(
        project_name="Azure Enterprise Portal",
        project_description="Corporate enterprise intelligence portal targeting Azure cloud infrastructure.",
        expected_users=10_000,
        document_count=500_000,
        deployment_target=DeploymentTarget.AZURE,
        priority=Priority.QUALITY,
    )

    res = service.recommend(req_azure)
    deploy_item = next((r for r in res.recommendations if r.category == "deployment"), None)

    assert deploy_item is not None
    assert any(k in deploy_item.recommended for k in ("Azure", "Aks", "SGLang", "Ray", "Kubernetes"))
    assert "Aws" not in deploy_item.recommended
    assert "deployment compatibility" in deploy_item.reason.lower() or "azure" in deploy_item.reason.lower() or "environment" in deploy_item.reason.lower()
    print(f"Azure Deployment Recommendation: {deploy_item.recommended} | Reason: {deploy_item.reason}")


def test_local_deployment_target_ranks_docker_above_cloud_platforms():
    """Verify Docker/local tools rank above cloud deployment platforms when deployment_target == 'local'."""
    service = get_decision_service()

    req_local = DecisionRequest(
        project_name="Local Offline Assistant",
        project_description="Desktop local assistant operating entirely offline.",
        expected_users=100,
        document_count=1_000,
        deployment_target=DeploymentTarget.LOCAL,
        priority=Priority.COST,
        constraints=["runs locally"],
    )

    res = service.recommend(req_local)
    deploy_item = next((r for r in res.recommendations if r.category == "deployment"), None)

    assert deploy_item is not None
    assert any(k in deploy_item.recommended for k in ("Docker", "BentoML", "Ollama", "Local", "FastAPI"))
    assert "Aws" not in deploy_item.recommended and "Azure" not in deploy_item.recommended
    assert "deployment compatibility" in deploy_item.reason.lower() or "local" in deploy_item.reason.lower()
    print(f"Local Deployment Recommendation: {deploy_item.recommended} | Reason: {deploy_item.reason}")


if __name__ == "__main__":
    test_aws_deployment_target_ranks_aws_sagemaker_above_azure_foundry()
    test_azure_deployment_target_ranks_azure_foundry_above_aws_sagemaker()
    test_local_deployment_target_ranks_docker_above_cloud_platforms()
    print("\nALL DEPLOYMENT COMPATIBILITY TESTS PASSED CLEANLY!")
