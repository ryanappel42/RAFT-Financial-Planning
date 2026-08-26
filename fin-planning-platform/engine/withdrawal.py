"""
Withdrawal sequencing engine.

Models retirement drawdown across three account types (taxable, tax-deferred,
Roth), solving for the gross withdrawal from each bucket needed to hit a
fixed after-tax spending target, under two sequencing strategies.
"""

from dataclasses import dataclass, field
from engine.tax_brackets import ordinary_income_tax, capital_gains_tax, FilingStatus


@dataclass
class AccountBalances:
    taxable_balance: float
    taxable_cost_basis: float   # amount of taxable_balance that is principal, not gains
    tax_deferred_balance: float
    roth_balance: float

    def total(self) -> float:
        return self.taxable_balance + self.tax_deferred_balance + self.roth_balance


@dataclass
class WithdrawalInputs:
    balances: AccountBalances
    annual_return: float              # r: deterministic annual return applied to all buckets
    years: int                        # planning horizon
    annual_after_tax_spending: float  # target net spending in year 1
    filing_status: FilingStatus
    spending_growth: float = 0.0      # inflation adjustment to spending target each year
    strategy: str = "taxable_first"   # "taxable_first" or "proportional"


@dataclass
class YearResult:
    year: int
    spending_target: float
    total_tax_paid: float
    shortfall: float          # > 0 if target couldn't be fully met (portfolio depleted)
    ending_balance: float


@dataclass
class WithdrawalResult:
    years_lasted: int             # years before depletion, or full horizon if never depleted
    depleted: bool
    total_tax_paid: float
    yearly_results: list[YearResult] = field(default_factory=list)


def _solve_gross_for_net(net_target: float, tax_func, max_iterations: int = 100) -> float:
    """
    Bisection search for the gross withdrawal amount whose after-tax net
    equals net_target, given tax_func(gross) -> tax owed. Relies on
    net(gross) = gross - tax_func(gross) being monotonically non-decreasing,
    which holds for progressive tax with marginal rates below 100%.
    """
    if net_target <= 0:
        return 0.0

    def net_of(gross):
        return gross - tax_func(gross)

    lo, hi = 0.0, max(net_target * 2, net_target + 1_000)
    expansions = 0
    while net_of(hi) < net_target and expansions < 50:
        hi *= 2
        expansions += 1

    for _ in range(max_iterations):
        mid = (lo + hi) / 2
        if net_of(mid) < net_target:
            lo = mid
        else:
            hi = mid
    return hi


def _gain_fraction(balances: AccountBalances) -> float:
    if balances.taxable_balance <= 0:
        return 0.0
    return max(0.0, (balances.taxable_balance - balances.taxable_cost_basis) / balances.taxable_balance)


def _withdraw_taxable(balances: AccountBalances, net_remaining: float,
                       ordinary_income_so_far: float, filing_status: FilingStatus):
    avail = balances.taxable_balance
    if avail <= 0 or net_remaining <= 0:
        return 0.0, 0.0

    gain_fraction = _gain_fraction(balances)

    def tax_func(w):
        gain = w * gain_fraction
        return capital_gains_tax(gain, ordinary_income_so_far, filing_status)

    gross_needed = _solve_gross_for_net(net_remaining, tax_func)
    gross = min(avail, gross_needed)
    tax = tax_func(gross)

    if balances.taxable_balance > 0:
        balances.taxable_cost_basis *= max(0.0, 1 - gross / balances.taxable_balance)
    balances.taxable_balance -= gross

    return gross - tax, tax  # (net received, tax paid)


def _withdraw_tax_deferred(balances: AccountBalances, net_remaining: float,
                            ordinary_income_so_far: float, filing_status: FilingStatus):
    avail = balances.tax_deferred_balance
    if avail <= 0 or net_remaining <= 0:
        return 0.0, 0.0, 0.0  # (net received, tax paid, gross withdrawn)

    def tax_func(g):
        return (ordinary_income_tax(ordinary_income_so_far + g, filing_status)
                - ordinary_income_tax(ordinary_income_so_far, filing_status))

    gross_needed = _solve_gross_for_net(net_remaining, tax_func)
    gross = min(avail, gross_needed)
    tax = tax_func(gross)

    balances.tax_deferred_balance -= gross
    return gross - tax, tax, gross


def _withdraw_roth(balances: AccountBalances, net_remaining: float):
    avail = balances.roth_balance
    take = min(avail, max(0.0, net_remaining))
    balances.roth_balance -= take
    return take  # tax-free, net == gross


