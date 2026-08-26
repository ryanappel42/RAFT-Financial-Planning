import sys
sys.path.insert(0, "/home/claude/fin-planning-platform")

from engine.withdrawal import AccountBalances, WithdrawalInputs, run_withdrawal_simulation
from engine.tax_brackets import FilingStatus

# Case 1: Roth-only withdrawal, should be tax-free, net == gross exactly
balances1 = AccountBalances(taxable_balance=0, taxable_cost_basis=0, tax_deferred_balance=0, roth_balance=100_000)
inputs1 = WithdrawalInputs(
    balances=balances1, annual_return=0.0, years=3,
    annual_after_tax_spending=10_000, filing_status=FilingStatus.SINGLE, strategy="taxable_first"
)
result1 = run_withdrawal_simulation(inputs1)
print("Case 1: Roth-only, $10k/yr for 3 years")
print(f"  Total tax paid: ${result1.total_tax_paid:.2f}")
print(f"  Years lasted: {result1.years_lasted}, depleted: {result1.depleted}")
final_balance1 = result1.yearly_results[-1].ending_balance
print(f"  Ending balance: ${final_balance1:,.2f}")
assert abs(result1.total_tax_paid - 0.0) < 0.01, "Roth withdrawals should be tax-free"
assert abs(final_balance1 - 70_000) < 0.01, f"Expected $70,000 remaining, got {final_balance1}"
print("PASS: Roth-only case, no tax, correct balance drawdown\n")

# Case 2: Tax-deferred only, single filer, target net spending chosen to land in a known bracket
# Hand calc: gross=59000, taxable_income=59000-16100=42900
#   10% on 12400 = 1240, 12% on (42900-12400)=30500 = 3660, total tax = 4900
#   net = 59000 - 4900 = 54100
balances2 = AccountBalances(taxable_balance=0, taxable_cost_basis=0, tax_deferred_balance=200_000, roth_balance=0)
inputs2 = WithdrawalInputs(
    balances=balances2, annual_return=0.0, years=1,
    annual_after_tax_spending=54_100, filing_status=FilingStatus.SINGLE, strategy="taxable_first"
)
result2 = run_withdrawal_simulation(inputs2)
print("Case 2: Tax-deferred only, target net = $54,100")
print(f"  Total tax paid: ${result2.total_tax_paid:.2f}")
final_balance2 = result2.yearly_results[-1].ending_balance
print(f"  Ending balance: ${final_balance2:,.2f} (expect ~$141,000)")
assert abs(result2.total_tax_paid - 4_900.00) < 1.0, f"Expected ~$4,900 tax, got {result2.total_tax_paid}"
assert abs(final_balance2 - 141_000) < 1.0, f"Expected ~$141,000 remaining, got {final_balance2}"
assert result2.yearly_results[0].shortfall < 0.01, "Should fully meet target, no shortfall"
print("PASS: tax-deferred gross-up solve matches hand calculation\n")

# Case 3: Taxable-only, gain stays inside 0% capital gains bracket, so tax should be zero
# 20% gain fraction ($100k balance, $80k basis), target net $40,000 -> gain realized = $8,000, well under $49,450 0% threshold
balances3 = AccountBalances(taxable_balance=100_000, taxable_cost_basis=80_000, tax_deferred_balance=0, roth_balance=0)
inputs3 = WithdrawalInputs(
    balances=balances3, annual_return=0.0, years=1,
    annual_after_tax_spending=40_000, filing_status=FilingStatus.SINGLE, strategy="taxable_first"
)
result3 = run_withdrawal_simulation(inputs3)
print("Case 3: Taxable-only, gain within 0% capital gains bracket")
print(f"  Total tax paid: ${result3.total_tax_paid:.2f} (expect $0)")
final_balance3 = result3.yearly_results[-1].ending_balance
print(f"  Ending balance: ${final_balance3:,.2f} (expect $60,000)")
assert abs(result3.total_tax_paid - 0.0) < 0.01, "Gain should fall entirely in 0% bracket"
assert abs(final_balance3 - 60_000) < 0.01, f"Expected $60,000 remaining, got {final_balance3}"
print("PASS: taxable withdrawal in 0% bracket correctly untaxed\n")

# Case 4: depletion scenario, small balances forcing a shortfall partway through
balances4 = AccountBalances(taxable_balance=5_000, taxable_cost_basis=5_000, tax_deferred_balance=5_000, roth_balance=5_000)
inputs4 = WithdrawalInputs(
    balances=balances4, annual_return=0.0, years=3,
    annual_after_tax_spending=10_000, filing_status=FilingStatus.SINGLE, strategy="taxable_first"
)
result4 = run_withdrawal_simulation(inputs4)
print("Case 4: depletion scenario, $15k total across 3 buckets, $10k/yr target")
print(f"  Years lasted: {result4.years_lasted}, depleted: {result4.depleted}")
for yr in result4.yearly_results:
    print(f"    Year {yr.year}: target=${yr.spending_target:.2f}, shortfall=${yr.shortfall:.2f}, ending=${yr.ending_balance:.2f}")
assert result4.depleted, "Portfolio should deplete given insufficient balance"
assert result4.years_lasted == 2, f"Expected depletion flagged at year 2, got {result4.years_lasted}"
assert result4.yearly_results[0].shortfall < 0.01, "Year 1 should fully meet target (taxable + tax-deferred cover it)"
assert result4.yearly_results[1].shortfall > 4_000, "Year 2 should show a shortfall since only Roth remains"
print("PASS: depletion correctly detected at year 2 with expected shortfall\n")

print("All withdrawal engine checks passed.")
