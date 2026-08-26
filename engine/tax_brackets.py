"""
Federal tax bracket module.

Holds 2026 federal ordinary income brackets, standard deductions, and
long-term capital gains brackets, and computes progressive tax owed.

IMPORTANT: This data is set by the IRS annually (inflation-adjusted) and
WILL need to be updated for future tax years. See NEEDS_UPDATE_BY below.
Source for 2026 figures: IRS Revenue Procedure 2025-32.
"""

from dataclasses import dataclass
from enum import Enum

TAX_YEAR = 2026
NEEDS_UPDATE_BY = "2027-01-01"  # IRS typically publishes next year's brackets in Oct/Nov

class FilingStatus(Enum):
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married_filing_jointly"
    HEAD_OF_HOUSEHOLD = "head_of_household"


# Each bracket: (upper bound of bracket, rate). Last bracket uses float('inf').
ORDINARY_INCOME_BRACKETS_2026 = {
    FilingStatus.SINGLE: [
        (12_400, 0.10), (50_400, 0.12), (105_700, 0.22), (201_775, 0.24),
        (256_225, 0.32), (640_600, 0.35), (float("inf"), 0.37),
    ],
    FilingStatus.MARRIED_FILING_JOINTLY: [
        (24_800, 0.10), (100_800, 0.12), (211_400, 0.22), (403_550, 0.24),
        (512_450, 0.32), (768_700, 0.35), (float("inf"), 0.37),
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (17_700, 0.10), (67_450, 0.12), (105_700, 0.22), (201_775, 0.24),
        (256_200, 0.32), (640_600, 0.35), (float("inf"), 0.37),
    ],
}

STANDARD_DEDUCTION_2026 = {
    FilingStatus.SINGLE: 16_100,
    FilingStatus.MARRIED_FILING_JOINTLY: 32_200,
    FilingStatus.HEAD_OF_HOUSEHOLD: 24_150,
}

# Long-term capital gains brackets: (upper bound of taxable income, rate)
CAPITAL_GAINS_BRACKETS_2026 = {
    FilingStatus.SINGLE: [(49_450, 0.0), (545_500, 0.15), (float("inf"), 0.20)],
    FilingStatus.MARRIED_FILING_JOINTLY: [(98_900, 0.0), (613_700, 0.15), (float("inf"), 0.20)],
    FilingStatus.HEAD_OF_HOUSEHOLD: [(66_200, 0.0), (579_600, 0.15), (float("inf"), 0.20)],
}


def _progressive_tax(taxable_income: float, brackets: list[tuple[float, float]]) -> float:
    """Applies a progressive bracket schedule to taxable_income and returns tax owed."""
    if taxable_income <= 0:
        return 0.0

    tax = 0.0
    lower_bound = 0.0
    for upper_bound, rate in brackets:
        if taxable_income <= lower_bound:
            break
        taxed_in_bracket = min(taxable_income, upper_bound) - lower_bound
        tax += taxed_in_bracket * rate
        lower_bound = upper_bound

    return tax


def ordinary_income_tax(gross_income: float, filing_status: FilingStatus) -> float:
    """
    Tax owed on ordinary income (e.g. tax-deferred 401k/IRA withdrawals),
    after subtracting the standard deduction. Assumes no other income
    or itemized deductions.
    """
    taxable_income = max(0.0, gross_income - STANDARD_DEDUCTION_2026[filing_status])
    return _progressive_tax(taxable_income, ORDINARY_INCOME_BRACKETS_2026[filing_status])


def capital_gains_tax(gain_amount: float, other_taxable_income: float, filing_status: FilingStatus) -> float:
    """
    Tax owed on long-term capital gains (e.g. taxable account withdrawals),
    stacked on top of other taxable income since capital gains brackets are
    based on total taxable income, not gains alone.
    """
    if gain_amount <= 0:
        return 0.0

    brackets = CAPITAL_GAINS_BRACKETS_2026[filing_status]
    total_income = other_taxable_income + gain_amount

    tax_on_total = _progressive_tax(total_income, brackets)
    tax_on_other = _progressive_tax(other_taxable_income, brackets)
    return tax_on_total - tax_on_other


def effective_rate(tax_owed: float, gross_income: float) -> float:
    """Returns effective tax rate, 0.0 if gross_income is 0."""
    if gross_income <= 0:
        return 0.0
    return tax_owed / gross_income
