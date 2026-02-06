from pathlib import Path


TITLE = (
    "Table 14.3.1 Summary of Treatment-Emergent Adverse Events "
    "(Safety Population)"
)
FOOTNOTE = (
    "Every subject is counted a single time for each applicable row and column."
)
RTF_PATH = Path("tests/data/rtf/ae_summary_example.rtf")


def test_example_rtf_fixture_exists() -> None:
    """Assert the RTF fixture file exists."""
    assert RTF_PATH.exists()


def test_example_rtf_fixture_contains_markers() -> None:
    """Assert the RTF fixture contains expected markers."""
    content = RTF_PATH.read_text(encoding="utf-8", errors="ignore")
    assert "{\\rtf" in content
    assert TITLE in content
    assert FOOTNOTE in content
