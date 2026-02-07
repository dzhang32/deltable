"""Compare loaded table data and classify differences."""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from deltable.rtf_table import TableData, load_rtf_table

ComparisonCategory = Literal[
    "identical",
    "structure_differences",
]

WHITESPACE_PATTERN = re.compile(r"\s+")


@dataclass(frozen=True, slots=True, kw_only=True)
class TableComparisonResult:
    """Represent a classified table comparison outcome."""

    category: ComparisonCategory
    summary: str


def compare_tables(
    left: TableData,
    right: TableData,
    *,
    abs_tol: float = 0.0,
    rel_tol: float = 0.0,
    ignore_case: bool = False,
    ignore_spaces: bool = False,
) -> TableComparisonResult:
    """Compare two column-oriented tables and classify the result.

    Args:
        left: Left-hand table to compare.
        right: Right-hand table to compare.
        abs_tol: Absolute numeric tolerance for numeric values.
        rel_tol: Relative numeric tolerance for numeric values.
        ignore_case: Whether string comparisons should ignore case.
        ignore_spaces: Whether string comparisons should ignore spaces.

    Returns:
        Classified comparison result.

    Raises:
        ValueError: If a table has inconsistent column lengths.
    """
    left_columns = list(left.keys())
    right_columns = list(right.keys())
    if left_columns != right_columns:
        return TableComparisonResult(
            category="structure_differences",
            summary=(
                "Structure differs: column names/order do not match exactly "
                f"(left={left_columns}, right={right_columns})."
            ),
        )

    left_row_count = _get_row_count(left, label="left")
    right_row_count = _get_row_count(right, label="right")
    if left_row_count != right_row_count:
        return TableComparisonResult(
            category="structure_differences",
            summary=(
                "Structure differs: row count does not match "
                f"(left={left_row_count}, right={right_row_count})."
            ),
        )

    normalized_left = _normalize_string_columns(
        left,
        ignore_case=ignore_case,
        ignore_spaces=ignore_spaces,
    )
    normalized_right = _normalize_string_columns(
        right,
        ignore_case=ignore_case,
        ignore_spaces=ignore_spaces,
    )

    for column in left_columns:
        mismatch = _find_first_column_mismatch(
            left_values=normalized_left[column],
            right_values=normalized_right[column],
            abs_tol=abs_tol,
            rel_tol=rel_tol,
        )
        if mismatch is None:
            continue

        row_index, left_value, right_value = mismatch
        return TableComparisonResult(
            category="structure_differences",
            summary=(
                "Structure differs: value mismatch at column "
                f"{column!r}, row {row_index} "
                f"(left={left_value!r}, right={right_value!r})."
            ),
        )

    return TableComparisonResult(
        category="identical",
        summary=_build_identical_summary(
            abs_tol=abs_tol,
            rel_tol=rel_tol,
            ignore_case=ignore_case,
            ignore_spaces=ignore_spaces,
        ),
    )


def compare_rtf_tables(
    left_path: Path | str,
    right_path: Path | str,
    *,
    abs_tol: float = 0.0,
    rel_tol: float = 0.0,
    ignore_case: bool = False,
    ignore_spaces: bool = False,
) -> TableComparisonResult:
    """Load two RTF tables and compare them."""
    left = load_rtf_table(left_path)
    right = load_rtf_table(right_path)
    return compare_tables(
        left,
        right,
        abs_tol=abs_tol,
        rel_tol=rel_tol,
        ignore_case=ignore_case,
        ignore_spaces=ignore_spaces,
    )


def _get_row_count(table: TableData, *, label: str) -> int:
    """Return table row count and ensure column lengths are consistent."""
    if not table:
        return 0

    row_counts = {len(values) for values in table.values()}
    if len(row_counts) != 1:
        raise ValueError(f"{label} table has inconsistent column lengths.")

    return next(iter(row_counts))


def _build_identical_summary(
    *,
    abs_tol: float,
    rel_tol: float,
    ignore_case: bool,
    ignore_spaces: bool,
) -> str:
    """Build a short human-readable summary for identical tables."""
    options = (
        f"abs_tol={abs_tol}, rel_tol={rel_tol}, ignore_case={ignore_case}, "
        f"ignore_spaces={ignore_spaces}"
    )
    return f"Tables are identical under comparison options ({options})."


def _find_first_column_mismatch(
    *,
    left_values: Sequence[Any],
    right_values: Sequence[Any],
    abs_tol: float,
    rel_tol: float,
) -> tuple[int, Any, Any] | None:
    """Return the first mismatching row index and values for a column."""
    for row_index, (left_value, right_value) in enumerate(
        zip(left_values, right_values, strict=True)
    ):
        if _values_match(
            left_value=left_value,
            right_value=right_value,
            abs_tol=abs_tol,
            rel_tol=rel_tol,
        ):
            continue
        return (row_index, left_value, right_value)

    return None


def _values_match(
    *,
    left_value: Any,
    right_value: Any,
    abs_tol: float,
    rel_tol: float,
) -> bool:
    """Check whether two values should be considered equal."""
    if left_value is None and right_value is None:
        return True
    if left_value is None or right_value is None:
        return False

    if (
        isinstance(left_value, (int, float))
        and not isinstance(left_value, bool)
        and isinstance(right_value, (int, float))
        and not isinstance(right_value, bool)
    ):
        return _numbers_match(
            left_value=float(left_value),
            right_value=float(right_value),
            abs_tol=abs_tol,
            rel_tol=rel_tol,
        )

    return left_value == right_value


def _numbers_match(
    *,
    left_value: float,
    right_value: float,
    abs_tol: float,
    rel_tol: float,
) -> bool:
    """Check numeric equality with absolute and relative tolerance."""
    if math.isnan(left_value) and math.isnan(right_value):
        return True
    if math.isnan(left_value) or math.isnan(right_value):
        return False

    return math.isclose(
        left_value,
        right_value,
        abs_tol=abs_tol,
        rel_tol=rel_tol,
    )


def _normalize_string_columns(
    table: TableData,
    *,
    ignore_case: bool,
    ignore_spaces: bool,
) -> TableData:
    """Normalize string values before comparison."""
    if not ignore_case and not ignore_spaces:
        return {column: values.copy() for column, values in table.items()}

    normalized: TableData = {}
    for column, values in table.items():
        normalized_values: list[Any] = []
        for value in values:
            if not isinstance(value, str):
                normalized_values.append(value)
                continue

            normalized_value = value
            if ignore_case:
                normalized_value = normalized_value.lower()
            if ignore_spaces:
                normalized_value = WHITESPACE_PATTERN.sub("", normalized_value)

            normalized_values.append(normalized_value)

        normalized[column] = normalized_values

    return normalized
