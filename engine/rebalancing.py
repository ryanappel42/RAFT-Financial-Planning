"""
Portfolio drift and tax-aware rebalancing engine.

Compares current allocation across asset classes (aggregated across
accounts) to a target allocation, then generates the specific trades needed
to rebalance, preferring trades inside tax-deferred/Roth accounts (which
have no tax consequence) before selling appreciated taxable positions.
"""

from dataclasses import dataclass, field
from engine.tax_brackets import capital_gains_tax, FilingStatus


@dataclass
class Account:
    account_type: str  # "tax_deferred", "roth", or "taxable"
    holdings: dict = field(default_factory=dict)     # asset_class -> dollar value
    cost_basis: dict = field(default_factory=dict)   # asset_class -> cost basis (taxable only)

    def total(self) -> float:
        return sum(self.holdings.values())


@dataclass
class RebalanceInputs:
    accounts: list  # list[Account]
    target_allocation: dict  # asset_class -> target fraction, should sum to 1.0
    filing_status: FilingStatus
    other_taxable_income: float = 0.0  # for stacking capital gains tax correctly


@dataclass
class Trade:
    account_index: int
    account_type: str
    asset_class: str
    action: str  # "sell" or "buy"
    amount: float


@dataclass
class RebalanceResult:
    trades: list  # list[Trade]
    total_capital_gains_tax: float
    total_portfolio_value: float
    pre_rebalance_drift: dict   # asset_class -> dollars over/under target (+ = overweight)
    post_rebalance_drift: dict  # same, after trades


# Process accounts in this order: no-tax-consequence accounts first, taxable last,
# so as much rebalancing as possible happens without realizing capital gains.
ACCOUNT_PROCESSING_ORDER = ["tax_deferred", "roth", "taxable"]


def _compute_drift(accounts, target_allocation):
    total_value = sum(acct.total() for acct in accounts)
    current_dollars = {}
    for acct in accounts:
        for asset, value in acct.holdings.items():
            current_dollars[asset] = current_dollars.get(asset, 0.0) + value

    drift = {}
    for asset, target_pct in target_allocation.items():
        target_dollars = target_pct * total_value
        drift[asset] = current_dollars.get(asset, 0.0) - target_dollars

    return total_value, drift


def run_rebalancing(inputs: RebalanceInputs) -> RebalanceResult:
    # Work on copies so the caller's account objects aren't mutated
    accounts = [
        Account(
            account_type=acct.account_type,
            holdings=dict(acct.holdings),
            cost_basis=dict(acct.cost_basis),
        )
        for acct in inputs.accounts
    ]

    total_value, drift = _compute_drift(accounts, inputs.target_allocation)
    pre_rebalance_drift = dict(drift)

    trades = []
    total_tax = 0.0

    indexed_accounts = list(enumerate(accounts))
    ordered = sorted(
        indexed_accounts,
        key=lambda pair: ACCOUNT_PROCESSING_ORDER.index(pair[1].account_type)
    )

    for idx, acct in ordered:
        cash_raised = 0.0

        # Step 1: sell overweight assets held in this account
        for asset, drift_amount in list(drift.items()):
            if drift_amount <= 0:
                continue
            held = acct.holdings.get(asset, 0.0)
            if held <= 0:
                continue

            sell_amount = min(held, drift_amount)
            if sell_amount <= 0:
                continue

            if acct.account_type == "taxable":
                basis = acct.cost_basis.get(asset, held)  # assume full basis if untracked
                gain_fraction = max(0.0, (held - basis) / held) if held > 0 else 0.0
                gain_realized = sell_amount * gain_fraction
                tax = capital_gains_tax(gain_realized, inputs.other_taxable_income, inputs.filing_status)
                total_tax += tax
                # reduce basis proportionally to the portion sold
                acct.cost_basis[asset] = basis * max(0.0, 1 - sell_amount / held)

            acct.holdings[asset] = held - sell_amount
            drift[asset] -= sell_amount
            cash_raised += sell_amount
            trades.append(Trade(idx, acct.account_type, asset, "sell", sell_amount))

        # Step 2: use cash raised in this account to buy underweight assets, same account
        if cash_raised > 0:
            underweight = {a: -d for a, d in drift.items() if d < 0}
            total_need = sum(underweight.values())
            if total_need > 0:
                for asset, need in underweight.items():
                    if cash_raised <= 0:
                        break
                    buy_amount = min(need, cash_raised * (need / total_need))
                    if buy_amount <= 0:
                        continue
                    acct.holdings[asset] = acct.holdings.get(asset, 0.0) + buy_amount
                    drift[asset] += buy_amount
                    trades.append(Trade(idx, acct.account_type, asset, "buy", buy_amount))

    return RebalanceResult(
        trades=trades,
        total_capital_gains_tax=total_tax,
        total_portfolio_value=total_value,
        pre_rebalance_drift=pre_rebalance_drift,
        post_rebalance_drift=drift,
    )
