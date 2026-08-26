import sys
sys.path.insert(0, "/home/claude/fin-planning-platform")

from api.client import execute_tool_call

# Simulate what Claude would send as tool_input after parsing a user's message
tool_input = {
    "starting_balance": 150_000,
    "annual_contribution": 15_000,
    "years": 25,
    "expected_return": 0.07,
    "volatility": 0.14,
    "contribution_growth": 0.03,
    "target_balance": 1_500_000,
}

result = execute_tool_call("run_retirement_monte_carlo", tool_input)
print("Tool execution result:")
for k, v in result.items():
    print(f"  {k}: {v}")

assert "median_balance" in result
assert "probability_of_success" in result
assert 0.0 <= result["probability_of_success"] <= 1.0
assert result["percentile_10"] < result["median_balance"] < result["percentile_90"]
print("\nPASS: tool execution wrapper returns well-formed, sane results")

# Also confirm unknown tool names raise, so silent failures aren't possible
try:
    execute_tool_call("not_a_real_tool", {})
    print("FAIL: should have raised on unknown tool")
except ValueError as e:
    print(f"PASS: unknown tool correctly raises: {e}")
