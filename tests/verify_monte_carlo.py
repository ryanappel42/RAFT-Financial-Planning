import sys
sys.path.insert(0, "/home/claude/fin-planning-platform")

import numpy as np
from engine.growth import GrowthInputs, project_growth
from engine.monte_carlo import MonteCarloInputs, run_monte_carlo

# Sanity check 1: zero volatility should collapse Monte Carlo onto the deterministic path
det_inputs = GrowthInputs(
    starting_balance=100_000, annual_contribution=10_000,
    annual_return=0.07, years=20, contribution_growth=0.03
)
det_result = project_growth(det_inputs)

mc_inputs = MonteCarloInputs(
    starting_balance=100_000, annual_contribution=10_000,
    years=20, expected_return=0.07, volatility=0.0,
    contribution_growth=0.03, num_trials=500, random_seed=42
)
mc_result = run_monte_carlo(mc_inputs)

print("Deterministic final balance:", round(det_result.final_balance, 2))
print("Monte Carlo (0% vol) median balance:", round(mc_result.median_balance, 2))
assert abs(mc_result.median_balance - det_result.final_balance) < 0.01, "Zero-vol MC should match deterministic"
assert np.allclose(mc_result.final_balances, det_result.final_balance, atol=0.01), "All trials should be identical at 0% vol"
print("PASS: zero-volatility Monte Carlo matches deterministic engine exactly")

# Sanity check 2: with real volatility, trials should differ and spread should be sensible
mc_inputs_real = MonteCarloInputs(
    starting_balance=100_000, annual_contribution=10_000,
    years=20, expected_return=0.07, volatility=0.15,
    contribution_growth=0.03, target_balance=500_000,
    num_trials=10_000, random_seed=42
)
mc_result_real = run_monte_carlo(mc_inputs_real)

print(f"\nWith 15% volatility over 10,000 trials:")
print(f"  10th percentile: {round(mc_result_real.percentile_10, 2)}")
print(f"  Median: {round(mc_result_real.median_balance, 2)}")
print(f"  90th percentile: {round(mc_result_real.percentile_90, 2)}")
print(f"  P(final >= $500,000): {mc_result_real.probability_of_success}")

assert mc_result_real.percentile_10 < mc_result_real.median_balance < mc_result_real.percentile_90, \
    "Percentiles should be ordered correctly"
assert 0.0 <= mc_result_real.probability_of_success <= 1.0
print("PASS: percentile ordering and probability bounds are sane")

# Sanity check 3: median with volatility should be roughly in the neighborhood of the deterministic
# result (not exact, since compounding random returns is not the same as compounding the mean,
# but it shouldn't be wildly off either)
pct_diff = abs(mc_result_real.median_balance - det_result.final_balance) / det_result.final_balance
print(f"\nDeterministic vs volatile-median % difference: {round(pct_diff * 100, 1)}%")
assert pct_diff < 0.5, "Median with volatility should still be in a reasonable range of deterministic result"
print("PASS: volatile median is in a reasonable range of the deterministic anchor")
