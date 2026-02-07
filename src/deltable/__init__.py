"""Public package exports for deltable."""

from deltable.comparison import (
    TableComparisonResult,
    compare_dataframes,
    compare_rtf_tables,
)
from deltable.rtf_table import load_rtf_table

__all__ = [
    "TableComparisonResult",
    "compare_dataframes",
    "compare_rtf_tables",
    "load_rtf_table",
]
