"""
Mock client data for advisor mode.

A portfolio project shouldn't build real account aggregation, that's its
own large integration problem. These are a handful of realistic mock
clients an advisor can select in the demo, standing in for what would
otherwise come from a custodian/aggregation API.
"""

MOCK_CLIENTS = {
    "client_001": {
        "name": "Diane Foster",
        "age": 58,
        "filing_status": "married_filing_jointly",
        "target_retirement_age": 65,
        "accounts": {
            "taxable_balance": 320_000,
            "taxable_cost_basis": 210_000,
            "tax_deferred_balance": 610_000,
            "roth_balance": 95_000,
        },
        "allocation_accounts": [
            {"account_type": "tax_deferred", "holdings": {"us_stocks": 380_000, "intl_stocks": 100_000, "bonds": 130_000}},
            {"account_type": "roth", "holdings": {"us_stocks": 60_000, "bonds": 35_000}},
            {"account_type": "taxable", "holdings": {"us_stocks": 220_000, "bonds": 100_000},
             "cost_basis": {"us_stocks": 140_000, "bonds": 70_000}},
        ],
        "target_allocation": {"us_stocks": 0.55, "intl_stocks": 0.15, "bonds": 0.30},
        "notes": "Wants to retire at 65, currently 58. Moderate risk tolerance.",
    },
    "client_002": {
        "name": "Marcus Whitfield",
        "age": 47,
        "filing_status": "single",
        "target_retirement_age": 60,
        "accounts": {
            "taxable_balance": 180_000,
            "taxable_cost_basis": 90_000,
            "tax_deferred_balance": 340_000,
            "roth_balance": 220_000,
        },
        "allocation_accounts": [
            {"account_type": "tax_deferred", "holdings": {"us_stocks": 250_000, "bonds": 90_000}},
            {"account_type": "roth", "holdings": {"us_stocks": 180_000, "intl_stocks": 40_000}},
            {"account_type": "taxable", "holdings": {"us_stocks": 150_000, "bonds": 30_000},
             "cost_basis": {"us_stocks": 75_000, "bonds": 15_000}},
        ],
        "target_allocation": {"us_stocks": 0.65, "intl_stocks": 0.10, "bonds": 0.25},
        "notes": "Aggressive early-retirement target (60). Higher risk tolerance, stock-heavy.",
    },
    "client_003": {
        "name": "Eleanor Cho",
        "age": 66,
        "filing_status": "head_of_household",
        "target_retirement_age": 66,
        "accounts": {
            "taxable_balance": 450_000,
            "taxable_cost_basis": 260_000,
            "tax_deferred_balance": 380_000,
            "roth_balance": 140_000,
        },
        "allocation_accounts": [
            {"account_type": "tax_deferred", "holdings": {"us_stocks": 150_000, "bonds": 230_000}},
            {"account_type": "roth", "holdings": {"us_stocks": 90_000, "bonds": 50_000}},
            {"account_type": "taxable", "holdings": {"us_stocks": 250_000, "bonds": 200_000},
             "cost_basis": {"us_stocks": 140_000, "bonds": 120_000}},
        ],
        "target_allocation": {"us_stocks": 0.45, "intl_stocks": 0.05, "bonds": 0.50},
        "notes": "Already at target retirement age, transitioning into withdrawal phase. Conservative allocation.",
    },
}


def get_client_context(client_id: str) -> str:
    """Formats a mock client's data as plain text for injection into the advisor-mode system prompt."""
    client = MOCK_CLIENTS.get(client_id)
    if not client:
        return "(client not found)"

    accts = client["accounts"]
    lines = [
        f"Name: {client['name']}",
        f"Age: {client['age']}, target retirement age: {client['target_retirement_age']}",
        f"Filing status: {client['filing_status']}",
        f"Taxable balance: ${accts['taxable_balance']:,} (cost basis ${accts['taxable_cost_basis']:,})",
        f"Tax-deferred balance: ${accts['tax_deferred_balance']:,}",
        f"Roth balance: ${accts['roth_balance']:,}",
        f"Target allocation: {client['target_allocation']}",
        f"Notes: {client['notes']}",
    ]
    return "\n".join(lines)


def get_client_allocation_accounts(client_id: str):
    """Returns the accounts list in the shape run_portfolio_rebalancing's tool schema expects."""
    client = MOCK_CLIENTS.get(client_id)
    return client["allocation_accounts"] if client else []


def list_clients():
    """Returns id -> name for a client picker UI."""
    return {cid: c["name"] for cid, c in MOCK_CLIENTS.items()}
