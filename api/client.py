"""
API client for RAFT, the retirement planning assistant.

Runs the tool-use loop: send user message + tool definitions to Claude,
execute any tool calls Claude makes against the real calculation engine,
send results back, and return Claude's final natural-language response.
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anthropic
from engine.monte_carlo import MonteCarloInputs, run_monte_carlo
from engine.withdrawal import AccountBalances, WithdrawalInputs, run_withdrawal_simulation
from engine.rebalancing import Account, RebalanceInputs, run_rebalancing
from engine.tax_brackets import FilingStatus
from api.tool_schemas import (
    RETIREMENT_MONTE_CARLO_TOOL,
    WITHDRAWAL_SEQUENCING_TOOL,
    PORTFOLIO_REBALANCING_TOOL,
)

MODEL = "claude-sonnet-4-6"

ALL_TOOLS = [RETIREMENT_MONTE_CARLO_TOOL, WITHDRAWAL_SEQUENCING_TOOL, PORTFOLIO_REBALANCING_TOOL]

BASE_SYSTEM_PROMPT = """You are RAFT, a retirement and financial planning assistant built \
on Claude (by Anthropic). If asked who or what you are, say plainly that you're RAFT, \
powered by Claude. You help understand retirement readiness, withdrawal sequencing, and \
portfolio rebalancing using real calculations, not guesses.

Critical rules:
1. Before calling any tool, make sure you have real values for its required inputs (or \
enough information to reasonably infer them, e.g. expected_return/volatility from a \
stated risk tolerance or asset allocation).
2. If you don't have enough information, ask for it directly. Explain that you need it \
to run an accurate simulation rather than a rough guess, since these projections are \
sensitive to their inputs. Ask for the minimum needed to proceed, not everything at once.
3. Never estimate or make up simulation, withdrawal, or rebalancing results yourself. \
Always call the appropriate tool.
4. When you get results back, explain them in plain language:
   - Retirement Monte Carlo: what the median outcome means, what the 10th/90th percentile \
range represents (best/worst case spread), and if a target was given, what the probability \
of success means in practical terms.
   - Withdrawal sequencing: how many years the portfolio is projected to last, total tax \
paid, and what that means for the retirement spending plan.
   - Rebalancing: what trades are being suggested and why, and highlight when tax-aware \
sequencing avoided or reduced capital gains tax versus a naive approach.
5. Be direct about uncertainty. These are estimates based on assumptions, not guarantees, \
and it's fine to say so.
6. For filing_status, translate a plain-language answer (e.g. "married", "single") into \
one of: single, married_filing_jointly, head_of_household. Ask if it's ambiguous.
7. Never use em dashes in your responses. Use commas, periods, or parentheses instead."""

CONSUMER_MODE_ADDENDUM = """

You're talking directly with the person whose money this is. Address them directly ("you", \
"your retirement"), and keep the tone approachable, this is likely not a financial \
professional, so avoid jargon or explain it when you use it.{intake_section}"""

ADVISOR_MODE_ADDENDUM = """

You're talking with a financial advisor who is prepping for or reviewing a client \
relationship, not the client themselves. The client's account data below is provided by \
the advisor's firm; treat it as ground truth for tool inputs rather than asking the advisor \
to re-supply numbers you already have. Address the advisor professionally and refer to "the \
client" or the client by name (not "you"), and feel free to use appropriate financial/tax \
terminology since you're speaking with a professional. When relevant, proactively flag \
things worth the advisor's attention (meaningful drift, a low probability of retirement \
success, an unusually high tax cost) rather than waiting to be asked.

Client context for this conversation:
{client_context}"""


def build_system_prompt(mode: str = "consumer", context: str | None = None) -> str:
    if mode == "advisor":
        return BASE_SYSTEM_PROMPT + ADVISOR_MODE_ADDENDUM.format(
            client_context=context or "(no client selected yet, ask the advisor which client this is for)"
        )

    intake_section = ""
    if context:
        intake_section = (
            f"\n\nInformation this person already provided in their intake form:\n{context}\n\n"
            "Use this directly, don't ask them to repeat it. Only ask for additional details "
            "genuinely needed to run a calculation."
        )
    return BASE_SYSTEM_PROMPT + CONSUMER_MODE_ADDENDUM.format(intake_section=intake_section)


