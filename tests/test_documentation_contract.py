from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_and_evidence_placeholders_cover_project_handoff() -> None:
    readme = (ROOT / "README.md").read_text()
    evidence_files = {
        path.name for path in (ROOT / "docs/evidence").glob("*.md")
    }

    for expected in [
        "Service URLs",
        "Environment Variables",
        "Configure Local Source Data",
        "Run the Pipeline",
        "dbt Documentation",
        "Redash Dashboard",
        "Export Redash Assets",
        "Failure Alerts",
    ]:
        assert expected in readme

    assert {
        "tech-stack-flow.md",
        "dbt-lineage-screenshot.md",
        "redash-dashboard-screenshot.md",
        "alert-placeholder.md",
    } <= evidence_files
