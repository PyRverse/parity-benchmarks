"""Execute R, then record hashes of its real output; never synthesize R fixtures."""

import argparse
import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rscript", default="Rscript", help="Rscript executable or absolute path")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [args.rscript, "--vanilla", "reference/generate.R"],
        cwd=root,
        check=True,
        text=True,
        capture_output=True,
        env={**os.environ, "LC_ALL": "C", "LANG": "C"},
    )
    for generated in ("reference/summary.csv", "reference/session-info.txt"):
        path = root / generated
        normalized = "\n".join(
            line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()
        )
        path.write_text(normalized + "\n", encoding="utf-8", newline="\n")
    # Store no user name, home directory, or executable installation path.
    files = [
        "datasets/summary.csv",
        "reference/generate.R",
        "reference/generate.py",
        "reference/summary.csv",
        "reference/session-info.txt",
    ]
    metadata = {
        "origin": "executed R reference/generate.R",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "r_version": completed.stdout.strip(),
        "command": "Rscript --vanilla reference/generate.R",
        "missing_value_mapping": "R NA and NaN are serialized as NaN; distinction is not tested",
        "sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files},
    }
    (root / "reference/provenance.json").write_text(
        json.dumps(metadata, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(completed.stdout.strip())
    if completed.stderr:
        print(completed.stderr.strip())
    print("Recorded real R output and SHA-256 provenance.")


if __name__ == "__main__":
    main()
