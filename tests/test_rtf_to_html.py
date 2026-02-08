from pathlib import Path

import pytest

from deltable.compare import compare_html_tables
from deltable.rtf_to_html import (
    convert_rtf_to_html,
    is_soffice_available,
)


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

    result = compare_html_tables(generated_html_path, expected_html_path)
    assert result.structure_match, result.summary
