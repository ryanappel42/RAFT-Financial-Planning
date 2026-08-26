import sys
sys.path.insert(0, "/home/claude/fin-planning-platform")

from engine.growth import GrowthInputs, project_growth

# Case 1: flat contributions (g=0), same numbers as before, should still match
inputs = GrowthInputs(starting_balance=100_000, annual_contribution=10_000, annual_return=0.07, years=3)
result = project_growth(inputs)
print("Flat contribution yearly balances:", [round(b, 2) for b in result.yearly_balances])
expected_year3 = 154653.30
assert abs(result.final_balance - expected_year3) < 0.01, f"Mismatch: got {result.final_balance}"
print("PASS: flat-contribution case still matches")

# Case 2: growing contributions, hand-calculated
# P0=100,000, c1=10,000, r=7%, g=3%, t=3
# Year 1: c=10000.00 -> balance = 100000*1.07 + 10000.00 = 117000.00
# Year 2: c=10300.00 -> balance = 117000.00*1.07 + 10300.00 = 125190.00 + 10300.00 = 135490.00
# Year 3: c=10609.00 -> balance = 135490.00*1.07 + 10609.00 = 144974.30 + 10609.00 = 155583.30
growing_inputs = GrowthInputs(
    starting_balance=100_000, annual_contribution=10_000,
    annual_return=0.07, years=3, contribution_growth=0.03
)
growing_result = project_growth(growing_inputs)
print("\nGrowing contribution yearly balances:", [round(b, 2) for b in growing_result.yearly_balances])
expected = 155583.30
assert abs(growing_result.final_balance - expected) < 0.01, f"Mismatch: got {growing_result.final_balance}, expected {expected}"
print("PASS: growing-contribution case matches hand calculation")

# Sanity: growing contributions should produce a higher final balance than flat, all else equal
assert growing_result.final_balance > result.final_balance
print("PASS: growing contributions yield higher balance than flat, as expected")
