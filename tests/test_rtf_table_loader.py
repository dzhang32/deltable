from __future__ import annotations

from csv import DictReader
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from deltable.rtf_table import TableData, load_rtf_table


EXPECTED_COLUMNS = [
    "Category",
    "Placebo (N=60) | n",
    "Placebo (N=60) | (%)",
    "Low Dose (N=60) | n",
    "Low Dose (N=60) | (%)",
    "High Dose (N=60) | n",
    "High Dose (N=60) | (%)",
    "Total (N=180) | n",
    "Total (N=180) | (%)",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class VariantCase:
    """Represent one RTF formatting variant test case."""

    name: str


VARIANT_CASES = [
    VariantCase(name="multiline_headers"),
    VariantCase(name="indented_group_rows"),
    VariantCase(name="repeating_header_row"),
    VariantCase(name="spanning_header_horizontal_merge"),
    VariantCase(name="vertical_merge_stub_column"),
    VariantCase(name="unicode_superscript_symbols"),
    VariantCase(name="pagination_repeated_headers"),
    VariantCase(name="group_header_first_cell_bare_cells"),
    VariantCase(name="group_header_merged_spanning"),
    VariantCase(name="row_terminator_plain_row"),
    VariantCase(name="grouped_row_headers_vertical_merge"),
]


def _variant_parameters() -> list[pytest.ParameterSet]:
    """Build variant parameters."""
    return [pytest.param(case, id=case.name) for case in VARIANT_CASES]


def _load_csv_as_table(path: Path) -> dict[str, list[str]]:
    """Load an expected CSV fixture into a column-oriented string table."""
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV fixture is missing header row.")

        table: dict[str, list[str]] = {field: [] for field in reader.fieldnames}
        for row in reader:
            for field in reader.fieldnames:
                table[field].append(row[field] or "")

    return table


def _stringify_table(table: TableData) -> dict[str, list[str]]:
    """Convert typed table values to CSV-comparable string values."""
    return {
        column: ["" if value is None else str(value) for value in values]
        for column, values in table.items()
    }


def _table_to_rows(table: TableData) -> list[dict[str, Any]]:
    """Convert a column-oriented table into row dictionaries."""
    if not table:
        return []

    row_count = _row_count(table)
    columns = list(table.keys())
    return [
        {column: table[column][row_index] for column in columns}
        for row_index in range(row_count)
    ]


def _row_count(table: TableData) -> int:
    """Return row count for a consistent column-oriented table."""
    if not table:
        return 0

    counts = {len(values) for values in table.values()}
    if len(counts) != 1:
        raise ValueError("Table has inconsistent column lengths.")

    return next(iter(counts))


def test_load_rtf_table_returns_column_oriented_table(test_data_dir: Path) -> None:
    """Load the RTF fixture into a non-empty dict-based table."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"

    table = load_rtf_table(rtf_path)

    assert isinstance(table, dict)
    assert list(table.keys()) == EXPECTED_COLUMNS
    assert _row_count(table) == 11


def test_load_rtf_table_uses_none_for_empty_cells(test_data_dir: Path) -> None:
    """Represent empty RTF table cells as None values."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"

    table = load_rtf_table(rtf_path)

    assert table["Placebo (N=60) | (%)"][0] is None


def test_load_rtf_table_parses_numeric_columns_with_strict_inference(
    test_data_dir: Path,
) -> None:
    """Parse all-numeric columns while preserving mixed-format columns as strings."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"

    table = load_rtf_table(rtf_path)

    assert all(
        isinstance(value, int)
        for value in table["Placebo (N=60) | n"]
        if value is not None
    )
    assert all(
        isinstance(value, str)
        for value in table["Placebo (N=60) | (%)"]
        if value is not None
    )


def test_load_rtf_table_matches_expected_csv_exactly(test_data_dir: Path) -> None:
    """Match the parsed RTF content to the expected CSV fixture."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"
    csv_path = test_data_dir / "csv" / "ae_summary_baseline.csv"

    expected_table = _load_csv_as_table(csv_path)
    actual_table = _stringify_table(load_rtf_table(rtf_path))

    assert actual_table == expected_table


@pytest.mark.parametrize("case", _variant_parameters())
def test_load_rtf_table_variant_matches_expected_csv(
    test_data_dir: Path,
    case: VariantCase,
) -> None:
    """Match each generated variant against its CSV expectation."""
    rtf_path = test_data_dir / "rtf" / f"{case.name}.rtf"
    csv_path = test_data_dir / "csv" / f"{case.name}.csv"

    expected_table = _load_csv_as_table(csv_path)
    actual_table = _stringify_table(load_rtf_table(rtf_path))

    assert actual_table == expected_table


def test_load_rtf_table_drops_pagination_repeated_header_rows(
    test_data_dir: Path,
) -> None:
    """Drop repeated mid-table header rows introduced by pagination."""
    rtf_path = test_data_dir / "rtf" / "pagination_repeated_headers.rtf"
    table = load_rtf_table(rtf_path)

    rows = _table_to_rows(table)
    assert not any(
        row["Category"] is None
        and row["Placebo (N=60) | n"] == "n"
        and row["Placebo (N=60) | (%)"] == "(%)"
        for row in rows
    )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "group_header_first_cell_bare_cells",
        "group_header_merged_spanning",
    ],
)
def test_load_rtf_table_keeps_standalone_group_header_rows(
    test_data_dir: Path,
    fixture_name: str,
) -> None:
    """Keep standalone group-header rows with blank numeric cells."""
    rtf_path = test_data_dir / "rtf" / f"{fixture_name}.rtf"
    table = load_rtf_table(rtf_path)

    group_rows = [
        row for row in _table_to_rows(table) if row["Category"] == "System Organ Class"
    ]
    assert len(group_rows) == 1
    group_row = group_rows[0]

    for column in EXPECTED_COLUMNS[1:]:
        assert group_row[column] is None


def test_load_rtf_table_raises_on_inconsistent_body_row_width(tmp_path: Path) -> None:
    """Raise an error when a non-header body row has inconsistent width."""
    baseline_rtf_path = (
        Path(__file__).parent / "data" / "rtf" / "ae_summary_baseline.rtf"
    )
    rtf_text = baseline_rtf_path.read_text(encoding="utf-8", errors="ignore")

    value_cell = r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 96}\cell"
    malformed_rtf_text = rtf_text.replace(value_cell, "", 1)
    assert malformed_rtf_text != rtf_text

    malformed_path = tmp_path / "inconsistent_width.rtf"
    malformed_path.write_text(malformed_rtf_text, encoding="utf-8")

    with pytest.raises(ValueError, match="inconsistent row width"):
        load_rtf_table(malformed_path)


def test_load_rtf_table_grouped_row_headers_preserve_hierarchy(
    test_data_dir: Path,
) -> None:
    """Preserve two-stub grouped row headers without parent label propagation."""
    rtf_path = test_data_dir / "rtf" / "grouped_row_headers_vertical_merge.rtf"
    table = load_rtf_table(rtf_path)

    assert list(table.keys())[:2] == ["System Organ Class", "Preferred Term"]
    rows = _table_to_rows(table)
    assert any(
        row["System Organ Class"] is None and row["Preferred Term"] == "Tachycardia"
        for row in rows
    )
    assert any(
        row["System Organ Class"] is None and row["Preferred Term"] == "Headache"
        for row in rows
    )
    assert any(row["System Organ Class"] == "Cardiac disorders" for row in rows)
    assert any(row["System Organ Class"] == "Nervous system disorders" for row in rows)
