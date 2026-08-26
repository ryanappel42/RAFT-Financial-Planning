"""
Monte Carlo retirement projection.

Simulates many possible portfolio paths by drawing a random annual return
each year (instead of assuming a fixed return), so we can report a
distribution of outcomes and a probability of hitting a target balance.
"""

from dataclasses import dataclass
import numpy as np


@dataclass
class MonteCarloInputs:
    starting_balance: float           # P0
    annual_contribution: float        # c1: contribution in year 1
    years: int                        # t: years until retirement
    expected_return: float            # mu: mean annual return, e.g. 0.07
    volatility: float                 # sigma: annual return std dev, e.g. 0.15
    contribution_growth: float = 0.0  # g: annual growth rate of contributions
    target_balance: float | None = None  # optional target to compute success probability
    num_trials: int = 10_000
    random_seed: int | None = None


@dataclass
class MonteCarloResult:
    final_balances: np.ndarray        # shape (num_trials,)
    median_balance: float
    percentile_10: float
    percentile_90: float
    probability_of_success: float | None  # None if no target_balance given


def run_monte_carlo(inputs: MonteCarloInputs) -> MonteCarloResult:
    rng = np.random.default_rng(inputs.random_seed)

    n = inputs.num_trials
    t = inputs.years

    if t < 0:
        raise ValueError("years must be non-negative")
    if inputs.volatility < 0:
        raise ValueError("volatility must be non-negative")

    if t == 0:
        final_balances = np.full(n, inputs.starting_balance)
    else:
        # returns[i, y] = simulated return for trial i, year y (0-indexed year)
        returns = rng.normal(loc=inputs.expected_return, scale=inputs.volatility, size=(n, t))

        # contributions[y] = contribution amount in year y (same across all trials)
        years_idx = np.arange(t)
        contributions = inputs.annual_contribution * (1 + inputs.contribution_growth) ** years_idx

        # Simulate year by year across all trials at once (vectorized over trials, looped over years
        # since each year's balance depends on the previous year's).
        balances = np.full(n, inputs.starting_balance, dtype=float)
        for y in range(t):
            balances = balances * (1 + returns[:, y]) + contributions[y]

        final_balances = balances

    probability_of_success = None
    if inputs.target_balance is not None:
        probability_of_success = float(np.mean(final_balances >= inputs.target_balance))

    return MonteCarloResult(
        final_balances=final_balances,
        median_balance=float(np.median(final_balances)),
        percentile_10=float(np.percentile(final_balances, 10)),
        percentile_90=float(np.percentile(final_balances, 90)),
        probability_of_success=probability_of_success,
    )
