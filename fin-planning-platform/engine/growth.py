"""
Deterministic compound growth projection.

Models portfolio growth assuming a fixed annual return, with contributions
made once per year that can themselves grow annually (e.g. raises, inflation
adjustment). This is the baseline projection before Monte Carlo introduces
return variability.
"""

from dataclasses import dataclass


@dataclass
class GrowthInputs:
    starting_balance: float          # P0: current portfolio value
    annual_contribution: float       # c1: contribution made in year 1
    annual_return: float             # r: expected nominal annual return, e.g. 0.07
    years: int                       # t: years until retirement
    contribution_growth: float = 0.0  # g: annual growth rate of contributions, e.g. 0.03


@dataclass
class GrowthResult:
    final_balance: float
    yearly_balances: list[float]  # balance at end of each year, index 0 = year 1


def project_growth(inputs: GrowthInputs) -> GrowthResult:
    """
    Year-by-year simulation:
        c_y = c1 * (1+g)^(y-1)
        P_y = P_{y-1} * (1+r) + c_y

    Contributions are modeled as end-of-year deposits and grow at rate g
    each year. Setting g=0 reduces to flat contributions.
    """
    p0 = inputs.starting_balance
    c1 = inputs.annual_contribution
    r = inputs.annual_return
    g = inputs.contribution_growth
    t = inputs.years

    if t < 0:
        raise ValueError("years must be non-negative")

    balance = p0
    yearly_balances = []
    for year in range(1, t + 1):
        contribution = c1 * (1 + g) ** (year - 1)
        balance = balance * (1 + r) + contribution
        yearly_balances.append(balance)

    final_balance = yearly_balances[-1] if yearly_balances else p0
    return GrowthResult(final_balance=final_balance, yearly_balances=yearly_balances)
