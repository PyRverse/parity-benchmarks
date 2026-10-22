# PyRverse parity benchmarks

**Reproducible cross-language benchmarks for scientific Python implementations.**

A small working foundation for comparing Python results with recorded R outputs.
The first example compares arithmetic means and sample variances on twelve synthetic
datasets, including missing values, infinities, empty vectors, and constant data.
It establishes no parity claim for an R package or production statistical method.

## Run the example

Use Python 3.11 or later from the repository root:

```bash
python -m venv .venv
# POSIX: source .venv/bin/activate
# PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
pytest
ruff check .
pyrverse-parity --output reports/latest
```

The command writes `reports/latest/report.json` and `reports/latest/summary.md`.
It exits 1 for a comparison failure. Provenance or input errors also exit nonzero.
Python-only checks use the committed fixture and do not need R. The checked-in
[example report](reports/example/summary.md) records one actual local execution;
fresh reports include your Python/NumPy versions and implementation hashes.

To regenerate the reference using a locally installed R runtime:

```bash
python reference/generate.py
# If Rscript is not on PATH:
python reference/generate.py --rscript /path/to/Rscript
```

This executes `reference/generate.R`, records the R session and file hashes, and
replaces the reference fixture. Review the changed outputs and provenance before
committing them. No R packages beyond base/stats are needed. R is only required
for reference generation, not the Python implementation.

## What is implemented

- Real numeric arrays with strict shape checks and no broadcasting.
- Numeric tables with named columns and explicit, unique row IDs.
- Explicit absolute/relative tolerances for each comparison.
- NaN policy, signed infinity matching, and finite error summaries.
- Strict JSON reports and readable Markdown summaries.
- Dataset, generator, output, and session hashes checked before each example run.
- Fast pytest checks and a small Python CI matrix.

Use the Python API for other comparisons:

```python
from pyrverse_parity import Tolerance, compare_arrays

result = compare_arrays(
    [1.0, 2.0], [1.0, 2.00000001], name="illustrative values",
    tolerance=Tolerance(atol=1e-10, rtol=1e-7),
)
assert result["passed"]
```

Those example tolerances are not scientific recommendations. Read the
[validation guide](docs/validation.md) before adding a method. Inference requires
more than matching point estimates: test p-values, convergence, test decisions,
edge cases, and statistical assumptions.

## Repository map

| Path | Purpose |
| --- | --- |
| `reference/` | R generator, actual outputs, and provenance |
| `python/` | Comparison/report code and NumPy example |
| `datasets/` | Small original synthetic datasets |
| `comparisons/` | Explicit comparison configuration |
| `reports/` | Example report; local runs are ignored |
| `docs/` | Scientific validation and licensing notes |
| `tests/` | Numerical, structural, provenance, and CLI tests |

See [contribution guidance](CONTRIBUTING.md) and [provenance](docs/provenance.md).
This repository's original framework, examples, and synthetic data use the
[MIT license](LICENSE). Licenses for future reference implementations and datasets
must be assessed individually. PyRverse is an independent community effort.
