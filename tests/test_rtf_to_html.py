from __future__ import annotations

from pathlib import Path

import pytest

from deltable.rtf_to_html import (
    convert_rtf_to_html,
    is_soffice_available,
)

@pytest.mark.skipif(not is_soffice_available(), reason="soffice is unavailable")
def test_convert_rtf_fixtures_match_saved_html(
    test_data_dir: Path,
    tmp_path: Path,
) -> None:
    rtf_dir = test_data_dir / "rtf"
    expected_html_dir = test_data_dir / "html"

    rtf_stems = {path.stem for path in rtf_dir.glob("*.rtf")}
    expected_stems = {path.stem for path in expected_html_dir.glob("*.html")}

    assert rtf_stems
    assert expected_stems == rtf_stems

    for rtf_path in sorted(rtf_dir.glob("*.rtf")):
        expected_html_path = expected_html_dir / f"{rtf_path.stem}.html"
        generated_html_path = convert_rtf_to_html(
            input_path=rtf_path,
            output_dir=tmp_path,
        )

        generated_html = generated_html_path.read_text(encoding="utf-8")
        expected_html = expected_html_path.read_text(encoding="utf-8")
        assert generated_html == expected_html
