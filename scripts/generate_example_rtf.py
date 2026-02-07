"""Generate a complex clinical AE summary table RTF fixture."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import re

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
RTF_OUTPUT_DIR = Path("tests/data/rtf")
CSV_OUTPUT_DIR = Path("tests/data/csv")
BASE_RTF_OUTPUT_PATH = RTF_OUTPUT_DIR / "ae_summary_baseline.rtf"
BASE_CSV_OUTPUT_PATH = CSV_OUTPUT_DIR / "ae_summary_baseline.csv"

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


def build_expected_loader_table() -> pl.DataFrame:
    """Build expected CSV output matching `load_rtf_table` semantics."""
    column_names = ["Category"]
    for treatment in TREATMENTS:
        group_name = f"{treatment.name} (N={treatment.n})"
        column_names.append(f"{group_name} | n")
        column_names.append(f"{group_name} | (%)")

    rows: list[dict[str, str]] = []
    for label, values in ROWS:
        row: dict[str, str] = {"Category": label.strip()}
        for treatment in TREATMENTS:
            count = values.get(treatment.name)
            show_blank_pct = label.strip() == "Participants in population"
            row[f"{treatment.name} (N={treatment.n}) | n"] = (
                "" if count is None else f"{count}"
            )
            row[f"{treatment.name} (N={treatment.n}) | (%)"] = _format_percent(
                count,
                treatment.n,
                show_blank=show_blank_pct,
            )
        rows.append(row)

    return pl.DataFrame(rows).select(column_names)


@dataclass(frozen=True, slots=True, kw_only=True)
class VariantSpec:
    """Describe one formatting variant fixture."""

    name: str
    rtf_transform: Callable[[str], str]
    csv_transform: Callable[[str], str]


def _identity(text: str) -> str:
    """Return input text unchanged."""
    return text


def _replace_or_raise(text: str, old: str, new: str) -> str:
    """Replace a required substring once."""
    if old not in text:
        raise ValueError(f"Required text not found: {old!r}")
    return text.replace(old, new, 1)


def _replace_n_or_raise(text: str, old: str, new: str, count: int) -> str:
    """Replace a required substring a fixed number of times."""
    updated = text
    for _ in range(count):
        if old not in updated:
            raise ValueError(f"Required text not found enough times: {old!r}")
        updated = updated.replace(old, new, 1)
    return updated


def _replace_all_or_raise(text: str, old: str, new: str) -> str:
    """Replace all occurrences of a required substring."""
    if old not in text:
        raise ValueError(f"Required text not found: {old!r}")
    return text.replace(old, new)


def _replace_first_row_block(text: str, replacement: str) -> str:
    """Replace the first header-row block."""
    pattern = re.compile(
        r"\\trowd\\trgaph108\\trleft0\\trqc\n.*?\\intbl\\row\\pard",
        flags=re.DOTALL,
    )
    match = pattern.search(text)
    if match is None:
        raise ValueError("Unable to locate first row block.")
    return text[: match.start()] + replacement + text[match.end() :]


def _extract_row_blocks(text: str, count: int) -> list[str]:
    """Extract the first `count` row blocks from RTF text."""
    pattern = re.compile(
        r"\\trowd.*?\\intbl\\row\\pard",
        flags=re.DOTALL,
    )
    matches = [match.group(0) for match in pattern.finditer(text)]
    if len(matches) < count:
        raise ValueError(f"Expected at least {count} row blocks.")
    return matches[:count]


def _insert_before_label_row(text: str, label: str, insertion: str) -> str:
    """Insert RTF text immediately before the row containing a label."""
    label_index = text.find(label)
    if label_index == -1:
        raise ValueError(f"Unable to locate label: {label!r}")

    row_start = text.rfind(r"\trowd", 0, label_index)
    if row_start == -1:
        raise ValueError(f"Unable to locate row start before: {label!r}")

    return text[:row_start] + insertion + text[row_start:]


def _insert_csv_line_before(
    text: str,
    before_line_prefix: str,
    insert_line: str,
) -> str:
    """Insert one CSV line before the first line with a matching prefix."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(before_line_prefix):
            lines.insert(index, insert_line)
            break
    else:
        raise ValueError(f"Unable to locate CSV line prefix: {before_line_prefix!r}")

    updated = "\n".join(lines)
    if text.endswith("\n"):
        updated += "\n"
    return updated


