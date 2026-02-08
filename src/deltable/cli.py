import tempfile
from pathlib import Path

import click
import pandas as pd

from deltable.compare import compare_html_tables
from deltable.rtf_to_html import convert_rtf_to_html


@click.group()
def cli() -> None:
    """Deltable — compare RTF / HTML table structures."""


@cli.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True))
@click.option("--output", "output_path", required=True, type=click.Path())
def compare(input_path: str, output_path: str) -> None:
    """Compare table pairs listed in a CSV file.

    The input CSV must have ``left_path`` and ``right_path`` columns.
    Each path may point to an ``.html`` or ``.rtf`` file.  RTF files
    are converted to HTML automatically before comparison.
    """
    pairs = pd.read_csv(input_path)
    rows: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)

        for _, row in pairs.iterrows():
            left = Path(row["left_path"])
            right = Path(row["right_path"])

            left_html = _ensure_html(left, tmp)
            right_html = _ensure_html(right, tmp)

            result = compare_html_tables(left_html, right_html)
            rows.append(
                {
                    "left_path": str(left),
                    "right_path": str(right),
                    "structure_match": result.structure_match,
                    "summary": result.summary,
                },
            )

    pd.DataFrame(rows).to_csv(output_path, index=False)


def _ensure_html(path: Path, tmp_dir: Path) -> Path:
    """Return an HTML path, converting from RTF if needed."""
    if path.suffix.lower() == ".rtf":
        return convert_rtf_to_html(path, tmp_dir)
    return path