def _process_year_sequential(balances: AccountBalances, spending_target: float,
                              filing_status: FilingStatus, order: list[str]):
    net_remaining = spending_target
    ordinary_income_so_far = 0.0
    total_tax = 0.0

    for bucket in order:
        if net_remaining <= 1e-6:
            break
        if bucket == "roth":
            net_remaining -= _withdraw_roth(balances, net_remaining)
        elif bucket == "tax_deferred":
            net_received, tax, gross = _withdraw_tax_deferred(
                balances, net_remaining, ordinary_income_so_far, filing_status
            )
            ordinary_income_so_far += gross
            total_tax += tax
            net_remaining -= net_received
        elif bucket == "taxable":
            net_received, tax = _withdraw_taxable(
                balances, net_remaining, ordinary_income_so_far, filing_status
            )
            total_tax += tax
            net_remaining -= net_received

    shortfall = max(0.0, net_remaining)
    return total_tax, shortfall


def _process_year_proportional(balances: AccountBalances, spending_target: float,
                                filing_status: FilingStatus):
    total_balance = balances.total()
    if total_balance <= 0:
        return 0.0, spending_target

    weights = {
        "taxable": balances.taxable_balance / total_balance,
        "tax_deferred": balances.tax_deferred_balance / total_balance,
        "roth": balances.roth_balance / total_balance,
    }
    gain_fraction = _gain_fraction(balances)

    def total_net(k):
        td_gross = min(balances.tax_deferred_balance, k * weights["tax_deferred"])
        ordinary_tax = ordinary_income_tax(td_gross, filing_status)  # base is 0, only source of ordinary income

        tx_gross = min(balances.taxable_balance, k * weights["taxable"])
        gain = tx_gross * gain_fraction
        cg_tax = capital_gains_tax(gain, td_gross, filing_status)

        roth_gross = min(balances.roth_balance, k * weights["roth"])

        net = (td_gross - ordinary_tax) + (tx_gross - cg_tax) + roth_gross
        return net, td_gross, tx_gross, roth_gross, ordinary_tax + cg_tax

    lo, hi = 0.0, max(spending_target * 2, spending_target + 1_000)
    expansions = 0
    while total_net(hi)[0] < spending_target and expansions < 50:
        hi *= 2
        expansions += 1

    for _ in range(100):
        mid = (lo + hi) / 2
        if total_net(mid)[0] < spending_target:
            lo = mid
        else:
            hi = mid

    net_achieved, td_gross, tx_gross, roth_gross, total_tax = total_net(hi)

    if balances.taxable_balance > 0:
        balances.taxable_cost_basis *= max(0.0, 1 - tx_gross / balances.taxable_balance)
    balances.taxable_balance -= tx_gross
    balances.tax_deferred_balance -= td_gross
    balances.roth_balance -= roth_gross

    shortfall = max(0.0, spending_target - net_achieved)
    return total_tax, shortfall


def run_withdrawal_simulation(inputs: WithdrawalInputs) -> WithdrawalResult:
    balances = AccountBalances(
        taxable_balance=inputs.balances.taxable_balance,
        taxable_cost_basis=inputs.balances.taxable_cost_basis,
        tax_deferred_balance=inputs.balances.tax_deferred_balance,
        roth_balance=inputs.balances.roth_balance,
    )

    order = ["taxable", "tax_deferred", "roth"]  # used only for taxable_first strategy

    yearly_results = []
    total_tax_paid = 0.0
    depleted = False
    years_lasted = inputs.years

    for year in range(1, inputs.years + 1):
        spending_target = inputs.annual_after_tax_spending * (1 + inputs.spending_growth) ** (year - 1)

        if inputs.strategy == "taxable_first":
            tax_paid, shortfall = _process_year_sequential(balances, spending_target, inputs.filing_status, order)
        elif inputs.strategy == "proportional":
            tax_paid, shortfall = _process_year_proportional(balances, spending_target, inputs.filing_status)
        else:
            raise ValueError(f"Unknown strategy: {inputs.strategy}")

        total_tax_paid += tax_paid

        # Apply growth to what remains after withdrawal
        balances.taxable_balance *= (1 + inputs.annual_return)
        balances.tax_deferred_balance *= (1 + inputs.annual_return)
        balances.roth_balance *= (1 + inputs.annual_return)

        yearly_results.append(YearResult(
            year=year,
            spending_target=spending_target,
            total_tax_paid=tax_paid,
            shortfall=shortfall,
            ending_balance=balances.total(),
        ))

        if shortfall > 0.01 and not depleted:
            depleted = True
            years_lasted = year

    return WithdrawalResult(
        years_lasted=years_lasted,
        depleted=depleted,
        total_tax_paid=total_tax_paid,
        yearly_results=yearly_results,
    )
