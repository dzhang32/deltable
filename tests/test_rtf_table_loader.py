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
    should_xfail: bool = False
    xfail_reason: str | None = None


VARIANT_CASES = [
    VariantCase(name="multiline_headers"),
    VariantCase(name="indented_group_rows"),
    VariantCase(name="repeating_header_row"),
    VariantCase(
        name="spanning_header_horizontal_merge",
        should_xfail=True,
        xfail_reason="Horizontal merged spanner headers are not yet supported.",
    ),
    VariantCase(
        name="vertical_merge_stub_column",
        should_xfail=True,
        xfail_reason="Vertical merged first-column stubs are not yet supported.",
    ),
    VariantCase(
        name="unicode_superscript_symbols",
        should_xfail=True,
        xfail_reason="Unicode and superscript text normalization is incomplete.",
    ),
]


def _variant_parameters() -> list[pytest.ParameterSet]:
    """Build variant parameters with strict xfail markers."""
    params: list[pytest.ParameterSet] = []
    for case in VARIANT_CASES:
        marks = []
        if case.should_xfail:
            marks.append(
                pytest.mark.xfail(
                    strict=True,
                    reason=case.xfail_reason or "Known unsupported formatting variant.",
                )
            )
        params.append(pytest.param(case, id=case.name, marks=marks))
    return params


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
