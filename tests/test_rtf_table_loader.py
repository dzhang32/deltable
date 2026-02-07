from dataclasses import dataclass
from pathlib import Path

import polars as pl
from polars.testing import assert_frame_equal
import pytest

from deltable.rtf_table import load_rtf_table


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


def test_load_rtf_table_returns_polars_dataframe(test_data_dir: Path) -> None:
    """Load the RTF fixture into a non-empty Polars DataFrame."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"

    dataframe = load_rtf_table(rtf_path)

    assert isinstance(dataframe, pl.DataFrame)
    assert dataframe.columns == EXPECTED_COLUMNS
    assert dataframe.height == 11
    assert dataframe.dtypes == [pl.String] * len(EXPECTED_COLUMNS)


def test_load_rtf_table_matches_expected_csv_exactly(test_data_dir: Path) -> None:
    """Match the parsed RTF DataFrame to the expected CSV fixture exactly."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_baseline.rtf"
    csv_path = test_data_dir / "csv" / "ae_summary_baseline.csv"

    expected_dataframe = pl.read_csv(
        csv_path,
        infer_schema_length=0,
        missing_utf8_is_empty_string=True,
    )
    actual_dataframe = load_rtf_table(rtf_path)

    assert_frame_equal(actual_dataframe, expected_dataframe)


@pytest.mark.parametrize("case", _variant_parameters())
def test_load_rtf_table_variant_matches_expected_csv(
    test_data_dir: Path,
    case: VariantCase,
) -> None:
    """Match each generated variant against its CSV expectation."""
    rtf_path = test_data_dir / "rtf" / f"{case.name}.rtf"
    csv_path = test_data_dir / "csv" / f"{case.name}.csv"

    expected_dataframe = pl.read_csv(
        csv_path,
        infer_schema_length=0,
        missing_utf8_is_empty_string=True,
    )
    actual_dataframe = load_rtf_table(rtf_path)

    assert_frame_equal(actual_dataframe, expected_dataframe)


def test_load_rtf_table_drops_pagination_repeated_header_rows(
    test_data_dir: Path,
) -> None:
    """Drop repeated mid-table header rows introduced by pagination."""
    rtf_path = test_data_dir / "rtf" / "pagination_repeated_headers.rtf"
    dataframe = load_rtf_table(rtf_path)

    rows = dataframe.to_dicts()
    assert not any(
        row["Category"] == ""
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
    dataframe = load_rtf_table(rtf_path)

    group_rows = [
        row for row in dataframe.to_dicts() if row["Category"] == "System Organ Class"
    ]
    assert len(group_rows) == 1
    group_row = group_rows[0]

    for column in EXPECTED_COLUMNS[1:]:
        assert group_row[column] == ""


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
    dataframe = load_rtf_table(rtf_path)

    assert dataframe.columns[:2] == ["System Organ Class", "Preferred Term"]
    rows = dataframe.to_dicts()
    assert any(
        row["System Organ Class"] == "" and row["Preferred Term"] == "Tachycardia"
        for row in rows
    )
    assert any(
        row["System Organ Class"] == "" and row["Preferred Term"] == "Headache"
        for row in rows
    )
    assert any(row["System Organ Class"] == "Cardiac disorders" for row in rows)
    assert any(row["System Organ Class"] == "Nervous system disorders" for row in rows)
