from pathlib import Path

import pytest

from deltable.compare import compare_html_tables
from deltable.error import HtmlComparisonError


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("baseline/ds_table.html", "baseline/ds_table.html"),
        ("baseline/frq_table.html", "baseline/frq_table.html"),
        ("baseline/lb_table.html", "baseline/lb_table.html"),
        ("baseline/surv_table.html", "baseline/surv_table.html"),
        ("baseline/ds_table.html", "variants/ds_table_changed_values.html"),
    ],
    ids=[
        "ds_identical",
        "frq_identical",
        "lb_identical",
        "surv_identical",
        "data_differences_ignored",
    ],
)
def test_structure_match(left: str, right: str, test_data_dir: Path) -> None:
    html_dir = test_data_dir / "html"

    result = compare_html_tables(html_dir / left, html_dir / right)

    assert result.structure_match is True


@pytest.mark.parametrize(
    ("left", "right", "expected_in_summary"),
    [
        ("baseline/ds_table.html", "variants/ds_table_minus_1_column.html", "column"),
        ("baseline/ds_table.html", "variants/ds_table_swapped_rows.html", "row order"),
        ("baseline/ds_table.html", "baseline/lb_table.html", "table count"),
        ("baseline/lb_table.html", "variants/lb_table_minus_1_table.html", "table count"),
    ],
    ids=[
        "column_removed",
        "row_order_swapped",
        "different_table_counts",
        "table_removed",
    ],
)
def test_structure_mismatch(
    left: str,
    right: str,
    expected_in_summary: str,
    test_data_dir: Path,
) -> None:
    html_dir = test_data_dir / "html"

    result = compare_html_tables(html_dir / left, html_dir / right)

    assert result.structure_match is False
    assert expected_in_summary in result.summary


def test_raises_for_missing_file(baseline_dir: Path) -> None:
    existing = baseline_dir / "ds_table.html"
    missing = baseline_dir / "nonexistent.html"

    with pytest.raises(HtmlComparisonError, match="does not exist"):
        compare_html_tables(missing, existing)


def test_raises_when_no_table_found(tmp_path: Path) -> None:
    left = tmp_path / "left.html"
    right = tmp_path / "right.html"
    left.write_text(
        "<html><body><p>no table</p></body></html>\n",
        encoding="utf-8",
    )
    right.write_text(
        "<html><body><p>no table</p></body></html>\n",
        encoding="utf-8",
    )

    with pytest.raises(HtmlComparisonError, match="Unable to parse HTML tables"):
        compare_html_tables(left, right)
