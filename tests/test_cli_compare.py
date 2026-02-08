from pathlib import Path

import pandas as pd
from click.testing import CliRunner

from deltable.cli import cli


def test_compare_cli(
    test_data_dir: Path,
    tmp_path: Path,
) -> None:
    """Test that the compare CLI works correctly."""
    html_dir = test_data_dir / "html"
    rtf_dir = test_data_dir / "rtf"

    baseline_html = html_dir / "baseline" / "ds_table.html"
    changed_html = html_dir / "variants" / "ds_table_changed_values.html"
    baseline_rtf = rtf_dir / "ds_table.rtf"

    input_path = tmp_path / "table_paths.csv"
    output_path = tmp_path / "comparison_results.csv"

    pd.DataFrame(
        {
            "left_path": [
                baseline_html,
                baseline_rtf,
                baseline_html,
                baseline_html,
            ],
            "right_path": [
                changed_html,
                baseline_rtf,
                baseline_rtf,
                html_dir / "variants" / "ds_table_minus_1_column.html",
            ],
        },
    ).to_csv(input_path, index=False)

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["compare", "--input", str(input_path), "--output", str(output_path)],
    )

    assert result.exit_code == 0

    output_df = pd.read_csv(output_path)
    assert output_df.columns.tolist() == [
        "left_path",
        "right_path",
        "structure_match",
        "summary",
    ]
    assert len(output_df) == 4
    assert output_df["structure_match"].tolist() == [True, True, True, False]
    assert "structure mismatch" in output_df.loc[3, "summary"]
