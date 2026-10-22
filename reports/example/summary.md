# Numerical comparison report

Overall: **PASS**

This result applies only to the recorded inputs, implementation, and tolerances.

| Comparison | Result | Mismatches | Max absolute error | Max relative error |
| --- | --- | ---: | ---: | ---: |
| mean | PASS | 0 | 0.0 | 0.0 |
| sample_variance | PASS | 0 | 0.0 | 0.0 |

Errors summarize finite pairs only. Matching NaNs and signed infinities
are counted separately in JSON. Relative error at a zero reference is 0
for exact equality and Infinity otherwise. n/a means no finite pairs.

## Reproduction metadata

```json
{
  "reference": {
    "origin": "executed R reference/generate.R",
    "generated_at_utc": "2026-10-22T16:41:43.550572+00:00",
    "r_version": "R version 4.6.1 (2026-06-24 ucrt)",
    "command": "Rscript --vanilla reference/generate.R",
    "missing_value_mapping": "R NA and NaN are serialized as NaN; distinction is not tested",
    "sha256": {
      "datasets/summary.csv": "cd8618e1cd4ed3a6dab292724d0a552d49c65357de4e547db0adac89dc97c835",
      "reference/generate.R": "3693344349d38e46dd88fb5b44847eae33b8dcd0323741c226acc41fe3ea42c9",
      "reference/generate.py": "7c5faa9b315037ef9460385e3e08e6460a64547eb8e05f8d3ff2fda56901d485",
      "reference/summary.csv": "5da0482f37305fe1b8ebb000a1b3c66a2cbd6a0d01b9618b14df9702d1afbbbc",
      "reference/session-info.txt": "22d2bcbbe96ed0286a6e63e98d7d211081e4a0171d499331de71a8a3b0bd8fb1"
    }
  },
  "python_version": "3.12.10",
  "numpy_version": "2.5.4",
  "config": {
    "name": "Arithmetic mean and sample variance on 12 synthetic edge cases",
    "tolerance": {
      "atol": 1e-12,
      "rtol": 1e-12,
      "equal_nan": true
    },
    "rationale": "Small deterministic float64 examples with simple arithmetic. These tolerances are specific to this example and are not a default for statistical methods.",
    "scope": "Point estimates and explicit missing/infinity behavior; not p-values, inference, model fitting, performance, or arbitrary datasets."
  },
  "python_source_sha256": "2b937c82605a34824637b3b6c7164b9a65c3fc06a6fc5e69feaaed72310616b3",
  "comparator_sha256": "646351e478ceb94f23631f9e74c871c65cc9b9eb6d3f6186f4e655fd70bc5155"
}
```
