import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from pyrverse_parity.example import run_example, summary

ROOT = Path(__file__).resolve().parents[1]


def test_r_fixture_example_and_reports(tmp_path):
    report = run_example(ROOT, tmp_path)
    assert report["status"] == "pass"
    assert report["metadata"]["reference"]["origin"] == "executed R reference/generate.R"
    assert len(report["comparisons"][0]["row_ids"]) == 12
    assert (tmp_path / "report.json").is_file()
    assert "**PASS**" in (tmp_path / "summary.md").read_text()


def test_known_statistics():
    assert summary([1, 2, 3, 4, 5], remove_missing=False) == (3.0, 2.5)
    assert summary([7, 7, 7], remove_missing=False) == (7.0, 0.0)


def test_tampered_fixture_is_rejected(tmp_path):
    for directory in ("reference", "datasets", "comparisons"):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    (tmp_path / "reference/summary.csv").write_text("tampered")
    with pytest.raises(ValueError, match="provenance hash mismatch"):
        run_example(tmp_path, tmp_path / "report")


def test_cli_exit_status_is_nonzero_for_numerical_failure(tmp_path):
    for directory in ("reference", "datasets", "comparisons"):
        shutil.copytree(ROOT / directory, tmp_path / directory)
    config_path = tmp_path / "comparisons/summary.json"
    config = json.loads(config_path.read_text())
    config["tolerance"]["equal_nan"] = False
    config_path.write_text(json.dumps(config))
    env = {**os.environ, "PYTHONPATH": str(ROOT / "python")}
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pyrverse_parity.example",
            "--root",
            str(tmp_path),
            "--output",
            str(tmp_path / "reports"),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert completed.returncode == 1, completed.stderr
    assert "FAIL" in completed.stdout
    assert json.loads((tmp_path / "reports/report.json").read_text())["status"] == "fail"
