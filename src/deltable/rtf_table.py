"""Load a single-table RTF document into a Polars DataFrame."""

from __future__ import annotations

import re
from pathlib import Path

import polars as pl

ROW_PATTERN = re.compile(r"\\trowd(?P<body>.*?)(?:\\intbl\\row\\pard)", re.DOTALL)
CELL_PATTERN = re.compile(r"\\pard(?P<cell>.*?)(?=\\cell(?!x))", re.DOTALL)
CONTROL_WORD_PATTERN = re.compile(r"\\[a-zA-Z]+-?\d* ?")
HEX_ESCAPE_PATTERN = re.compile(r"\\'[0-9a-fA-F]{2}")
ESCAPED_BRACE_PATTERN = re.compile(r"\\([{}\\])")
WHITESPACE_PATTERN = re.compile(r"\s+")


def load_rtf_table(path: Path | str) -> pl.DataFrame:
    """Load a single RTF table from disk into a Polars DataFrame.

    Args:
        path: Path to an RTF file containing one table.

    Returns:
        Parsed table data as a Polars DataFrame with string columns.

    Raises:
        ValueError: If the RTF table does not contain enough rows.
    """
    rtf_text = Path(path).read_text(encoding="utf-8", errors="ignore")
    rows = _extract_rows_from_rtf(rtf_text)
    if len(rows) < 3:
        raise ValueError("RTF table did not contain enough rows.")

    header_top = rows[0]
    header_sub = rows[1]
    headers = _build_composite_headers(header_top, header_sub)

    body_rows = _normalize_body_rows(rows[2:], len(headers))
    if not body_rows:
        raise ValueError("RTF table did not contain any body rows.")

    return pl.DataFrame(
        body_rows,
        schema=headers,
        orient="row",
    )


def _extract_rows_from_rtf(rtf_text: str) -> list[list[str]]:
    """Extract a list of cleaned rows from an RTF table string."""
    rows: list[list[str]] = []
    for row_match in ROW_PATTERN.finditer(rtf_text):
        row_block = row_match.group("body")
        cells = [
            _clean_cell_text(cell_match.group("cell"))
            for cell_match in CELL_PATTERN.finditer(row_block)
        ]
        if cells and any(cells):
            rows.append(cells)
    return rows


def _clean_cell_text(cell_rtf: str) -> str:
    """Convert an RTF cell fragment to plain text."""
    text = cell_rtf.replace(r"\line", " ")
    text = HEX_ESCAPE_PATTERN.sub("", text)
    text = ESCAPED_BRACE_PATTERN.sub(r"\1", text)
    text = CONTROL_WORD_PATTERN.sub("", text)
    text = text.replace("{", "").replace("}", "")
    text = WHITESPACE_PATTERN.sub(" ", text)
    return text.strip()


def _build_composite_headers(
    header_row_1: list[str],
    header_row_2: list[str],
) -> list[str]:
    """Build flattened column names from two header rows."""
    expanded_header_row_1 = _expand_header_row(
        header_row=header_row_1,
        target_length=len(header_row_2),
    )
    headers: list[str] = []
    for index, (level_1, level_2) in enumerate(
        zip(expanded_header_row_1, header_row_2, strict=True),
        start=1,
    ):
        header_name = _compose_header_name(
            column_index=index,
            level_1=level_1,
            level_2=level_2,
        )
        headers.append(header_name)
    return _deduplicate_headers(headers)


def _expand_header_row(header_row: list[str], target_length: int) -> list[str]:
    """Expand a grouped top header row to the full second-header width."""
    if target_length <= 0:
        return []

    if not header_row:
        return [f"column_{index}" for index in range(1, target_length + 1)]

    if len(header_row) == target_length:
        return header_row.copy()

    if len(header_row) == 1:
        return [header_row[0]] * target_length

    first_column = header_row[0]
    grouped_columns = header_row[1:]
    remaining_width = target_length - 1
    expanded_row = [first_column]

    if grouped_columns and remaining_width % len(grouped_columns) == 0:
        repeat_count = remaining_width // len(grouped_columns)
        for grouped_header in grouped_columns:
            expanded_row.extend([grouped_header] * repeat_count)
    else:
        expanded_row.extend(grouped_columns)

    if len(expanded_row) < target_length:
        fill_value = expanded_row[-1] if expanded_row else ""
        expanded_row.extend([fill_value] * (target_length - len(expanded_row)))

    return expanded_row[:target_length]


def _compose_header_name(column_index: int, level_1: str, level_2: str) -> str:
    """Build the output header string for one column."""
    cleaned_level_1 = level_1.strip()
    cleaned_level_2 = level_2.strip()

    if column_index == 1:
        return cleaned_level_1 or cleaned_level_2 or f"column_{column_index}"

    if cleaned_level_1 and cleaned_level_2:
        return f"{cleaned_level_1} | {cleaned_level_2}"

    if cleaned_level_1:
        return cleaned_level_1

    if cleaned_level_2:
        return cleaned_level_2

    return f"column_{column_index}"


def _deduplicate_headers(headers: list[str]) -> list[str]:
    """Make duplicate header names unique with deterministic suffixes."""
    counts: dict[str, int] = {}
    deduplicated: list[str] = []

    for header in headers:
        counts[header] = counts.get(header, 0) + 1
        if counts[header] == 1:
            deduplicated.append(header)
            continue
        deduplicated.append(f"{header}__{counts[header]}")

    return deduplicated


def _normalize_body_rows(rows: list[list[str]], width: int) -> list[list[str]]:
    """Keep only table rows that match or exceed expected width."""
    normalized_rows: list[list[str]] = []
    for row in rows:
        if len(row) < width:
            continue
        normalized_rows.append(row[:width])
    return normalized_rows