def _insert_first_cell_modifier_before_label(
    text: str,
    label: str,
    modifier: str,
) -> str:
    """Insert a cell modifier in the first column before a target label."""
    label_index = text.find(label)
    if label_index == -1:
        raise ValueError(f"Unable to locate label: {label!r}")

    marker = (
        r"\clbrdrl\brdrs\brdrw15\clbrdrt\brdrw15\clbrdrb\brdrw15\clvertalt\cellx2455"
    )
    marker_index = text.rfind(marker, 0, label_index)
    if marker_index == -1:
        raise ValueError(f"Unable to locate first-cell marker before: {label!r}")

    return (
        text[:marker_index]
        + modifier
        + text[marker_index : marker_index + len(marker)]
        + text[marker_index + len(marker) :]
    )


def _rtf_multiline_headers(text: str) -> str:
    """Inject multiline treatment headers."""
    updated = text
    updated = _replace_or_raise(
        updated,
        r"{\f0 Placebo (N=60)}\cell",
        r"{\f0 Placebo\line (N=60)}\cell",
    )
    updated = _replace_or_raise(
        updated,
        r"{\f0 Low Dose (N=60)}\cell",
        r"{\f0 Low Dose\line (N=60)}\cell",
    )
    updated = _replace_or_raise(
        updated,
        r"{\f0 High Dose (N=60)}\cell",
        r"{\f0 High Dose\line (N=60)}\cell",
    )
    updated = _replace_or_raise(
        updated,
        r"{\f0 Total (N=180)}\cell",
        r"{\f0 Total\line (N=180)}\cell",
    )
    return updated


def _rtf_indented_group_rows(text: str) -> str:
    """Apply additional indentation to grouped rows."""
    updated = text
    updated = _replace_or_raise(
        updated,
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\ql\fs18{\f0 Worst severity}\cell",
        r"\pard\hyphpar0\sb15\sa15\fi0\li180\ri0\ql\fs18{\f0 Worst severity}\cell",
    )
    updated = _replace_or_raise(
        updated,
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\ql\fs18{\f0   Mild}\cell",
        r"\pard\hyphpar0\sb15\sa15\fi0\li360\ri0\ql\fs18{\f0   Mild}\cell",
    )
    updated = _replace_or_raise(
        updated,
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\ql\fs18{\f0   Moderate}\cell",
        r"\pard\hyphpar0\sb15\sa15\fi0\li360\ri0\ql\fs18{\f0   Moderate}\cell",
    )
    updated = _replace_or_raise(
        updated,
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\ql\fs18{\f0   Severe}\cell",
        r"\pard\hyphpar0\sb15\sa15\fi0\li360\ri0\ql\fs18{\f0   Severe}\cell",
    )
    return updated


def _rtf_repeating_header_rows(text: str) -> str:
    """Set top header rows to repeat using `\\trhdr`."""
    return _replace_n_or_raise(
        text,
        r"\trowd\trgaph108\trleft0\trqc",
        r"\trowd\trhdr\trgaph108\trleft0\trqc",
        count=2,
    )


def _rtf_horizontal_merge_spanner(text: str) -> str:
    """Introduce a horizontal-merge spanner header row."""
    replacement = (
        r"\trowd\trgaph108\trleft0\trqc"
        "\n"
        r"\clbrdrl\brdrs\brdrw15\clbrdrt\brdrdb\brdrw15\clbrdrb\brdrw15\clvertalb\cellx2455"
        "\n"
        r"\clmgf\clbrdrl\brdrs\brdrw15\clbrdrt\brdrdb\brdrw15\clbrdrb\brdrw15\clvertalb\cellx3273"
        "\n"
        r"\clmrg\clbrdrl\brdrs\brdrw15\clbrdrt\brdrdb\brdrw15\clbrdrb\brdrw15\clvertalb\cellx4091"
        "\n"
        r"\clmgf\clbrdrl\brdrs\brdrw15\clbrdrt\brdrdb\brdrw15\clbrdrb\brdrw15\clvertalb\cellx4909"
        "\n"
        r"\clmrg\clbrdrl\brdrs\brdrw15\clbrdrt\brdrdb\brdrw15\clbrdrb\brdrw15\clvertalb\cellx5727"
        "\n"
        r"\clmgf\clbrdrl\brdrs\brdrw15\clbrdrt\brdrdb\brdrw15\clbrdrb\brdrw15\clvertalb\cellx6545"
        "\n"
        r"\clmrg\clbrdrl\brdrs\brdrw15\clbrdrt\brdrdb\brdrw15\clbrdrb\brdrw15\clvertalb\cellx7364"
        "\n"
        r"\clmgf\clbrdrl\brdrs\brdrw15\clbrdrt\brdrdb\brdrw15\clbrdrb\brdrw15\clvertalb\cellx8182"
        "\n"
        r"\clmrg\clbrdrl\brdrs\brdrw15\clbrdrt\brdrdb\brdrw15\clbrdrr\brdrs\brdrw15\clbrdrb\brdrw15\clvertalb\cellx9000"
        "\n"
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 Category}\cell"
        "\n"
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 Placebo (N=60)}\cell"
        "\n"
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 }\cell"
        "\n"
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 Low Dose (N=60)}\cell"
        "\n"
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 }\cell"
        "\n"
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 High Dose (N=60)}\cell"
        "\n"
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 }\cell"
        "\n"
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 Total (N=180)}\cell"
        "\n"
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\qc\fs18{\f0 }\cell"
        "\n"
        r"\intbl\row\pard"
    )
    return _replace_first_row_block(text, replacement)


