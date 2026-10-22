"""Numerical comparisons with explicit tolerances and reference provenance."""

from .compare import Tolerance, compare_arrays, compare_tables
from .report import write_reports

__all__ = ["Tolerance", "compare_arrays", "compare_tables", "write_reports"]
