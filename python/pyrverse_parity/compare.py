"""Compare real numeric arrays without broadcasting or implicit table alignment."""

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class Tolerance:
    """A benchmark-specific policy: |actual - reference| <= atol + rtol*|reference|."""

    atol: float
    rtol: float
    equal_nan: bool = False

    def __post_init__(self) -> None:
        for name in ("atol", "rtol"):
            value = getattr(self, name)
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        if not isinstance(self.equal_nan, bool):
            raise TypeError("equal_nan must be a boolean")


def _numeric(values: ArrayLike) -> NDArray[np.float64]:
    # An object array preserves original Python integers even in mixed int/float
    # lists. np.asarray(values) could already round those integers before validation.
    original = np.asarray(values, dtype=object)
    for value in original.flat:
        if isinstance(value, (bool, np.bool_)) or not isinstance(
            value, (int, float, np.integer, np.floating)
        ):
            raise TypeError(
                "Expected real numeric values, not strings, booleans, or complex values"
            )
        if isinstance(value, (int, np.integer)):
            try:
                converted = float(value)
            except OverflowError as error:
                raise ValueError("Integer input is not exactly representable as float64") from error
            if not np.isfinite(converted) or int(converted) != int(value):
                raise ValueError("Integer input is not exactly representable as float64")
    return original.astype(np.float64)


def compare_arrays(
    reference: ArrayLike,
    actual: ArrayLike,
    *,
    name: str,
    tolerance: Tolerance,
) -> dict[str, Any]:
    """Return a report; shape mismatches fail without broadcasting.

    Empty arrays with the same shape pass as a structural check only. Matching
    signed infinities pass. NaNs match only when explicitly allowed by the policy.
    """
    ref, got = _numeric(reference), _numeric(actual)
    result: dict[str, Any] = {
        "name": name,
        "passed": False,
        "reference_shape": list(ref.shape),
        "actual_shape": list(got.shape),
        "tolerance": asdict(tolerance),
        "total": int(ref.size),
        "finite_pairs": 0,
        "mismatches": 0,
        "max_absolute_error": None,
        "max_relative_error": None,
        "examples": [],
    }
    if ref.shape != got.shape:
        result["reason"] = "shape mismatch; broadcasting is disabled"
        return result

    finite = np.isfinite(ref) & np.isfinite(got)
    same_inf = np.isinf(ref) & (ref == got)
    same_nan = np.isnan(ref) & np.isnan(got) & tolerance.equal_nan
    close = np.array(same_inf | same_nan, copy=True)
    left, right = ref[finite], got[finite]
    # Scaling avoids an inf <= inf false pass when subtraction or the tolerance
    # calculation would overflow for large but finite inputs.
    scale = np.maximum(np.abs(left), np.abs(right))
    scale[scale == 0] = 1
    with np.errstate(over="ignore", invalid="ignore", divide="ignore", under="ignore"):
        scaled_error = np.abs(right / scale - left / scale)
        absolute = np.abs(right - left)
        bound = tolerance.atol + tolerance.rtol * np.abs(left)
        within = absolute <= bound
        overflow = np.isinf(absolute) & np.isinf(bound)
        within[overflow] = scaled_error[overflow] <= (
            tolerance.atol / scale[overflow]
            + tolerance.rtol * (np.abs(left[overflow]) / scale[overflow])
        )
        close[finite] = within
        relative = np.where(
            left == 0,
            np.where(right == 0, 0.0, np.inf),
            np.where(
                np.isinf(absolute), scaled_error * (scale / np.abs(left)), absolute / np.abs(left)
            ),
        )
    bad = ~close
    result.update(
        passed=bool(np.all(close)),
        finite_pairs=int(np.count_nonzero(finite)),
        mismatches=int(np.count_nonzero(bad)),
        matched_nan_pairs=int(np.count_nonzero(same_nan)),
        matched_infinity_pairs=int(np.count_nonzero(same_inf)),
        max_absolute_error=float(np.max(absolute)) if absolute.size else None,
        max_relative_error=float(np.max(relative)) if relative.size else None,
    )
    if not ref.size:
        result["note"] = "empty arrays: no numerical evidence"
    for flat_index in np.flatnonzero(bad)[:10]:
        index = np.unravel_index(flat_index, ref.shape)
        result["examples"].append(
            {
                "index": [int(i) for i in index],
                "reference": float(ref[index]),
                "actual": float(got[index]),
            }
        )
    return result


def compare_tables(
    reference: Mapping[str, ArrayLike],
    actual: Mapping[str, ArrayLike],
    *,
    reference_index: Sequence[str],
    actual_index: Sequence[str],
    name: str,
    tolerance: Tolerance,
) -> dict[str, Any]:
    """Compare numeric columns by name, requiring unique, identically ordered row IDs."""
    ref_ids, got_ids = list(reference_index), list(actual_index)
    if len(set(ref_ids)) != len(ref_ids) or len(set(got_ids)) != len(got_ids):
        raise ValueError("Table row IDs must be unique")
    if any(not isinstance(key, str) for key in (*reference, *actual)):
        raise TypeError("Table column names must be strings")
    if ref_ids != got_ids or set(reference) != set(actual):
        return {
            "name": name,
            "passed": False,
            "reason": "table row IDs or columns differ",
            "columns": [],
        }
    columns = []
    for column, values in reference.items():
        left, right = _numeric(values), _numeric(actual[column])
        if left.shape != (len(ref_ids),) or right.shape != (len(got_ids),):
            raise ValueError("Every table column must be one-dimensional and match its row IDs")
        columns.append(compare_arrays(left, right, name=column, tolerance=tolerance))
    return {
        "name": name,
        "passed": all(c["passed"] for c in columns),
        "row_ids": ref_ids,
        "columns": columns,
    }
