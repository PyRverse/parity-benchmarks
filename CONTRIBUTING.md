# Contributing

Start with a small, independently reproducible comparison. Document the upstream
method, version, citation, license, dataset origin, parameters, random seed where
applicable, and intended scientific use. Do not copy or translate upstream source
without reviewing its license and preserving all required notices.

Generate reference outputs in the real reference runtime, retaining the generator,
session information, data, and output hashes. Review the reference output separately
from the candidate implementation. A Python-generated expected value must never be
labeled as R-generated.

Explain tolerance choices for each quantity and dataset. Add useful failure cases,
including mismatched labels, non-finite results, and degenerate inputs. Include
scientific validation appropriate to the method, not just this numerical comparator.

Run `pytest`, `ruff check .`, and `pyrverse-parity` from the repository root. Keep
fixtures small enough for routine CI; document larger experiments separately.
Pull requests should state changed behavior, provenance, expected differences,
validation results, and limitations. Reviewers should be able to reproduce the work.

For community expectations, see the organization's
[code of conduct](https://github.com/PyRverse/.github/blob/main/CODE_OF_CONDUCT.md).
