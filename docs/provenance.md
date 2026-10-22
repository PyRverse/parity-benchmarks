# Provenance and licensing

The initial dataset is original synthetic numeric data created for this repository.
The small R driver calls public `base::mean` and `stats::var` APIs. The Python example
uses NumPy mean and sample variance (`ddof=1`). No R source code was copied or
translated. This framework and its original files use MIT; that choice is not a
license recommendation for future R-to-Python ports.

The committed fixture was actually generated in R. Its exact runtime version, UTC
generation timestamp, source/data/output hashes, and missing-value mapping are in
[`reference/provenance.json`](../reference/provenance.json). The accompanying
[`session-info.txt`](../reference/session-info.txt) records the R environment.
The generator stores no local executable path or user name. Generation uses no random
numbers, so no random seed is needed. Hash checks detect fixture/source changes;
they are not a cryptographic attestation of who ran the calculation.

Reference behavior was checked against official R documentation:

- [Arithmetic mean](https://stat.ethz.ch/R-manual/R-devel/library/base/html/mean.html).
- [Variance and covariance](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/cor.html),
  including the `n - 1` denominator and undefined singleton variance.
- [NumPy mean](https://numpy.org/doc/stable/reference/generated/numpy.mean.html) and
  [variance](https://numpy.org/doc/stable/reference/generated/numpy.var.html), including
  the `N - ddof` divisor.
- [R licensing](https://www.r-project.org/COPYING), which governs R itself separately.

Future contributions must record upstream authors, citations, source versions,
license identifiers and notices, data licenses, and whether implementation work
uses copied, translated, or independently written code. Review obligations before
distribution; a language change alone does not remove them. Resolve uncertain cases
with qualified review before incorporating upstream material.

CI uses the current documented v7 majors for
[checkout](https://github.com/actions/checkout),
[setup-python](https://github.com/actions/setup-python), and
[upload-artifact](https://github.com/actions/upload-artifact), checked on 2026-10-22.
Dependabot checks Python and Actions dependencies monthly. CI compares against the
committed R fixture; it does not regenerate R outputs on every pull request.
