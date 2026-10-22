# Designing a meaningful comparison

The comparator checks `abs(actual - reference) <= atol + rtol * abs(reference)`.
The reference is deliberately the scale for relative tolerance. Choose tolerances
before inspecting a candidate's failures, based on floating-point precision,
conditioning, output scale, and scientific consequences. Record a rationale for
every comparison; one threshold cannot validate all statistical methods.

Exact shapes are required. Tables match columns by name and require identical row
order and unique row IDs; align deliberately before comparing. The current API is
for real numeric columns only, converts to float64, and does not validate categorical
data or preserve large integers beyond float64's exact range. Check metadata,
categorical outputs, and large integer counts separately.

Matching signed infinities pass. A finite/infinite pair or opposite infinities fails.
NaNs match only with `equal_nan=True`; check why missing results occurred before
using that setting. Empty arrays pass structurally and provide no numerical evidence.
R distinguishes `NA` from `NaN`; the example deliberately collapses both to NumPy NaN
and therefore does not test that distinction.

Reports include maximum absolute and relative errors over finite pairs and counts
of non-finite matches. At a zero reference, relative error is zero for equality and
infinite otherwise. JSON encodes non-finite diagnostics as strings `"NaN"`,
`"Infinity"`, or `"-Infinity"`; `null` means no finite error summary exists. Up to ten
failed positions are retained, with a total mismatch count. Extreme absolute errors
can overflow to Infinity; scaled comparisons still avoid accepting an overflowed
difference solely because its tolerance also overflowed.

For actual scientific methods, also evaluate:

- P-values, adjusted p-values, confidence intervals, effect sizes, and decisions near
  meaningful cutoffs, including behavior around numerical zero.
- Convergence flags, iteration limits, warnings, singular fits, and invalid inputs.
- Missing-data handling, rank deficiency, constant variables, empty groups, and
  unequal group sizes.
- Randomness, seeds, BLAS/LAPACK and optimizer differences, stochastic distributions,
  permutation invariance, and scientifically justified metamorphic properties.
- Realistic and adversarial datasets, upstream examples, and independent analytical
  results where available. Respect data privacy and redistribution rights.

This example has no p-values, model fit, stochastic algorithm, or runtime performance
benchmark. Passing its twelve cases supports only its documented arithmetic scope.
