"""
Tool schema definitions for the retirement planning engine.

These describe the calculation functions to Claude in the format the
Anthropic API expects for tool use. Only user-facing inputs are exposed;
internal parameters (trial count, random seed) are fixed by our own code
so results stay consistent and Claude can't under-simulate.
"""

RETIREMENT_MONTE_CARLO_TOOL = {
    "name": "run_retirement_monte_carlo",
    "description": (
        "Runs a Monte Carlo simulation of retirement portfolio growth, drawing a "
        "random annual return each year (based on expected return and volatility) "
        "across thousands of trials. Returns a distribution of outcomes (10th "
        "percentile, median, 90th percentile) and, if a target balance is given, "
        "the probability of reaching that target. Use this whenever the user asks "
        "about retirement readiness, whether they're on track, or 'can I retire by X age' "
        "style questions. Do not estimate these numbers yourself, always call this tool."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "starting_balance": {
                "type": "number",
                "description": "Current total portfolio/retirement savings balance in dollars."
            },
            "annual_contribution": {
                "type": "number",
                "description": "Amount contributed to retirement savings in the first year, in dollars."
            },
            "years": {
                "type": "integer",
                "description": "Number of years until the target retirement date."
            },
            "expected_return": {
                "type": "number",
                "description": (
                    "Expected average annual investment return, as a decimal "
                    "(e.g. 0.07 for 7%). Use 0.07 as a reasonable default for a "
                    "diversified stock/bond portfolio if the user has no strong "
                    "view, but prefer asking if risk tolerance/allocation is unclear."
                )
            },
            "volatility": {
                "type": "number",
                "description": (
                    "Expected annual volatility (standard deviation of returns), as a "
                    "decimal (e.g. 0.15 for 15%, typical of a stock-heavy portfolio; "
                    "0.08-0.10 is more typical of a conservative/bond-heavy portfolio)."
                )
            },
            "contribution_growth": {
                "type": "number",
                "description": (
                    "Expected annual growth rate of contributions, as a decimal "
                    "(e.g. 0.03 for 3% to reflect raises). Default to 0.0 if the "
                    "user expects flat contributions."
                )
            },
            "target_balance": {
                "type": "number",
                "description": (
                    "Optional target retirement balance in dollars. If provided, "
                    "the tool also returns the probability of reaching this target."
                )
            }
        },
        "required": [
            "starting_balance", "annual_contribution", "years",
            "expected_return", "volatility"
        ]
    }
}


WITHDRAWAL_SEQUENCING_TOOL = {
    "name": "run_withdrawal_sequencing",
    "description": (
        "Simulates retirement drawdown across taxable, tax-deferred, and Roth "
        "accounts, solving for the gross withdrawal from each account needed to "
        "hit a fixed after-tax spending target each year, with real federal tax "
        "calculated on tax-deferred (ordinary income) and taxable (capital gains) "
        "withdrawals. Returns how many years the portfolio lasts, total tax paid, "
        "and whether/when it depletes, under a chosen withdrawal sequencing "
        "strategy. Use this whenever the user asks how long their retirement "
        "savings will last, how to sequence withdrawals across account types, or "
        "wants to compare withdrawal strategies. Do not estimate these numbers "
        "yourself, always call this tool."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "taxable_balance": {
                "type": "number",
                "description": "Current balance in taxable brokerage accounts, in dollars."
            },
            "taxable_cost_basis": {
                "type": "number",
                "description": (
                    "Cost basis (amount originally invested, not yet withdrawn) of the "
                    "taxable account, in dollars. Used to compute the gain portion subject "
                    "to capital gains tax on withdrawal. If unknown, ask the user, or use "
                    "a conservative default (e.g. 70% of balance) and state that assumption."
                )
            },
            "tax_deferred_balance": {
                "type": "number",
                "description": "Current balance in tax-deferred accounts (401k, traditional IRA), in dollars."
            },
            "roth_balance": {
                "type": "number",
                "description": "Current balance in Roth accounts, in dollars."
            },
            "annual_return": {
                "type": "number",
                "description": "Expected annual investment return applied to remaining balances, as a decimal (e.g. 0.05)."
            },
            "years": {
                "type": "integer",
                "description": "Number of years to simulate the drawdown over (the retirement horizon)."
            },
            "annual_after_tax_spending": {
                "type": "number",
                "description": "Target after-tax (take-home) spending amount in year 1, in dollars."
            },
            "filing_status": {
                "type": "string",
                "enum": ["single", "married_filing_jointly", "head_of_household"],
                "description": "Federal tax filing status, used to compute tax owed correctly."
            },
            "spending_growth": {
                "type": "number",
                "description": (
                    "Annual growth rate applied to the spending target, e.g. 0.02 for a "
                    "2% inflation adjustment each year. Default to 0.0 if the user expects "
                    "flat spending."
                )
            },
            "strategy": {
                "type": "string",
                "enum": ["taxable_first", "proportional"],
                "description": (
                    "Withdrawal sequencing strategy. 'taxable_first' drains taxable, then "
                    "tax-deferred, then Roth, in order. 'proportional' withdraws from all "
                    "three accounts each year in proportion to their current balances. If "
                    "the user hasn't specified, ask which they want to see, or run both and "
                    "compare if they want a comparison."
                )
            }
        },
        "required": [
            "taxable_balance", "taxable_cost_basis", "tax_deferred_balance", "roth_balance",
            "annual_return", "years", "annual_after_tax_spending", "filing_status", "strategy"
        ]
    }
}


