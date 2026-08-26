import sys
sys.path.insert(0, "/home/claude/fin-planning-platform")

from engine.withdrawal import AccountBalances, WithdrawalInputs, run_withdrawal_simulation
from engine.tax_brackets import FilingStatus

# Sanity check: proportional strategy should draw from all three buckets each year
# (not drain one before touching the next), so balances should shrink roughly together
balances_prop = AccountBalances(taxable_balance=300_000, taxable_cost_basis=200_000,
                                 tax_deferred_balance=300_000, roth_balance=300_000)
inputs_prop = WithdrawalInputs(
    balances=balances_prop, annual_return=0.05, years=5,
    annual_after_tax_spending=60_000, filing_status=FilingStatus.SINGLE, strategy="proportional"
)
result_prop = run_withdrawal_simulation(inputs_prop)
print("Proportional strategy, 5 years, $60k/yr target:")
for yr in result_prop.yearly_results:
    print(f"  Year {yr.year}: tax=${yr.total_tax_paid:.2f}, shortfall=${yr.shortfall:.2f}, ending=${yr.ending_balance:,.2f}")
assert not result_prop.depleted, "Should not deplete with $900k across buckets and $60k/yr spending"
assert all(yr.shortfall < 0.01 for yr in result_prop.yearly_results), "All years should fully meet target"
print("PASS: proportional strategy meets target across all years without depletion\n")

# Realistic comparison: same starting position, same spending need, compare total tax paid
# and years lasted under both strategies over a full retirement horizon
def make_balances():
    return AccountBalances(taxable_balance=400_000, taxable_cost_basis=250_000,
                            tax_deferred_balance=500_000, roth_balance=200_000)

common_kwargs = dict(annual_return=0.05, years=30, annual_after_tax_spending=70_000,
                      filing_status=FilingStatus.SINGLE, spending_growth=0.02)

result_taxable_first = run_withdrawal_simulation(
    WithdrawalInputs(balances=make_balances(), strategy="taxable_first", **common_kwargs)
)
result_proportional = run_withdrawal_simulation(
    WithdrawalInputs(balances=make_balances(), strategy="proportional", **common_kwargs)
)

print("30-year comparison, $1.1M starting across 3 buckets, $70k/yr (2% inflation-adjusted):")
print(f"  Taxable-first:  years lasted={result_taxable_first.years_lasted}, "
      f"depleted={result_taxable_first.depleted}, total tax=${result_taxable_first.total_tax_paid:,.2f}")
print(f"  Proportional:   years lasted={result_proportional.years_lasted}, "
      f"depleted={result_proportional.depleted}, total tax=${result_proportional.total_tax_paid:,.2f}")

# Both strategies should be internally consistent: tax paid should be non-negative,
# and years_lasted should never exceed the horizon
assert result_taxable_first.total_tax_paid >= 0
assert result_proportional.total_tax_paid >= 0
assert result_taxable_first.years_lasted <= 30
assert result_proportional.years_lasted <= 30
print("\nPASS: both strategies produce internally consistent results")