def execute_tool_call(tool_name: str, tool_input: dict) -> dict:
    """Executes a tool call against the real calculation engine and returns a JSON-serializable result."""
    if tool_name == "run_retirement_monte_carlo":
        mc_inputs = MonteCarloInputs(
            starting_balance=tool_input["starting_balance"],
            annual_contribution=tool_input["annual_contribution"],
            years=tool_input["years"],
            expected_return=tool_input["expected_return"],
            volatility=tool_input["volatility"],
            contribution_growth=tool_input.get("contribution_growth", 0.0),
            target_balance=tool_input.get("target_balance"),
            num_trials=10_000,   # fixed internally, not exposed to Claude
            random_seed=None,
        )
        result = run_monte_carlo(mc_inputs)
        return {
            "median_balance": round(result.median_balance, 2),
            "percentile_10": round(result.percentile_10, 2),
            "percentile_90": round(result.percentile_90, 2),
            "probability_of_success": result.probability_of_success,
        }

    if tool_name == "run_withdrawal_sequencing":
        balances = AccountBalances(
            taxable_balance=tool_input["taxable_balance"],
            taxable_cost_basis=tool_input["taxable_cost_basis"],
            tax_deferred_balance=tool_input["tax_deferred_balance"],
            roth_balance=tool_input["roth_balance"],
        )
        withdrawal_inputs = WithdrawalInputs(
            balances=balances,
            annual_return=tool_input["annual_return"],
            years=tool_input["years"],
            annual_after_tax_spending=tool_input["annual_after_tax_spending"],
            filing_status=FilingStatus(tool_input["filing_status"]),
            spending_growth=tool_input.get("spending_growth", 0.0),
            strategy=tool_input["strategy"],
        )
        result = run_withdrawal_simulation(withdrawal_inputs)
        return {
            "years_lasted": result.years_lasted,
            "depleted": result.depleted,
            "total_tax_paid": round(result.total_tax_paid, 2),
            "final_balance": round(result.yearly_results[-1].ending_balance, 2) if result.yearly_results else 0.0,
        }

    if tool_name == "run_portfolio_rebalancing":
        accounts = [
            Account(
                account_type=acct["account_type"],
                holdings=acct.get("holdings", {}),
                cost_basis=acct.get("cost_basis", {}),
            )
            for acct in tool_input["accounts"]
        ]
        rebalance_inputs = RebalanceInputs(
            accounts=accounts,
            target_allocation=tool_input["target_allocation"],
            filing_status=FilingStatus(tool_input["filing_status"]),
            other_taxable_income=tool_input.get("other_taxable_income", 0.0),
        )
        result = run_rebalancing(rebalance_inputs)
        return {
            "trades": [
                {
                    "account_type": t.account_type,
                    "asset_class": t.asset_class,
                    "action": t.action,
                    "amount": round(t.amount, 2),
                }
                for t in result.trades
            ],
            "total_capital_gains_tax": round(result.total_capital_gains_tax, 2),
            "total_portfolio_value": round(result.total_portfolio_value, 2),
        }

    raise ValueError(f"Unknown tool: {tool_name}")


def chat(messages: list, mode: str = "consumer", context: str | None = None) -> tuple:
    """
    Runs one full turn of the tool-use loop given a message history.
    mode: "consumer" or "advisor". context: plain-text summary, either the
    consumer's own intake form data, or the advisor's selected client data.
    Returns (updated_messages, tool_calls), where tool_calls is a list of
    {"tool_name": str, "result": dict} for every tool call made this turn,
    in order, so the caller can render structured visuals alongside the text.
    """
    client = anthropic.Anthropic()
    system_prompt = build_system_prompt(mode=mode, context=context)
    tool_calls_this_turn = []

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=system_prompt,
            tools=ALL_TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool_call(block.name, block.input)
                tool_calls_this_turn.append({"tool_name": block.name, "result": result})
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        messages.append({"role": "user", "content": tool_results})

    return messages, tool_calls_this_turn