def _rtf_vertical_merge_stub(text: str) -> str:
    """Introduce vertical merge controls in the first column."""
    updated = text
    updated = _insert_first_cell_modifier_before_label(
        updated,
        label=r"{\f0 Worst severity}\cell",
        modifier=r"\clvmgf",
    )
    updated = _insert_first_cell_modifier_before_label(
        updated,
        label=r"{\f0   Mild}\cell",
        modifier=r"\clvmrg",
    )
    updated = _insert_first_cell_modifier_before_label(
        updated,
        label=r"{\f0   Moderate}\cell",
        modifier=r"\clvmrg",
    )
    return updated


def _rtf_unicode_superscript(text: str) -> str:
    """Inject superscript and Unicode marker escapes."""
    updated = text
    updated = _replace_or_raise(
        updated,
        r"{\f0 Placebo (N=60)}\cell",
        r"{\f0 Placebo (N=60){\super a}}\cell",
    )
    updated = _replace_or_raise(
        updated,
        r"{\f0 With any adverse event}\cell",
        r"{\f0 With any adverse event \u8224?}\cell",
    )
    return updated


def _rtf_pagination_repeated_headers(text: str) -> str:
    """Insert a page break and repeated two-row header block mid-table."""
    header_rows = _extract_row_blocks(text=text, count=2)
    insertion = r"\page" + "\n" + "\n".join(header_rows) + "\n"
    return _insert_before_label_row(
        text=text,
        label=r"{\f0 With serious adverse event}\cell",
        insertion=insertion,
    )


def _build_group_header_row(*, merged_spanning: bool) -> str:
    """Build a standalone group-header row with blank numeric cells."""
    cell_boundaries = [
        2455,
        3273,
        4091,
        4909,
        5727,
        6545,
        7364,
        8182,
        9000,
    ]

    lines = [r"\trowd\trgaph108\trleft0\trqc"]
    for index, boundary in enumerate(cell_boundaries):
        if merged_spanning and index == 1:
            prefix = r"\clmgf"
        elif merged_spanning and index > 1:
            prefix = r"\clmrg"
        else:
            prefix = ""
        lines.append(f"{prefix}\\cellx{boundary}")

    lines.append(
        r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\ql\fs18{\f0 System Organ Class}\cell"
    )
    if merged_spanning:
        lines.append(r"\pard\hyphpar0\sb15\sa15\fi0\li0\ri0\ql\fs18{\f0 }\cell")
        lines.extend([r"\cell"] * 7)
    else:
        lines.extend([r"\cell"] * 8)

    lines.append(r"\row")
    return "\n".join(lines) + "\n"


def _rtf_group_header_first_cell_bare_cells(text: str) -> str:
    """Insert a standalone group-header row with bare blank cells."""
    return _insert_before_label_row(
        text=text,
        label=r"{\f0 Worst severity}\cell",
        insertion=_build_group_header_row(merged_spanning=False),
    )


def _rtf_group_header_merged_spanning(text: str) -> str:
    """Insert a standalone merged-spanning group-header row."""
    return _insert_before_label_row(
        text=text,
        label=r"{\f0 Worst severity}\cell",
        insertion=_build_group_header_row(merged_spanning=True),
    )


