"""Run NumPy summary statistics against the committed R-generated fixture."""

import argparse
import csv
import hashlib
import json
import platform
import warnings
from pathlib import Path

import numpy as np

from .compare import Tolerance, compare_tables
from .report import write_reports


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cases(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summary(values: list[float], *, remove_missing: bool) -> tuple[float, float]:
    """Arithmetic mean and sample variance; R NA and NaN both map to NumPy NaN."""
    data = np.asarray(values, dtype=float)
    if remove_missing:
        data = data[~np.isnan(data)]
    # These cases are intentional: empty/singleton data and non-finite arithmetic
    # have undefined statistics. Suppress only NumPy RuntimeWarnings in this example.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(np.mean(data)), float(np.var(data, ddof=1))


def run_example(root: Path, output: Path) -> dict:
    provenance = json.loads((root / "reference/provenance.json").read_text(encoding="utf-8"))
    for path, expected in provenance["sha256"].items():
        if sha256(root / path) != expected:
            raise ValueError(f"Reference provenance hash mismatch: {path}; regenerate in R")
    config = json.loads((root / "comparisons/summary.json").read_text(encoding="utf-8"))
    tolerance = Tolerance(**config["tolerance"])
    cases = load_cases(root / "datasets/summary.csv")
    reference = load_cases(root / "reference/summary.csv")
    actual = {"mean": [], "sample_variance": []}
    for row in cases:
        values = [float(v) for v in row["values"].split(";")] if row["values"] else []
        mean, variance = summary(values, remove_missing=row["remove_missing"] == "true")
        actual["mean"].append(mean)
        actual["sample_variance"].append(variance)
    expected = {column: [float(row[column]) for row in reference] for column in actual}
    comparison = compare_tables(
        expected,
        actual,
        reference_index=[row["case"] for row in reference],
        actual_index=[row["case"] for row in cases],
        name="R/NumPy summary statistics",
        tolerance=tolerance,
    )
    report = {
        "schema_version": 1,
        "status": "pass" if comparison["passed"] else "fail",
        "metadata": {
            "reference": provenance,
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "config": config,
            "python_source_sha256": sha256(Path(__file__)),
            "comparator_sha256": sha256(Path(__file__).with_name("compare.py")),
        },
        "comparisons": [comparison],
    }
    write_reports(report, output)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--output", type=Path, default=Path("reports/latest"))
    args = parser.parse_args()
    report = run_example(args.root.resolve(), args.output.resolve())
    print(f"{report['status'].upper()}: {args.output / 'summary.md'}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
