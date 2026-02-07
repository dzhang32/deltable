"""Load a single-table RTF document into a column-oriented table mapping."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from pathlib import Path
from typing import Any, Callable

TableData = dict[str, list[Any]]
RawTableData = dict[str, list[str | None]]

ROW_PATTERN = re.compile(
    r"\\trowd(?P<body>.*?)(?:(?:\\intbl\s*)?\\row(?:\s*\\pard)?)",
    re.DOTALL,
)
CELL_DELIMITER_PATTERN = re.compile(r"\\cell(?!x)")
CELLX_PATTERN = re.compile(r"\\cellx-?\d+")
UNICODE_ESCAPE_PATTERN = re.compile(r"\\u(-?\d+)\?")
CONTROL_WORD_PATTERN = re.compile(r"\\[a-zA-Z]+-?\d* ?")
HEX_ESCAPE_PATTERN = re.compile(r"\\'[0-9a-fA-F]{2}")
SUPERSCRIPT_GROUP_PATTERN = re.compile(r"\{\\super\s+[^{}]*\}")
ESCAPED_BRACE_PATTERN = re.compile(r"\\([{}\\])")
WHITESPACE_PATTERN = re.compile(r"\s+")
INTEGER_PATTERN = re.compile(r"[+-]?\d+")


@dataclass(frozen=True, slots=True, kw_only=True)
class RowCell:
    """Represent one parsed RTF table cell and its merge metadata."""

    text: str
    h_merge_start: bool
    h_merge_continue: bool
    v_merge_start: bool
    v_merge_continue: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class ParsedRow:
    """Represent one parsed RTF table row."""

    cells: list[RowCell]


def load_rtf_table(path: Path | str) -> TableData:
    """Load a single RTF table from disk into a column-oriented mapping.

    Args:
        path: Path to an RTF file containing one table.

    Returns:
        Parsed table data keyed by column name.

    Raises:
        ValueError: If the RTF table cannot be normalized to a consistent shape.
    """
    rtf_text = Path(path).read_text(encoding="utf-8", errors="ignore")
    rows = _extract_rows_from_rtf(rtf_text)
    if len(rows) < 3:
        raise ValueError("RTF table did not contain enough rows.")

    header_top = [cell.text for cell in rows[0].cells]
    header_sub = [cell.text for cell in rows[1].cells]
    headers = _build_composite_headers(
        header_row_1=header_top,
        header_row_2=header_sub,
        header_row_1_cells=rows[0].cells,
    )
    stub_column_span = _infer_stub_column_span(headers)

    body_rows = _normalize_body_rows(
        rows=rows[2:],
        width=len(headers),
        header_row_1=header_top,
        header_row_2=header_sub,
        stub_column_span=stub_column_span,
    )
    if not body_rows:
        raise ValueError("RTF table did not contain any body rows.")

    raw_table = _rows_to_table_data(headers=headers, rows=body_rows)
    return _parse_numeric_columns(raw_table)


def _rows_to_table_data(*, headers: list[str], rows: list[list[str]]) -> RawTableData:
    """Build a column-oriented table dictionary from normalized row values."""
    table: RawTableData = {header: [] for header in headers}

    for row_values in rows:
        for header, cell_value in zip(headers, row_values, strict=True):
            table[header].append(_normalize_output_value(cell_value))

    return table


def _normalize_output_value(value: str) -> str | None:
    """Map empty parsed cell text to None."""
    stripped_value = value.strip()
    if not stripped_value:
        return None
    return stripped_value


def _parse_numeric_columns(table: RawTableData) -> TableData:
    """Parse numeric columns using strict per-column inference."""
    parsed_table: TableData = {}
    for column_name, values in table.items():
        parser = _infer_numeric_parser(values)
        if parser is None:
            parsed_table[column_name] = values.copy()
            continue

        parsed_table[column_name] = [
            None if value is None else parser(value) for value in values
        ]

    return parsed_table


def _infer_numeric_parser(
    values: list[str | None],
) -> Callable[[str], int | float] | None:
    """Infer int/float parser for a full column when all values are numeric."""
    non_null_values = [value for value in values if value is not None]
    if not non_null_values:
        return None

    if all(_can_parse_int(value) for value in non_null_values):
        return int

    if all(_can_parse_float(value) for value in non_null_values):
        return float

    return None


def _can_parse_int(value: str) -> bool:
    """Return whether a value is an integer literal."""
    return bool(INTEGER_PATTERN.fullmatch(value))


def _can_parse_float(value: str) -> bool:
    """Return whether a value can be parsed as a finite float."""
    try:
        parsed_value = float(value)
    except ValueError:
        return False
    return math.isfinite(parsed_value)


def _extract_rows_from_rtf(rtf_text: str) -> list[ParsedRow]:
    """Extract a list of parsed rows from an RTF table string."""
    rows: list[ParsedRow] = []
    for row_match in ROW_PATTERN.finditer(rtf_text):
        row_block = row_match.group("body")
        cell_defs = _parse_cell_definitions(row_block)
        if not cell_defs:
            continue

        cell_start_index = _find_cell_content_start_index(row_block=row_block)
        cell_fragments = _split_row_cells(
            row_block=row_block,
            start_index=cell_start_index,
        )

        parsed_cells: list[RowCell] = []
        for index, cell_fragment in enumerate(cell_fragments):
            cell_def = cell_defs[index] if index < len(cell_defs) else ""
            parsed_cells.append(
                RowCell(
                    text=_clean_cell_text(cell_fragment),
                    h_merge_start=r"\clmgf" in cell_def,
                    h_merge_continue=r"\clmrg" in cell_def,
                    v_merge_start=r"\clvmgf" in cell_def,
                    v_merge_continue=r"\clvmrg" in cell_def,
                )
            )

        if parsed_cells and any(cell.text for cell in parsed_cells):
            rows.append(ParsedRow(cells=parsed_cells))
    return rows


def _parse_cell_definitions(row_block: str) -> list[str]:
    """Parse cell-definition segments from one row block."""
    matches = list(CELLX_PATTERN.finditer(row_block))
    if not matches:
        return []

    cell_defs: list[str] = []
    start_index = 0
    for match in matches:
        cell_defs.append(row_block[start_index : match.end()])
        start_index = match.end()
    return cell_defs


def _find_cell_content_start_index(*, row_block: str) -> int:
    """Return the index where row cell content begins."""
    matches = list(CELLX_PATTERN.finditer(row_block))
    if not matches:
        return 0
    return matches[-1].end()


def _split_row_cells(*, row_block: str, start_index: int) -> list[str]:
    """Split row content into cell fragments using `\\cell` delimiters."""
    cell_fragments: list[str] = []
    cursor = start_index
    for delimiter_match in CELL_DELIMITER_PATTERN.finditer(row_block, pos=start_index):
        cell_fragments.append(row_block[cursor : delimiter_match.start()])
        cursor = delimiter_match.end()
    return cell_fragments


def _clean_cell_text(cell_rtf: str) -> str:
    """Convert an RTF cell fragment to plain text."""
    text = cell_rtf.replace(r"\line", " ")
    text = SUPERSCRIPT_GROUP_PATTERN.sub("", text)
    text = UNICODE_ESCAPE_PATTERN.sub(_decode_unicode_escape, text)
    text = HEX_ESCAPE_PATTERN.sub("", text)
    text = ESCAPED_BRACE_PATTERN.sub(r"\1", text)
    text = CONTROL_WORD_PATTERN.sub("", text)
    text = text.replace("{", "").replace("}", "")
    text = WHITESPACE_PATTERN.sub(" ", text)
    return text.strip()


def _decode_unicode_escape(match: re.Match[str]) -> str:
    """Decode an RTF Unicode escape sequence."""
    code_point = int(match.group(1))
    if code_point < 0:
        code_point += 65536
    return chr(code_point)


def _build_composite_headers(
    header_row_1: list[str],
    header_row_2: list[str],
    header_row_1_cells: list[RowCell],
) -> list[str]:
    """Build flattened column names from two header rows."""
    header_stub_column_count = _infer_header_stub_column_count(header_row_2)
    expanded_header_row_1 = _expand_header_row(
        header_row=header_row_1,
        target_length=len(header_row_2),
        stub_column_count=header_stub_column_count,
    )
    expanded_header_row_1 = _apply_horizontal_merge_labels(
        header_row_1=expanded_header_row_1,
        header_row_1_cells=header_row_1_cells,
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


def _apply_horizontal_merge_labels(
    header_row_1: list[str],
    header_row_1_cells: list[RowCell],
    target_length: int,
) -> list[str]:
    """Propagate merged top-header labels across merged columns."""
    merged_labels: list[str] = []
    active_label = ""

    for index in range(target_length):
        raw_label = header_row_1[index] if index < len(header_row_1) else ""
        label = raw_label.strip()
        cell = header_row_1_cells[index] if index < len(header_row_1_cells) else None

        if cell is not None and cell.h_merge_start:
            active_label = label
            merged_labels.append(label)
            continue

        if cell is not None and cell.h_merge_continue:
            merged_labels.append(active_label or label)
            continue

        if label:
            active_label = label
        merged_labels.append(label)

    return merged_labels


def _infer_header_stub_column_count(header_row_2: list[str]) -> int:
    """Infer leading stub columns from blank second-header cells."""
    count = 0
    for value in header_row_2:
        if value.strip():
            break
        count += 1
    return max(1, count)


def _expand_header_row(
    header_row: list[str],
    target_length: int,
    stub_column_count: int,
) -> list[str]:
    """Expand a grouped top header row to the full second-header width."""
    if target_length <= 0:
        return []

    if not header_row:
        return [f"column_{index}" for index in range(1, target_length + 1)]

    if len(header_row) == target_length:
        return header_row.copy()

    if len(header_row) == 1:
        return [header_row[0]] * target_length

    stub_column_count = min(stub_column_count, len(header_row), target_length)
    stub_columns = header_row[:stub_column_count]
    grouped_columns = header_row[stub_column_count:]
    remaining_width = target_length - stub_column_count
    expanded_row = stub_columns.copy()

    if (
        grouped_columns
        and remaining_width > 0
        and remaining_width % len(grouped_columns) == 0
    ):
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


def _infer_stub_column_span(headers: list[str]) -> int:
    """Infer leading stub columns before treatment measure columns."""
    for index, header in enumerate(headers):
        if " | " in header:
            return max(1, index)
    return len(headers)


def _normalize_body_rows(
    *,
    rows: list[ParsedRow],
    width: int,
    header_row_1: list[str],
    header_row_2: list[str],
    stub_column_span: int,
) -> list[list[str]]:
    """Normalize body rows and enforce consistent body width."""
    filtered_rows: list[ParsedRow] = []
    for row in rows:
        row_values = [cell.text for cell in row.cells]
        if _is_repeated_header_row(
            row_values=row_values,
            header_row_1=header_row_1,
            header_row_2=header_row_2,
        ):
            continue
        filtered_rows.append(row)

    normalized_rows: list[list[str]] = []
    last_first_cell_value = ""
    for index, row in enumerate(filtered_rows):
        row_values = [cell.text for cell in row.cells]

        if len(row_values) != width:
            future_rows = filtered_rows[index + 1 :]
            has_future_matching_width = any(
                len([cell.text for cell in future_row.cells]) == width
                for future_row in future_rows
            )
            if has_future_matching_width:
                raise ValueError("RTF table contained inconsistent row width.")
            continue

        # Preserve group label continuity when a continuation row leaves the
        # first cell blank under vertical merge controls.
        if row_values[0]:
            last_first_cell_value = row_values[0]
        elif (
            stub_column_span == 1
            and row.cells
            and row.cells[0].v_merge_continue
            and last_first_cell_value
        ):
            row_values[0] = last_first_cell_value

        normalized_rows.append(row_values)
    return normalized_rows


def _is_repeated_header_row(
    *,
    row_values: list[str],
    header_row_1: list[str],
    header_row_2: list[str],
) -> bool:
    """Return True when a body row duplicates one of the header rows."""
    return row_values == header_row_1 or row_values == header_row_2
