"""Strict JSON and Markdown exports of the same comparison results."""

import json
import math
from pathlib import Path
from typing import Any


def json_safe(value: Any) -> Any:
    """Represent non-finite diagnostic numbers with strings, never invalid JSON tokens."""
    if isinstance(value, float) and not math.isfinite(value):
        return "NaN" if math.isnan(value) else ("Infinity" if value > 0 else "-Infinity")
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def _cell(value: Any) -> str:
    if value is None:
        return "n/a"
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_reports(report: dict[str, Any], output: Path) -> tuple[Path, Path]:
    """Write report.json and summary.md, creating the requested output directory."""
    output.mkdir(parents=True, exist_ok=True)
    safe = json_safe(report)
    json_path, markdown_path = output / "report.json", output / "summary.md"
    json_path.write_text(
        json.dumps(safe, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n"
    )
    lines = [
        "# Numerical comparison report",
        "",
        f"Overall: **{safe['status'].upper()}**",
        "",
        "This result applies only to the recorded inputs, implementation, and tolerances.",
        "",
        "| Comparison | Result | Mismatches | Max absolute error | Max relative error |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for result in safe["comparisons"]:
        for row in result.get("columns", [result]):
            cells = [
                row["name"],
                "PASS" if row["passed"] else "FAIL",
                row.get("mismatches"),
                row.get("max_absolute_error"),
                row.get("max_relative_error"),
            ]
            lines.append("| " + " | ".join(_cell(c) for c in cells) + " |")
        if not result["passed"] and result.get("reason"):
            lines.extend(["", f"Failure: {_cell(result['reason'])}"])
    lines.extend(
        [
            "",
            "Errors summarize finite pairs only. Matching NaNs and signed infinities",
            "are counted separately in JSON. Relative error at a zero reference is 0",
            "for exact equality and Infinity otherwise. n/a means no finite pairs.",
            "",
            "## Reproduction metadata",
            "",
            "```json",
            json.dumps(safe.get("metadata", {}), indent=2, allow_nan=False),
            "```",
            "",
        ]
    )
    markdown_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return json_path, markdown_path
