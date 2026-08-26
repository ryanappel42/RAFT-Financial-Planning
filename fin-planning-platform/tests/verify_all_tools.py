import sys
sys.path.insert(0, "/home/claude/fin-planning-platform")

from api.client import execute_tool_call

# Tool 1: retirement Monte Carlo (already verified before, quick smoke test here)
result1 = execute_tool_call("run_retirement_monte_carlo", {
    "starting_balance": 150_000, "annual_contribution": 15_000, "years": 25,
    "expected_return": 0.07, "volatility": 0.14, "contribution_growth": 0.03,
    "target_balance": 1_500_000,
})
print("Tool 1 (retirement Monte Carlo):", result1)
assert "median_balance" in result1 and "probability_of_success" in result1
print("PASS\n")

# Tool 2: withdrawal sequencing, using enum string as the API would actually send it
result2 = execute_tool_call("run_withdrawal_sequencing", {
    "taxable_balance": 400_000, "taxable_cost_basis": 250_000,
    "tax_deferred_balance": 500_000, "roth_balance": 200_000,
    "annual_return": 0.05, "years": 30, "annual_after_tax_spending": 70_000,
    "filing_status": "single", "spending_growth": 0.02, "strategy": "taxable_first",
})
print("Tool 2 (withdrawal sequencing):", result2)
assert "years_lasted" in result2 and "total_tax_paid" in result2
assert result2["years_lasted"] <= 30
print("PASS\n")

# Tool 3: portfolio rebalancing, list-of-dicts as the API would send accounts
result3 = execute_tool_call("run_portfolio_rebalancing", {
    "accounts": [
        {"account_type": "tax_deferred", "holdings": {"us_stocks": 50_000, "bonds": 10_000}},
        {"account_type": "taxable", "holdings": {"us_stocks": 30_000, "bonds": 10_000},
         "cost_basis": {"us_stocks": 20_000, "bonds": 10_000}},
    ],
    "target_allocation": {"us_stocks": 0.6, "bonds": 0.4},
    "filing_status": "single",
})
print("Tool 3 (portfolio rebalancing):", result3)
assert "trades" in result3 and "total_capital_gains_tax" in result3
# This matches Case 4 from verify_rebalancing.py: tax-deferred alone should cover the drift, zero tax
assert abs(result3["total_capital_gains_tax"] - 0.0) < 0.01
print("PASS: matches expected zero-tax outcome from the tax-aware ordering\n")

# Confirm an unknown tool name still raises cleanly
try:
    execute_tool_call("not_a_real_tool", {})
    print("FAIL: should have raised")
except ValueError as e:
    print(f"PASS: unknown tool raises cleanly: {e}")

print("\nAll three tool execution paths verified.")
