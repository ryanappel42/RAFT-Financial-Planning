import sys
sys.path.insert(0, "/home/claude/fin-planning-platform")

from engine.tax_brackets import (
    ordinary_income_tax, capital_gains_tax, effective_rate, FilingStatus,
    STANDARD_DEDUCTION_2026
)

# Case 1: Single filer, $70,000 gross income
# Standard deduction: $16,100 -> taxable income = $53,900
# Bracket math:
#   10% on first $12,400 = $1,240.00
#   12% on ($50,400-$12,400)=$38,000 = $4,560.00
#   22% on ($53,900-$50,400)=$3,500 = $770.00
# Total = 1240 + 4560 + 770 = $6,570.00
tax = ordinary_income_tax(70_000, FilingStatus.SINGLE)
print(f"Single, $70k gross -> tax owed: ${tax:,.2f}")
expected = 6570.00
assert abs(tax - expected) < 0.01, f"Mismatch: got {tax}, expected {expected}"
print("PASS: single filer $70k matches hand calculation")

# Case 2: Married filing jointly, $150,000 gross income
# Standard deduction: $32,200 -> taxable income = $117,800
# Bracket math:
#   10% on first $24,800 = $2,480.00
#   12% on ($100,800-$24,800)=$76,000 = $9,120.00
#   22% on ($117,800-$100,800)=$17,000 = $3,740.00
# Total = 2480 + 9120 + 3740 = $15,340.00
tax_mfj = ordinary_income_tax(150_000, FilingStatus.MARRIED_FILING_JOINTLY)
print(f"\nMFJ, $150k gross -> tax owed: ${tax_mfj:,.2f}")
expected_mfj = 15340.00
assert abs(tax_mfj - expected_mfj) < 0.01, f"Mismatch: got {tax_mfj}, expected {expected_mfj}"
print("PASS: MFJ $150k matches hand calculation")

# Case 3: Income below standard deduction should owe zero
tax_zero = ordinary_income_tax(10_000, FilingStatus.SINGLE)
print(f"\nSingle, $10k gross (below std deduction) -> tax owed: ${tax_zero:,.2f}")
assert tax_zero == 0.0
print("PASS: below-deduction income owes zero tax")

# Case 4: Capital gains, single filer, $30,000 in other taxable income, $20,000 gain
# 0% bracket covers up to $49,450 of total taxable income
# Other income: $30,000 (already in 0% bracket)
# Total after gain: $50,000 -> crosses into 15% bracket at $49,450
# Gain taxed: $19,450 at 0% (30000 to 49450) + $550 at 15% (49450 to 50000)
# = 0 + 82.50 = $82.50
cg_tax = capital_gains_tax(gain_amount=20_000, other_taxable_income=30_000, filing_status=FilingStatus.SINGLE)
print(f"\nCapital gains tax (stacked on $30k other income, $20k gain): ${cg_tax:,.2f}")
expected_cg = 82.50
assert abs(cg_tax - expected_cg) < 0.01, f"Mismatch: got {cg_tax}, expected {expected_cg}"
print("PASS: capital gains stacking matches hand calculation")

# Case 5: Effective rate sanity check
eff = effective_rate(tax, 70_000)
print(f"\nEffective rate on $70k single: {eff:.4f} ({eff*100:.2f}%)")
assert 0.0 < eff < 0.22  # should be below top marginal bracket hit
print("PASS: effective rate is below marginal rate, as expected for a progressive system")

# Case 6: boundary test - exactly at a bracket edge
# Single filer, taxable income exactly at $50,400 (top of 12% bracket)
# Gross = 50400 + 16100 = 66500
tax_boundary = ordinary_income_tax(66_500, FilingStatus.SINGLE)
# 10% on 12400 = 1240, 12% on (50400-12400)=38000 = 4560, total = 5800
expected_boundary = 5800.00
print(f"\nBoundary case (taxable income = top of 12% bracket): ${tax_boundary:,.2f}")
assert abs(tax_boundary - expected_boundary) < 0.01, f"Mismatch: got {tax_boundary}, expected {expected_boundary}"
print("PASS: bracket boundary case matches")
