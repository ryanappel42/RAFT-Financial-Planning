"""
Formats consumer intake form data into plain-text context for the system
prompt, the same idea as mock_clients.get_client_context but for a
self-service consumer who filled out their own intake form.
"""


def _fmt_currency(value) -> str:
    if value is None:
        return "not provided"
    return f"${value:,.0f}"


def format_intake_context(intake: dict) -> str:
    lines = []

    if intake.get("age") is not None:
        lines.append(f"Age: {intake['age']}")
    if intake.get("target_retirement_age") is not None:
        lines.append(f"Target retirement age: {intake['target_retirement_age']}")

    lines.append(f"Taxable brokerage balance: {_fmt_currency(intake.get('taxable_balance'))}")
    lines.append(f"Tax-deferred (401k/traditional IRA) balance: {_fmt_currency(intake.get('tax_deferred_balance'))}")
    lines.append(f"Roth balance: {_fmt_currency(intake.get('roth_balance'))}")

    if intake.get("annual_contribution") is not None:
        lines.append(f"Annual contribution: {_fmt_currency(intake['annual_contribution'])}")
    if intake.get("risk_tolerance"):
        lines.append(f"Stated risk tolerance: {intake['risk_tolerance']}")
    if intake.get("filing_status"):
        lines.append(f"Filing status: {intake['filing_status']}")
    if intake.get("target_balance") is not None:
        lines.append(f"Target retirement balance: {_fmt_currency(intake['target_balance'])}")

    lines.append(
        "Note: taxable account cost basis (needed for capital gains calculations in "
        "withdrawal/rebalancing scenarios) was not collected in the intake form, ask for "
        "it if a withdrawal or rebalancing question comes up."
    )

    return "\n".join(lines)