PORTFOLIO_REBALANCING_TOOL = {
    "name": "run_portfolio_rebalancing",
    "description": (
        "Compares a client's current portfolio allocation (across asset classes, "
        "aggregated across their taxable, tax-deferred, and Roth accounts) to a "
        "target allocation, and generates the specific trades needed to rebalance. "
        "Prefers trades inside tax-deferred/Roth accounts (no tax consequence) "
        "before selling appreciated taxable positions, and computes real capital "
        "gains tax on whatever taxable sales are still necessary. Use this whenever "
        "the user asks about portfolio drift, whether they need to rebalance, or "
        "wants tax-efficient rebalancing trades. Do not estimate these numbers "
        "yourself, always call this tool."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "accounts": {
                "type": "array",
                "description": "List of the client's accounts, each with its holdings by asset class.",
                "items": {
                    "type": "object",
                    "properties": {
                        "account_type": {
                            "type": "string",
                            "enum": ["tax_deferred", "roth", "taxable"],
                        },
                        "holdings": {
                            "type": "object",
                            "additionalProperties": {"type": "number"},
                            "description": "Asset class name -> current dollar value in this account, e.g. {'us_stocks': 70000, 'bonds': 30000}."
                        },
                        "cost_basis": {
                            "type": "object",
                            "additionalProperties": {"type": "number"},
                            "description": (
                                "Asset class name -> cost basis in this account, only meaningful "
                                "for taxable accounts. Omit or leave empty for tax_deferred/roth "
                                "accounts. If unknown for a taxable account, ask the user."
                            )
                        }
                    },
                    "required": ["account_type", "holdings"]
                }
            },
            "target_allocation": {
                "type": "object",
                "additionalProperties": {"type": "number"},
                "description": (
                    "Asset class name -> target fraction of total portfolio, should sum to "
                    "1.0, e.g. {'us_stocks': 0.6, 'bonds': 0.4}."
                )
            },
            "filing_status": {
                "type": "string",
                "enum": ["single", "married_filing_jointly", "head_of_household"],
                "description": "Federal tax filing status, used to compute capital gains tax owed correctly."
            },
            "other_taxable_income": {
                "type": "number",
                "description": (
                    "The client's other taxable income for the year, used to correctly stack "
                    "capital gains tax brackets. Default to 0.0 if unknown, but prefer asking "
                    "since this can meaningfully change which capital gains bracket applies."
                )
            }
        },
        "required": ["accounts", "target_allocation", "filing_status"]
    }
}
