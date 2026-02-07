from pathlib import Path

TITLE = "Table 14.3.1 Summary of Treatment-Emergent Adverse Events (Safety Population)"
FOOTNOTE = "Every subject is counted a single time for each applicable row and column."


def test_example_rtf_fixture_exists(test_data_dir: Path) -> None:
    """Assert the RTF fixture file exists."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"
    assert rtf_path.exists()


def test_example_rtf_fixture_contains_markers(test_data_dir: Path) -> None:
    """Assert the RTF fixture contains expected markers."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"
    content = rtf_path.read_text(encoding="utf-8", errors="ignore")
    assert "{\\rtf" in content
    assert TITLE in content
    assert FOOTNOTE in content
