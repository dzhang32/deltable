"""Compare loaded table data and classify differences."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import polars as pl
from datacompy.polars import PolarsCompare

from deltable.rtf_table import load_rtf_table

type ComparisonCategory = Literal[
    "identical",
    "data_differences",
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
        abs_tol: Absolute numeric tolerance used by DataCompPy.
        rel_tol: Relative numeric tolerance used by DataCompPy.
        ignore_case: Whether string comparisons should ignore case.
        ignore_spaces: Whether string comparisons should ignore spaces.

    Returns:
        Classified comparison result.
    """
    join_columns = _infer_join_columns(left.columns)
    if missing_columns := [
        column for column in join_columns if column not in right.columns
    ]:
        summary = (
            "Structure differs: inferred join columns are missing in the right "
            f"table ({', '.join(missing_columns)})."
        )
        return TableComparisonResult(
            category="structure_differences",
            summary=summary,
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

    compare = PolarsCompare(
        normalized_left,
        normalized_right,
        join_columns=list(join_columns),
        abs_tol=abs_tol,
        rel_tol=rel_tol,
        ignore_case=False,
        ignore_spaces=False,
        cast_column_names_lower=False,
    )

    strict_column_match = left.columns == right.columns
    all_columns_match = strict_column_match and bool(compare.all_columns_match())
    all_rows_overlap = bool(compare.all_rows_overlap())
    intersect_rows_match = bool(compare.intersect_rows_match())
    category = _classify_outcome(
        all_columns_match=all_columns_match,
        all_rows_overlap=all_rows_overlap,
        intersect_rows_match=intersect_rows_match,
    )
    summary = _build_summary(
        category=category,
        strict_column_match=strict_column_match,
        all_rows_overlap=all_rows_overlap,
        abs_tol=abs_tol,
        rel_tol=rel_tol,
        ignore_case=ignore_case,
        ignore_spaces=ignore_spaces,
    )

    return TableComparisonResult(
        category=category,
        summary=summary,
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
    """Load two RTF tables and compare them with DataCompPy."""
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


def _infer_join_columns(headers: list[str]) -> tuple[str, ...]:
    """Infer row-identity keys from leading stub columns."""
    if not headers:
        raise ValueError("Cannot infer join columns from an empty schema.")

    for index, header in enumerate(headers):
        if " | " in header:
            return tuple(headers[: max(1, index)])
    return (headers[0],)


def _classify_outcome(
    *,
    all_columns_match: bool,
    all_rows_overlap: bool,
    intersect_rows_match: bool,
) -> ComparisonCategory:
    """Map compare diagnostics to a comparison category."""
    if not all_columns_match or not all_rows_overlap:
        return "structure_differences"
    if not intersect_rows_match:
        return "data_differences"
    return "identical"


def _build_summary(
    *,
    category: ComparisonCategory,
    strict_column_match: bool,
    all_rows_overlap: bool,
    abs_tol: float,
    rel_tol: float,
    ignore_case: bool,
    ignore_spaces: bool,
) -> str:
    """Build a short human-readable summary for the classification."""
    options = (
        f"abs_tol={abs_tol}, rel_tol={rel_tol}, ignore_case={ignore_case}, "
        f"ignore_spaces={ignore_spaces}"
    )
    if category == "identical":
        return f"Tables are identical under comparison options ({options})."

    if category == "data_differences":
        return (
            "Structure matches, but value differences were found in overlapping "
            f"rows under options ({options})."
        )

    if not strict_column_match and not all_rows_overlap:
        return (
            "Structure differs in both schema (column order/names) and row membership."
        )
    if not strict_column_match:
        return "Structure differs: column names/order do not match exactly."
    return "Structure differs: row membership does not fully overlap."


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
