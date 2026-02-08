from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from deltable.error import HtmlComparisonError


@dataclass(frozen=True, slots=True, kw_only=True)
class ComparisonResult:
    """Outcome of a structural table comparison.

    Attributes:
        structure_match: True when every table pair is structurally
            equivalent.
        summary: Human-readable description of the comparison outcome.
    """

    structure_match: bool
    summary: str


def compare_html_tables(
    left_html_path: Path, right_html_path: Path
) -> ComparisonResult:
    """Compare table structure in two HTML files.

    Checks column layout, column types, row count, and row order.
    Numeric cell-value differences are intentionally ignored.
    String columns are compared after whitespace normalization.

    Args:
        left_path: Path to the first HTML file.
        right_path: Path to the second HTML file.

    Returns:
        A ComparisonResult indicating whether the tables are
        structurally equivalent and a human-readable summary.

    Raises:
        HtmlComparisonError: If a file does not exist or contains
            no parseable tables.
    """
    _validate_file_exists(left_html_path)
    _validate_file_exists(right_html_path)

    left_tables = _read_html_tables(left_html_path)
    right_tables = _read_html_tables(right_html_path)

    if len(left_tables) != len(right_tables):
        return ComparisonResult(
            structure_match=False,
            summary=(
                f"table count mismatch: "
                f"left={len(left_tables)}, right={len(right_tables)}"
            ),
        )

    for idx, (left, right) in enumerate(zip(left_tables, right_tables)):
        mismatch = _check_structure(left, right)
        if mismatch is not None:
            return ComparisonResult(
                structure_match=False,
                summary=f"structure mismatch at table index {idx}: {mismatch}",
            )

    return ComparisonResult(
        structure_match=True,
        summary=f"all tables identical ({len(left_tables)} table(s) compared)",
    )


def _validate_file_exists(path: Path) -> None:
    """Raise if *path* is not an existing regular file.

    Args:
        path: Filesystem path to validate.

    Raises:
        HtmlComparisonError: If the path does not exist or is not
            a file.
    """
    if not path.exists() or not path.is_file():
        raise HtmlComparisonError(f"file does not exist: {path}")


def _read_html_tables(path: Path) -> list[pd.DataFrame]:
    """Parse all ``<table>`` elements from an HTML file.

    Args:
        path: Path to the HTML file.

    Returns:
        A list of DataFrames, one per table found.

    Raises:
        HtmlComparisonError: If no tables can be parsed.
    """
    try:
        tables = pd.read_html(path, flavor="lxml")
    except ValueError as exc:
        raise HtmlComparisonError(
            f"Unable to parse HTML tables from {path}.",
        ) from exc
    return tables


def _check_structure(
    left: pd.DataFrame,
    right: pd.DataFrame,
) -> str | None:
    """Return a reason string if structure differs, otherwise None.

    Compares column names, row count, column type categories
    (numeric vs string after coercion), and string-column content
    with whitespace normalization.  Numeric columns are ignored.

    Args:
        left: First table as a DataFrame.
        right: Second table as a DataFrame.

    Returns:
        A short description of the structural mismatch, or None
        when the tables are structurally equivalent.
    """
    if list(left.columns) != list(right.columns):
        return "column mismatch"

    if len(left) != len(right):
        return "row count mismatch"

    left_typed = _coerce_numeric_columns(left)
    right_typed = _coerce_numeric_columns(right)

    left_cols_numeric = left_typed.select_dtypes(include="number").columns
    right_cols_numeric = right_typed.select_dtypes(include="number").columns
    if set(left_cols_numeric) != set(right_cols_numeric):
        return "column type mismatch"

    str_cols = [c for c in left_typed.columns if c not in left_cols_numeric]

    left_cols_str = left_typed[str_cols].map(_normalize_text, na_action="ignore")
    right_cols_str = right_typed[str_cols].map(_normalize_text, na_action="ignore")

    if left_cols_str.equals(right_cols_str):
        return None

    return "string content differs"


def _coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert columns to numeric where possible.

    Args:
        df: DataFrame whose columns may contain numeric data
            stored as strings.

    Returns:
        A copy of *df* with data columns converted to numeric
        dtype.
    """
    df_typed = df.copy()
    for col in df_typed.columns:
        # Try to convert the column to numeric.
        # Extract the leading number to account for 'n (%)' format.
        stripped = (
            df_typed[col]
            .astype(str)
            .str.extract(
                r"^\s*([\d.]+)",
                expand=False,
            )
        )
        numeric = pd.to_numeric(stripped, errors="coerce")

        if numeric.notna().mean() > 0.5:
            df_typed[col] = numeric

    return df_typed


def _normalize_text(value: str) -> str:
    """Collapse and strip whitespace for structural comparison.

    Args:
        value: Cell value from a string column.

    Returns:
        The string with leading/trailing whitespace stripped,
        internal runs of whitespace collapsed to a single space,
        and all characters lowercased.
    """
    return " ".join(value.lower().strip().split())
