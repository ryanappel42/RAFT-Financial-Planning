import sys
sys.path.insert(0, "/home/claude/fin-planning-platform")

from engine.rebalancing import Account, RebalanceInputs, run_rebalancing
from engine.tax_brackets import FilingStatus

# Case 1: single tax-deferred account, fully rebalanceable with zero tax
acct1 = Account(account_type="tax_deferred", holdings={"us_stocks": 70_000, "bonds": 30_000})
inputs1 = RebalanceInputs(
    accounts=[acct1],
    target_allocation={"us_stocks": 0.6, "bonds": 0.4},
    filing_status=FilingStatus.SINGLE,
)
result1 = run_rebalancing(inputs1)
print("Case 1: tax-deferred only, $100k, drifted 70/30 vs 60/40 target")
print(f"  Trades: {[(t.account_type, t.asset_class, t.action, round(t.amount,2)) for t in result1.trades]}")
print(f"  Total capital gains tax: ${result1.total_capital_gains_tax:.2f}")
print(f"  Post-rebalance drift: {result1.post_rebalance_drift}")
assert abs(result1.total_capital_gains_tax - 0.0) < 0.01, "Tax-deferred trades should never incur tax"
assert abs(result1.post_rebalance_drift["us_stocks"]) < 0.01
assert abs(result1.post_rebalance_drift["bonds"]) < 0.01
print("PASS: tax-deferred-only rebalance fully resolves drift, zero tax\n")

# Case 2: taxable-only account with a real gain, tax should compute correctly
# 20k gain being realized, stacked on $60k of other income (already above the 15% capital
# gains threshold), so the entire gain should be taxed at a flat 15%
acct2 = Account(
    account_type="taxable",
    holdings={"us_stocks": 70_000, "bonds": 30_000},
    cost_basis={"us_stocks": 50_000, "bonds": 30_000},  # $20k unrealized gain in us_stocks
)
inputs2 = RebalanceInputs(
    accounts=[acct2],
    target_allocation={"us_stocks": 0.6, "bonds": 0.4},
    filing_status=FilingStatus.SINGLE,
    other_taxable_income=60_000,
)
result2 = run_rebalancing(inputs2)
# Sell $10,000 of us_stocks (the drift amount), gain fraction = 20000/70000 = 0.285714
# gain realized = 10000 * 0.285714 = 2857.14, taxed at flat 15% since stacked income is
# already above the $49,450 threshold: tax = 2857.14 * 0.15 = 428.57
print("Case 2: taxable only, $20k unrealized gain, stacked on $60k other income")
print(f"  Total capital gains tax: ${result2.total_capital_gains_tax:.2f} (expect ~$428.57)")
assert abs(result2.total_capital_gains_tax - 428.57) < 1.0, f"Got {result2.total_capital_gains_tax}"
print("PASS: taxable rebalance tax matches hand calculation\n")

# Case 3: two accounts, tax-deferred holds only the underweight asset (can't help),
# so taxable has to absorb the entire rebalance and its tax cost
acct_td = Account(account_type="tax_deferred", holdings={"bonds": 20_000})
acct_tax = Account(
    account_type="taxable",
    holdings={"us_stocks": 80_000},
    cost_basis={"us_stocks": 60_000},  # $20k unrealized gain
)
inputs3 = RebalanceInputs(
    accounts=[acct_td, acct_tax],
    target_allocation={"us_stocks": 0.6, "bonds": 0.4},
    filing_status=FilingStatus.SINGLE,
    other_taxable_income=60_000,
)
result3 = run_rebalancing(inputs3)
# Total $100k, target us=60k/bonds=40k, current us=80k/bonds=20k -> drift us=+20k, bonds=-20k
# tax_deferred holds only bonds (underweight, nothing to sell), so it contributes nothing.
# taxable must sell $20k of us_stocks: gain fraction = 20000/80000 = 0.25, gain = 20000*0.25 = 5000
# stacked on $60k other income (already above 15% threshold): tax = 5000 * 0.15 = 750.00
print("Case 3: tax-deferred holds only the underweight asset, taxable absorbs full rebalance")
print(f"  Trades: {[(t.account_type, t.asset_class, t.action, round(t.amount,2)) for t in result3.trades]}")
print(f"  Total capital gains tax: ${result3.total_capital_gains_tax:.2f} (expect $750.00)")
assert abs(result3.total_capital_gains_tax - 750.00) < 0.5, f"Got {result3.total_capital_gains_tax}"
assert abs(result3.post_rebalance_drift["us_stocks"]) < 0.01
assert abs(result3.post_rebalance_drift["bonds"]) < 0.01
# Confirm tax_deferred account generated no trades, since it had nothing overweight to sell
td_trades = [t for t in result3.trades if t.account_type == "tax_deferred"]
assert len(td_trades) == 0, "Tax-deferred account should have no trades when it holds no overweight assets"
print("PASS: tax-deferred correctly contributes nothing when it can't help; taxable absorbs full cost\n")

# Case 4: both accounts hold the overweight asset, tax-deferred alone is enough to cover
# the entire drift, so tax-aware ordering should mean ZERO tax is paid even though the
# taxable account also holds an unrealized gain that a naive approach might have touched
acct_td4 = Account(account_type="tax_deferred", holdings={"us_stocks": 50_000, "bonds": 10_000})
acct_tax4 = Account(
    account_type="taxable",
    holdings={"us_stocks": 30_000, "bonds": 10_000},
    cost_basis={"us_stocks": 20_000, "bonds": 10_000},  # $10k unrealized gain in us_stocks
)
inputs4 = RebalanceInputs(
    accounts=[acct_td4, acct_tax4],
    target_allocation={"us_stocks": 0.6, "bonds": 0.4},
    filing_status=FilingStatus.SINGLE,
)
result4 = run_rebalancing(inputs4)
print("Case 4: both accounts hold overweight asset, tax-deferred alone covers the drift")
print(f"  Trades: {[(t.account_type, t.asset_class, t.action, round(t.amount,2)) for t in result4.trades]}")
print(f"  Total capital gains tax: ${result4.total_capital_gains_tax:.2f} (expect $0.00)")
tax_trades4 = [t for t in result4.trades if t.account_type == "taxable"]
assert abs(result4.total_capital_gains_tax - 0.0) < 0.01, "Tax-deferred should fully absorb this drift, zero tax"
assert len(tax_trades4) == 0, "Taxable account should be untouched when tax-deferred alone suffices"
assert abs(result4.post_rebalance_drift["us_stocks"]) < 0.01
assert abs(result4.post_rebalance_drift["bonds"]) < 0.01
print("PASS: tax-aware ordering avoids realizing an unnecessary taxable gain entirely\n")

print("All rebalancing engine checks passed.")
