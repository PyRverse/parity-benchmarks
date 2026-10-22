import json
import math

import numpy as np
import pytest

from pyrverse_parity import Tolerance, compare_arrays, compare_tables, write_reports


def check(reference, actual, *, atol=0.0, rtol=0.0, equal_nan=False):
    return compare_arrays(
        reference, actual, name="test", tolerance=Tolerance(atol, rtol, equal_nan)
    )


def test_exact_and_scalar():
    assert check([[1, 2], [3, 4]], [[1, 2], [3, 4]])["passed"]
    assert check(3.0, 3.0)["passed"]
    assert check(3.0, 4.0)["examples"] == [{"index": [], "reference": 3.0, "actual": 4.0}]


def test_absolute_tolerance_near_zero_and_relative_tolerance():
    assert check([0], [1e-10], atol=1e-9)["passed"]
    assert check([1e6], [1e6 + 1], rtol=2e-6)["passed"]
    assert not check([1e6], [1e6 + 1], rtol=5e-7)["passed"]


def test_errors_and_mismatch_indices():
    result = check([0, 2, 4], [0, 3, 6])
    assert result["mismatches"] == 2
    assert result["max_absolute_error"] == 2
    assert result["max_relative_error"] == pytest.approx(0.5)
    assert result["examples"][0]["index"] == [1]
    assert math.isinf(check([0], [1])["max_relative_error"])


def test_nonfinite_policy_and_sign():
    values = [np.nan, np.inf, -np.inf]
    assert not check(values, values)["passed"]
    match = check(values, values, equal_nan=True)
    assert match["passed"]
    assert match["matched_nan_pairs"] == 1
    assert match["matched_infinity_pairs"] == 2
    assert match["max_absolute_error"] is None
    assert not check([np.inf], [-np.inf])["passed"]
    assert not check([np.nan], [0], equal_nan=True)["passed"]
    assert not check([1], [np.inf], atol=1e100)["passed"]


def test_shapes_never_broadcast_and_empty_is_explicit():
    assert not check([[1, 2]], [1, 2])["passed"]
    empty = check([], [])
    assert empty["passed"] and empty["total"] == 0
    assert "no numerical evidence" in empty["note"]
    assert not check(np.empty((0, 2)), np.empty((0, 3)))["passed"]


def test_overflow_does_not_create_false_match():
    result = check([1.7e308], [-1.7e308], rtol=1.5)
    assert not result["passed"]
    assert math.isinf(result["max_absolute_error"])
    assert result["max_relative_error"] == 2


@pytest.mark.parametrize("value", [-1.0, float("inf"), float("nan")])
def test_invalid_tolerance(value):
    with pytest.raises(ValueError):
        Tolerance(atol=value, rtol=0)
    with pytest.raises(ValueError):
        Tolerance(atol=0, rtol=value)


@pytest.mark.parametrize("value", [["1"], [1j], [True]])
def test_reject_implicit_numeric_conversion(value):
    with pytest.raises(TypeError):
        check(value, value)


@pytest.mark.parametrize(
    ("reference", "actual"),
    [
        ([2**53], [2**53 + 1]),
        (np.array([2**53], dtype=np.int64), np.array([2**53 + 1], dtype=np.int64)),
        ([0.0, 2**53], [0.0, 2**53 + 1]),
        ([[2**53, 0.0]], [[2**53 + 1, 0.0]]),
        ([0], np.array([2**64 - 1], dtype=np.uint64)),
        ([0], [10**400]),
    ],
)
def test_reject_integer_precision_loss_before_numpy_coercion(reference, actual):
    with pytest.raises(ValueError, match="not exactly representable as float64"):
        check(reference, actual)


def test_exactly_representable_large_integers_remain_valid():
    assert check([2**53 + 2], [2**53 + 2])["passed"]
    assert not check([2**53], [2**53 + 2])["passed"]


def test_tables_align_columns_but_require_row_order():
    ref = {"mean": [1.0, 2.0], "variance": [0.1, 0.2]}
    got = {"variance": [0.1, 0.2], "mean": [1.0, 2.0]}
    kwargs = {
        "reference_index": ["a", "b"],
        "actual_index": ["a", "b"],
        "name": "table",
        "tolerance": Tolerance(0, 0),
    }
    assert compare_tables(ref, got, **kwargs)["passed"]
    kwargs["actual_index"] = ["b", "a"]
    assert not compare_tables(ref, got, **kwargs)["passed"]
    kwargs["actual_index"] = ["a", "b"]
    assert not compare_tables(ref, {"mean": [1, 2]}, **kwargs)["passed"]


def test_tables_reject_duplicate_ids_and_bad_lengths():
    kwargs = {
        "reference_index": ["a", "a"],
        "actual_index": ["a", "a"],
        "name": "table",
        "tolerance": Tolerance(0, 0),
    }
    with pytest.raises(ValueError, match="unique"):
        compare_tables({"a": [1, 2]}, {"a": [1, 2]}, **kwargs)
    kwargs.update(reference_index=["a"], actual_index=["a"])
    with pytest.raises(ValueError, match="one-dimensional"):
        compare_tables({"a": [1, 2]}, {"a": [1, 2]}, **kwargs)


def test_strict_json_handles_nonfinite_failures_and_markdown(tmp_path):
    comparison = check([0, np.inf, np.nan], [1, -np.inf, 4])
    comparison["name"] = "a|b"
    json_path, md_path = write_reports(
        {"status": "fail", "comparisons": [comparison], "metadata": {}},
        tmp_path,
    )

    def reject(token):
        raise AssertionError(f"Invalid JSON token {token}")

    decoded = json.loads(json_path.read_text(), parse_constant=reject)
    result = decoded["comparisons"][0]
    assert result["max_relative_error"] == "Infinity"
    assert result["examples"][1]["reference"] == "Infinity"
    assert result["examples"][2]["reference"] == "NaN"
    assert "**FAIL**" in md_path.read_text()
    assert "a\\|b" in md_path.read_text()
