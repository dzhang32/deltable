from dataclasses import fields
from pathlib import Path

import polars as pl

from deltable.comparison import (
    TableComparisonResult,
    compare_dataframes,
    compare_rtf_tables,
)
from deltable.rtf_table import load_rtf_table


def test_table_comparison_result_keeps_only_public_contract_fields() -> None:
    """Expose only category and summary in comparison result."""
    field_names = tuple(field.name for field in fields(TableComparisonResult))

    assert field_names == ("category", "summary")


def test_compare_dataframes_identical() -> None:
    """Classify fully matching frames as identical."""
    left = pl.DataFrame({"Category": ["A", "B"], "Total | n": ["1", "2"]})
    right = pl.DataFrame({"Category": ["A", "B"], "Total | n": ["1", "2"]})

    result = compare_dataframes(left, right)

    assert result.category == "identical"
    assert "identical" in result.summary.lower()


def test_compare_dataframes_detects_structure_difference_for_value_mismatch() -> None:
    """Classify value mismatches as structure differences."""
    left = pl.DataFrame({"Category": ["A", "B"], "Total | n": ["1", "2"]})
    right = pl.DataFrame({"Category": ["A", "B"], "Total | n": ["1", "3"]})

    result = compare_dataframes(left, right)

    assert result.category == "structure_differences"
    assert "value mismatch" in result.summary.lower()
    assert "total | n" in result.summary.lower()


def test_compare_dataframes_detects_structure_difference_for_column_order() -> None:
    """Classify differing column order as a structural mismatch."""
    left = pl.DataFrame({"Category": ["A", "B"], "Total | n": ["1", "2"]})
    right = pl.DataFrame({"Total | n": ["1", "2"], "Category": ["A", "B"]})

    result = compare_dataframes(left, right)

    assert result.category == "structure_differences"
    assert "column" in result.summary.lower()


def test_compare_dataframes_detects_structure_difference_for_row_count() -> None:
    """Classify differing row count as a structural mismatch."""
    left = pl.DataFrame({"Category": ["A", "B"], "Total | n": ["1", "2"]})
    right = pl.DataFrame({"Category": ["A", "B", "C"], "Total | n": ["1", "2", "3"]})

    result = compare_dataframes(left, right)

    assert result.category == "structure_differences"
    assert "row count" in result.summary.lower()


def test_compare_dataframes_applies_numeric_tolerance() -> None:
    """Treat numeric deviations within tolerance as identical."""
    left = pl.DataFrame({"id": [1, 2], "value": [10.0, 20.0]})
    right = pl.DataFrame({"id": [1, 2], "value": [10.005, 19.995]})

    within_tol = compare_dataframes(left, right, abs_tol=0.01)
    outside_tol = compare_dataframes(left, right, abs_tol=0.001)

    assert within_tol.category == "identical"
    assert outside_tol.category == "structure_differences"


def test_compare_dataframes_supports_ignore_case_and_spaces_flags() -> None:
    """Normalize case and spaces when flags are enabled."""
    left = pl.DataFrame({"id": ["01"], "term": ["Grade 3"]})
    right = pl.DataFrame({"id": ["01"], "term": ["grade    3"]})

    strict = compare_dataframes(left, right)
    normalized = compare_dataframes(
        left,
        right,
        ignore_case=True,
        ignore_spaces=True,
    )

    assert strict.category == "structure_differences"
    assert normalized.category == "identical"


def test_compare_dataframes_infers_grouped_stub_join_columns(
    test_data_dir: Path,
) -> None:
    """Compare grouped row-header tables without false differences."""
    dataframe = load_rtf_table(
        test_data_dir / "rtf" / "grouped_row_headers_vertical_merge.rtf"
    )

    result = compare_dataframes(dataframe, dataframe)

    assert result.category == "identical"


def test_compare_dataframes_stops_at_first_column_mismatch() -> None:
    """Return first mismatch based on column order and row position."""
    left = pl.DataFrame({"First": [1, 2], "Second": [10, 20]})
    right = pl.DataFrame({"First": [9, 2], "Second": [99, 20]})

    result = compare_dataframes(left, right)

    assert result.category == "structure_differences"
    assert "column 'first'" in result.summary.lower()
    assert "row 0" in result.summary.lower()


def test_compare_rtf_tables_compares_loaded_rtf_fixtures(test_data_dir: Path) -> None:
    """Compare RTF files through the convenience wrapper."""
    left_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"
    right_path = test_data_dir / "rtf" / "row_terminator_plain_row.rtf"

    result = compare_rtf_tables(left_path, right_path)

    assert result.category == "identical"


def test_compare_rtf_tables_detects_structure_difference_for_columns(
    test_data_dir: Path,
) -> None:
    """Classify differing RTF column schemas as structure differences."""
    left_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"
    right_path = test_data_dir / "rtf" / "grouped_row_headers_vertical_merge.rtf"

    result = compare_rtf_tables(left_path, right_path)

    assert result.category == "structure_differences"
    assert "column" in result.summary.lower()


def test_compare_rtf_tables_detects_structure_difference_for_row_count(
    test_data_dir: Path,
) -> None:
    """Classify differing RTF row counts as structure differences."""
    left_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"
    right_path = test_data_dir / "rtf" / "group_header_merged_spanning.rtf"

    result = compare_rtf_tables(left_path, right_path)

    assert result.category == "structure_differences"
    assert "row count" in result.summary.lower()
