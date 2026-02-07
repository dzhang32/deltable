from pathlib import Path

import polars as pl
from polars.testing import assert_frame_equal

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


def test_load_rtf_table_returns_polars_dataframe(test_data_dir: Path) -> None:
    """Load the RTF fixture into a non-empty Polars DataFrame."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_example.rtf"

    dataframe = load_rtf_table(rtf_path)

    assert isinstance(dataframe, pl.DataFrame)
    assert dataframe.columns == EXPECTED_COLUMNS
    assert dataframe.height == 11
    assert dataframe.dtypes == [pl.String] * len(EXPECTED_COLUMNS)


def test_load_rtf_table_matches_expected_csv_exactly(test_data_dir: Path) -> None:
    """Match the parsed RTF DataFrame to the expected CSV fixture exactly."""
    rtf_path = test_data_dir / "rtf" / "ae_summary_example.rtf"
    csv_path = test_data_dir / "csv" / "ae_summary_example.csv"

    expected_dataframe = pl.read_csv(
        csv_path,
        infer_schema_length=0,
        missing_utf8_is_empty_string=True,
    )
    actual_dataframe = load_rtf_table(rtf_path)

    assert_frame_equal(actual_dataframe, expected_dataframe)
