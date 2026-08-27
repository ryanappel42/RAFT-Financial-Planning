"""
Starter client data for advisor mode.

A portfolio project shouldn't build real account aggregation or a database,
those are their own large scope. These three are starter clients an advisor
sees on load; advisors can also add their own clients directly in the
browser (see frontend), which are sent to the backend as full records per
request rather than stored server-side.
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
        "target_allocation": {"us_stocks": 0.45, "intl_stocks": 0.05, "bonds": 0.50},
        "notes": "Already at target retirement age, transitioning into withdrawal phase. Conservative allocation.",
    },
}


def get_all_clients() -> dict:
    """Returns id -> full client record, for the advisor-mode client picker."""
    return MOCK_CLIENTS


def format_client_context(client: dict) -> str:
    """
    Formats a client record (built-in or one the advisor just added in their
    browser) as plain text for injection into the advisor-mode system prompt.
    """
    if not client:
        return "(client not found)"

    accts = client.get("accounts", {})
    lines = [
        f"Name: {client.get('name', 'Unknown')}",
        f"Age: {client.get('age', 'unknown')}, target retirement age: {client.get('target_retirement_age', 'unknown')}",
        f"Filing status: {client.get('filing_status', 'unknown')}",
        f"Taxable balance: ${accts.get('taxable_balance', 0):,} (cost basis ${accts.get('taxable_cost_basis', 0):,})",
        f"Tax-deferred balance: ${accts.get('tax_deferred_balance', 0):,}",
        f"Roth balance: ${accts.get('roth_balance', 0):,}",
        f"Target allocation: {client.get('target_allocation', {})}",
        f"Notes: {client.get('notes', '')}",
    ]
    return "\n".join(lines)