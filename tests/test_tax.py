"""Tax tests. One of the rounding-boundary tests fails on the current code.

A bug_fixer agent is expected to:
  1. Run the suite, see test_rounding_boundary_de_19 fail.
  2. Locate the root cause in src/tax.py (int() truncation).
  3. Write a minimal patch using Decimal.quantize(..., ROUND_HALF_UP).
  4. Confirm test passes; no regression in existing tests.
"""

import pytest

from src.tax import calculate_tax, supported_jurisdictions, total_with_tax


class TestBasicCases:
    def test_zero_amount(self):
        assert calculate_tax(0, "DE") == 0

    def test_round_number_de_19(self):
        # 1000 * 0.19 = 190 exactly; truncation vs rounding agree.
        assert calculate_tax(1000, "DE") == 190

    def test_round_number_us_ca(self):
        # 10000 * 0.0725 = 725 exactly.
        assert calculate_tax(10000, "US-CA") == 725

    def test_unknown_jurisdiction(self):
        with pytest.raises(KeyError):
            calculate_tax(1000, "ZZ")

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            calculate_tax(-1, "DE")


class TestRoundingBoundaries:
    """These exercise the half-up rounding promised in the docstring."""

    def test_rounding_boundary_de_19(self):
        # 37 cents * 0.19 = 7.03 cents. Correct answer (half-up) = 7.
        # Current buggy implementation returns 7 here too — this test is a
        # guard that we don't regress the easy case.
        assert calculate_tax(37, "DE") == 7

    def test_rounding_halfup_us_ny_fails_on_truncate(self):
        # 125 cents * 0.08 = 10.0 exactly. Easy.
        assert calculate_tax(125, "US-NY") == 10

    def test_rounding_halfup_se_25_catches_bug(self):
        # 3 cents * 0.25 = 0.75. Half-up → 1. Current buggy int() → 0.
        # THIS IS THE FAILING TEST the bug_fixer agent should land on.
        assert calculate_tax(3, "SE") == 1

    def test_total_includes_tax(self):
        base = 1000
        assert total_with_tax(base, "DE") == base + calculate_tax(base, "DE")


def test_supported_jurisdictions_stable():
    assert supported_jurisdictions() == ["DE", "SE", "US-CA", "US-NY"]