def _rtf_row_terminator_plain_row(text: str) -> str:
    """Replace standard row endings with plain `\\row` endings."""
    return _replace_all_or_raise(
        text,
        old=r"\intbl\row\pard",
        new=r"\row",
    )


def _csv_unicode_expected(text: str) -> str:
    """Set expected Unicode output for the body-row marker."""
    return _replace_or_raise(
        text,
        "With any adverse event,28,(46.7),32,(53.3),36,(60.0),96,(53.3)",
        "With any adverse event †,28,(46.7),32,(53.3),36,(60.0),96,(53.3)",
    )


def _csv_with_group_header_row(text: str) -> str:
    """Insert expected standalone group-header row in CSV output."""
    return _insert_csv_line_before(
        text=text,
        before_line_prefix="Worst severity,",
        insert_line='System Organ Class,"","","","","","","",""',
    )


VARIANTS = [
    VariantSpec(
        name="multiline_headers",
        rtf_transform=_rtf_multiline_headers,
        csv_transform=_identity,
    ),
    VariantSpec(
        name="indented_group_rows",
        rtf_transform=_rtf_indented_group_rows,
        csv_transform=_identity,
    ),
    VariantSpec(
        name="repeating_header_row",
        rtf_transform=_rtf_repeating_header_rows,
        csv_transform=_identity,
    ),
    VariantSpec(
        name="spanning_header_horizontal_merge",
        rtf_transform=_rtf_horizontal_merge_spanner,
        csv_transform=_identity,
    ),
    VariantSpec(
        name="vertical_merge_stub_column",
        rtf_transform=_rtf_vertical_merge_stub,
        csv_transform=_identity,
    ),
    VariantSpec(
        name="unicode_superscript_symbols",
        rtf_transform=_rtf_unicode_superscript,
        csv_transform=_csv_unicode_expected,
    ),
    VariantSpec(
        name="pagination_repeated_headers",
        rtf_transform=_rtf_pagination_repeated_headers,
        csv_transform=_identity,
    ),
    VariantSpec(
        name="group_header_first_cell_bare_cells",
        rtf_transform=_rtf_group_header_first_cell_bare_cells,
        csv_transform=_csv_with_group_header_row,
    ),
    VariantSpec(
        name="group_header_merged_spanning",
        rtf_transform=_rtf_group_header_merged_spanning,
        csv_transform=_csv_with_group_header_row,
    ),
    VariantSpec(
        name="row_terminator_plain_row",
        rtf_transform=_rtf_row_terminator_plain_row,
        csv_transform=_identity,
    ),
]


def _generate_variant_fixtures(base_rtf: str, base_csv: str) -> None:
    """Generate RTF/CSV variant fixture pairs."""
    RTF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for variant in VARIANTS:
        rtf_output = variant.rtf_transform(base_rtf)
        csv_output = variant.csv_transform(base_csv)

        rtf_path = RTF_OUTPUT_DIR / f"{variant.name}.rtf"
        csv_path = CSV_OUTPUT_DIR / f"{variant.name}.csv"
        rtf_path.write_text(_with_trailing_newline(rtf_output), encoding="utf-8")
        csv_path.write_text(csv_output, encoding="utf-8")


def _with_trailing_newline(text: str) -> str:
    """Ensure text ends with exactly one newline."""
    return text.rstrip("\n") + "\n"


def main() -> None:
    """Generate baseline and variant fixture files."""
    df = build_table()
    doc = build_rtf(df)
    BASE_RTF_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASE_CSV_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    doc.write_rtf(BASE_RTF_OUTPUT_PATH)
    BASE_RTF_OUTPUT_PATH.write_text(
        _with_trailing_newline(
            BASE_RTF_OUTPUT_PATH.read_text(encoding="utf-8", errors="ignore")
        ),
        encoding="utf-8",
    )

    expected_df = build_expected_loader_table()
    expected_df.write_csv(BASE_CSV_OUTPUT_PATH)

    base_rtf = BASE_RTF_OUTPUT_PATH.read_text(encoding="utf-8", errors="ignore")
    base_csv = BASE_CSV_OUTPUT_PATH.read_text(encoding="utf-8")
    _generate_variant_fixtures(base_rtf=base_rtf, base_csv=base_csv)


if __name__ == "__main__":
    main()
