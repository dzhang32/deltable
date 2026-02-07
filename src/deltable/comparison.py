"""Compare loaded table data and classify differences."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeIs

import polars as pl

from deltable.rtf_table import load_rtf_table

type ComparisonCategory = Literal[
    "identical",
    "structure_differences",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class TableComparisonResult:
    """Represent a classified table comparison outcome."""

    category: ComparisonCategory
    summary: str


def compare_dataframes(
    left: pl.DataFrame,
    right: pl.DataFrame,
    *,
    abs_tol: float = 0.0,
    rel_tol: float = 0.0,
    ignore_case: bool = False,
    ignore_spaces: bool = False,
) -> TableComparisonResult:
    """Compare two Polars DataFrames and classify the result.

    Args:
        left: Left-hand table to compare.
        right: Right-hand table to compare.
        abs_tol: Absolute numeric tolerance for numeric values.
        rel_tol: Relative numeric tolerance for numeric values.
        ignore_case: Whether string comparisons should ignore case.
        ignore_spaces: Whether string comparisons should ignore spaces.

    Returns:
        Classified comparison result.
    """
    if left.columns != right.columns:
        return TableComparisonResult(
            category="structure_differences",
            summary=(
                "Structure differs: column names/order do not match exactly "
                f"(left={left.columns}, right={right.columns})."
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

    if normalized_left.height != normalized_right.height:
        return TableComparisonResult(
            category="structure_differences",
            summary=(
                "Structure differs: row count does not match "
                f"(left={normalized_left.height}, right={normalized_right.height})."
            ),
        )

    for column in normalized_left.columns:
        mismatch = _find_first_column_mismatch(
            left_values=normalized_left.get_column(column).to_list(),
            right_values=normalized_right.get_column(column).to_list(),
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
    return compare_dataframes(
        left,
        right,
        abs_tol=abs_tol,
        rel_tol=rel_tol,
        ignore_case=ignore_case,
        ignore_spaces=ignore_spaces,
    )


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
    left_values: Sequence[object],
    right_values: Sequence[object],
    abs_tol: float,
    rel_tol: float,
) -> tuple[int, object, object] | None:
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
    left_value: object,
    right_value: object,
    abs_tol: float,
    rel_tol: float,
) -> bool:
    """Check whether two values should be considered equal."""
    if left_value is None and right_value is None:
        return True
    if left_value is None or right_value is None:
        return False

    if _is_numeric_value(left_value) and _is_numeric_value(right_value):
        return _numbers_match(
            left_value=float(left_value),
            right_value=float(right_value),
            abs_tol=abs_tol,
            rel_tol=rel_tol,
        )

    return left_value == right_value


def _is_numeric_value(value: object) -> TypeIs[int | float]:
    """Return whether a value should use numeric tolerance comparison."""
    return isinstance(value, int | float) and not isinstance(value, bool)


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
    dataframe: pl.DataFrame,
    *,
    ignore_case: bool,
    ignore_spaces: bool,
) -> pl.DataFrame:
    """Normalize string columns before comparison."""
    if not ignore_case and not ignore_spaces:
        return dataframe

    expressions: list[pl.Expr] = []
    for column, dtype in dataframe.schema.items():
        if dtype == pl.String:
            normalized_column = pl.col(column)
            if ignore_case:
                normalized_column = normalized_column.str.to_lowercase()
            if ignore_spaces:
                normalized_column = normalized_column.str.replace_all(
                    r"\s+",
                    "",
                )
            expressions.append(normalized_column.alias(column))
            continue
        expressions.append(pl.col(column))

    return dataframe.select(expressions)
