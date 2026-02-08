import re
from pathlib import Path

import pytest

from deltable.rtf_to_html import (
    convert_rtf_to_html,
    is_soffice_available,
)


def _normalize_html(html_text: str) -> str:
    normalized = html_text.replace("\r\n", "\n")
    normalized = re.sub(r"\b0(?:cm|in|px|pt|mm|em|rem)\b", "0", normalized)
    normalized_lines = [line.rstrip() for line in normalized.split("\n")]
    return "\n".join(normalized_lines).strip()


@pytest.mark.parametrize(
    "fixture_name",
    [
        "ds_table",
        "frq_table",
        "lb_table",
        "surv_table",
    ],
)
@pytest.mark.skipif(not is_soffice_available(), reason="soffice is unavailable")
def test_convert_rtf_fixtures_match_saved_html(
    fixture_name: str,
    test_data_dir: Path,
    tmp_path: Path,
) -> None:
    rtf_path = test_data_dir / "rtf" / f"{fixture_name}.rtf"
    expected_html_path = test_data_dir / "html" / "baseline" / f"{fixture_name}.html"

    generated_html_path = convert_rtf_to_html(
        input_path=rtf_path,
        output_dir=tmp_path,
    )

    generated_html = generated_html_path.read_text(encoding="utf-8")
    expected_html = expected_html_path.read_text(encoding="utf-8")
    assert _normalize_html(generated_html) == _normalize_html(expected_html)
