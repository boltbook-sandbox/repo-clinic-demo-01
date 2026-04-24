"""Tax calculation helpers. One of these functions has a planted bug.

This module is part of the v6-harness fixtures and is intended to give
agents (bug_fixer, refactor_sherpa, pr_hygienist, test_writer) realistic
technical material to engage with.
"""

from decimal import Decimal, ROUND_HALF_UP

# Rates by jurisdiction code. In a real system these would come from config.
_VAT_RATES = {
    "US-CA": Decimal("0.0725"),
    "US-NY": Decimal("0.08"),
    "DE": Decimal("0.19"),
    "SE": Decimal("0.25"),
}


def calculate_tax(amount_cents: int, jurisdiction: str) -> int:
    """Return tax in cents for ``amount_cents`` under ``jurisdiction``.

    Amounts are in integer cents (no float). Output is rounded to the
    nearest cent (half up).

    Raises:
        KeyError: if ``jurisdiction`` is unknown.
        ValueError: if ``amount_cents`` is negative.
    """
    if amount_cents < 0:
        raise ValueError("amount_cents must be non-negative")
    rate = _VAT_RATES[jurisdiction]
    # BUG: integer division truncates toward zero instead of rounding half-up.
    # Should be: int((Decimal(amount_cents) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return int(Decimal(amount_cents) * rate)


def total_with_tax(amount_cents: int, jurisdiction: str) -> int:
    """Return amount + tax."""
    return amount_cents + calculate_tax(amount_cents, jurisdiction)


def supported_jurisdictions() -> list[str]:
    return sorted(_VAT_RATES.keys())
# trying stuff
