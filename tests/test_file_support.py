from create_app.initializer.controller import Controller
from create_app.initializer.generator import Generator


def test_generated_paths_preserve_supported_file_locations():
    assert (
        Controller._normalize_generated_path(
            ".github/ISSUE_TEMPLATE/bug_report.md", "github"
        )
        == ".github/ISSUE_TEMPLATE/bug_report.md"
    )
    assert (
        Controller._normalize_generated_path("ci.yml", "github")
        == ".github/workflows/ci.yml"
    )
    assert (
        Controller._normalize_generated_path("docker/Dockerfile", "docker")
        == "docker/Dockerfile"
    )
    assert (
        Controller._normalize_generated_path("deployment.yml", "kubernetes")
        == "k8s/deployment.yml"
    )
    assert (
        Controller._normalize_generated_path("CONTRIBUTING.md", "community")
        == "CONTRIBUTING.md"
    )
    assert Controller._normalize_generated_path("setup.cfg", "pkg") == "setup.cfg"


def test_missing_templates_generate_useful_supported_files(tmp_path):
    generator = Generator(
        tmp_path,
        {
            "project_name": "demo_app",
            "fw_name": "fastapi",
            "framework": "fastapi",
            "dependencies": "fastapi\nuvicorn",
        },
    )

    generator._render_and_write(
        "generated/.github/workflows/ci.yml.tpl",
        ".github/workflows/ci.yml",
    )
    generator._render_and_write("generated/docker/Dockerfile.tpl", "docker/Dockerfile")
    generator._render_and_write(
        "generated/.github/ISSUE_TEMPLATE/bug_report.md.tpl",
        ".github/ISSUE_TEMPLATE/bug_report.md",
    )
    generator._render_and_write("generated/k8s/deployment.yml.tpl", "k8s/deployment.yml")

    assert "runs-on: ubuntu-latest" in (
        tmp_path / ".github" / "workflows" / "ci.yml"
    ).read_text()
    dockerfile = (tmp_path / "docker" / "Dockerfile").read_text()
    workflow = (tmp_path / ".github" / "workflows" / "ci.yml").read_text()
    assert "FROM python:" in dockerfile
    assert "pip install --upgrade pip setuptools wheel" in dockerfile
    assert "pip install --upgrade setuptools wheel" in workflow
    assert "Steps to Reproduce" in (
        tmp_path / ".github" / "ISSUE_TEMPLATE" / "bug_report.md"
    ).read_text()
    assert "kind: Deployment" in (tmp_path / "k8s" / "deployment.yml").read_text()
