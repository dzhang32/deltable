"""Generate a complex clinical AE summary table RTF fixture."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import polars as pl
from rtflite import (
    RTFBody,
    RTFColumnHeader,
    RTFDocument,
    RTFFootnote,
    RTFSource,
    RTFTitle,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TreatmentGroup:
    """Represent a treatment group and its denominator."""

    name: str
    n: int


TITLE = "Table 14.3.1 Summary of Treatment-Emergent Adverse Events (Safety Population)"
SUBTITLE = "Safety Population"
FOOTNOTE = "Every subject is counted a single time for each applicable row and column."
SOURCE = "Source: Synthetic data generated for fixture purposes."

TREATMENTS = [
    TreatmentGroup(name="Placebo", n=60),
    TreatmentGroup(name="Low Dose", n=60),
    TreatmentGroup(name="High Dose", n=60),
    TreatmentGroup(name="Total", n=180),
]

ROWS: list[tuple[str, dict[str, int | None]]] = [
    (
        "Participants in population",
        {
            "Placebo": 60,
            "Low Dose": 60,
            "High Dose": 60,
            "Total": 180,
        },
    ),
    (
        "With any adverse event",
        {
            "Placebo": 28,
            "Low Dose": 32,
            "High Dose": 36,
            "Total": 96,
        },
    ),
    (
        "With drug-related adverse event",
        {
            "Placebo": 10,
            "Low Dose": 14,
            "High Dose": 18,
            "Total": 42,
        },
    ),
    (
        "With serious adverse event",
        {
            "Placebo": 4,
            "Low Dose": 6,
            "High Dose": 8,
            "Total": 18,
        },
    ),
    (
        "With serious drug-related adverse event",
        {
            "Placebo": 1,
            "Low Dose": 2,
            "High Dose": 3,
            "Total": 6,
        },
    ),
    (
        "Discontinued due to adverse event",
        {
            "Placebo": 2,
            "Low Dose": 3,
            "High Dose": 4,
            "Total": 9,
        },
    ),
    (
        "Who died",
        {
            "Placebo": 0,
            "Low Dose": 1,
            "High Dose": 2,
            "Total": 3,
        },
    ),
    (
        "Worst severity",
        {
            "Placebo": None,
            "Low Dose": None,
            "High Dose": None,
            "Total": None,
        },
    ),
    (
        "  Mild",
        {
            "Placebo": 12,
            "Low Dose": 14,
            "High Dose": 16,
            "Total": 42,
        },
    ),
    (
        "  Moderate",
        {
            "Placebo": 10,
            "Low Dose": 12,
            "High Dose": 13,
            "Total": 35,
        },
    ),
    (
        "  Severe",
        {
            "Placebo": 6,
            "Low Dose": 6,
            "High Dose": 7,
            "Total": 19,
        },
    ),
]


def _format_percent(n: int | None, denom: int, show_blank: bool = False) -> str:
    """Format a percentage value in parentheses with one decimal place.

    Args:
        n: The numerator value.
        denom: The denominator for percentage calculation.
        show_blank: Whether to return an empty string regardless of input.

    Returns:
        The formatted percentage string or an empty string.
    """
    if show_blank or n is None:
        return ""
    percent = (n / denom) * 100.0
    return f"({percent:.1f})"


def build_table() -> pl.DataFrame:
    """Build the adverse event summary table as a Polars DataFrame.

    Returns:
        The final table as a Polars DataFrame.
    """
    rows: list[dict[str, str]] = []
    for label, values in ROWS:
        row: dict[str, str] = {"Category": label}
        for treatment in TREATMENTS:
            count = values.get(treatment.name)
            row[f"{treatment.name}_n"] = "" if count is None else f"{count}"
            row[f"{treatment.name}_pct"] = _format_percent(
                count,
                treatment.n,
                show_blank=label == "Participants in population",
            )
        rows.append(row)
    return pl.DataFrame(rows)


def _build_headers() -> list[RTFColumnHeader]:
    """Build multi-row column headers for the adverse event table.

    Returns:
        The ordered list of column header rows.
    """
    group_labels = [f"{t.name} (N={t.n})" for t in TREATMENTS]

    header_1 = RTFColumnHeader(
        text=["Category", *group_labels],
        col_rel_width=[3, 2, 2, 2, 2],
    )

    header_2 = RTFColumnHeader(
        text=[
            "",
            "n",
            "(%)",
            "n",
            "(%)",
            "n",
            "(%)",
            "n",
            "(%)",
        ],
        col_rel_width=[3, 1, 1, 1, 1, 1, 1, 1, 1],
        border_bottom=["single"] * 9,
    )

    return [header_1, header_2]


def build_rtf(df: pl.DataFrame) -> RTFDocument:
    """Create the RTF document for the adverse event table.

    Args:
        df: The table data to render.

    Returns:
        The configured RTF document object.
    """
    return RTFDocument(
        df=df,
        rtf_title=RTFTitle(
            text=[TITLE, SUBTITLE],
            text_format=["b", ""],
        ),
        rtf_column_header=_build_headers(),
        rtf_body=RTFBody(
            col_rel_width=[3, 1, 1, 1, 1, 1, 1, 1, 1],
            text_justification=[
                ["l", "c", "c", "c", "c", "c", "c", "c", "c"],
            ],
        ),
        rtf_footnote=RTFFootnote(text=FOOTNOTE),
        rtf_source=RTFSource(text=SOURCE),
    )


def main() -> None:
    """Generate the RTF fixture file."""
    df = build_table()
    doc = build_rtf(df)
    output_path = Path("tests/data/rtf/ae_summary_example.rtf")
    doc.write_rtf(output_path)


if __name__ == "__main__":
    main()
