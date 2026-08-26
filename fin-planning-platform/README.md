# Financial Planning Platform - Calculation Engine + Tool Layer (Complete)

All three planning scenarios built and wired into Claude via tool use:
retirement readiness, withdrawal sequencing, and portfolio drift/rebalancing.
Claude sits as a conversational layer on top of a real Python calculation
engine, never estimating numbers itself. Platform/UI layer is the next phase.

## Structure

- `engine/growth.py` - deterministic compound growth projection, with support
  for contributions that grow annually (raises/inflation)
- `engine/monte_carlo.py` - Monte Carlo simulation of retirement accumulation
  using numpy, draws a random annual return per year/trial to produce a
  distribution of outcomes and a probability of hitting a target balance
- `engine/tax_brackets.py` - 2026 federal ordinary income brackets, standard
  deductions, and long-term capital gains brackets, with progressive tax
  calculation. **Needs annual updating** — see below.
- `engine/withdrawal.py` - retirement drawdown engine across three account
  types (taxable, tax-deferred, Roth). Solves for the gross withdrawal that
  hits a fixed after-tax spending target via bisection, under two sequencing
  strategies (taxable-first, proportional)
- `engine/rebalancing.py` - portfolio drift and tax-aware rebalancing.
  Compares current vs. target allocation across asset classes, generates
  trades preferring tax-deferred/Roth accounts (no tax consequence) before
  taxable, and computes real capital gains tax on whatever taxable sales
  remain necessary
- `api/tool_schemas.py` - all three tool definitions exposed to Claude via
  the Anthropic API (retirement Monte Carlo, withdrawal sequencing, portfolio
  rebalancing)
- `api/client.py` - runs the tool-use loop (Claude decides which tool(s) to
  call, we execute the real Python function, results go back to Claude to
  explain). System prompt enforces asking for missing inputs rather than
  assuming them, and adapts by mode (consumer vs. advisor).
- `backend/main.py` - FastAPI service wrapping the tool-use loop behind HTTP
  endpoints (`POST /chat`, `GET /clients`), with per-session conversation
  state and an optional access-code gate (`ACCESS_CODE` env var) for public
  deployment
- `backend/mock_clients.py` - a handful of realistic mock clients for the
  advisor-mode demo, standing in for real account aggregation (out of scope
  for this project)
- `frontend/` - Vite + React app, two routes (`/consumer`, `/advisor`) off a
  landing page, sharing a `ChatWindow` component. Ledger/statement visual
  design: ink navy + bone paper palette, Fraunces/Inter/IBM Plex Mono type,
  an animated compounding-curve signature element on the landing page.
- `tests/` - verification scripts checking engine output against hand-calculated
  values, including bracket-boundary cases, a portfolio-depletion scenario, a
  case demonstrating tax-aware rebalancing avoiding an unnecessary taxable
  gain entirely, and an end-to-end check of all three tools through the same
  dispatcher Claude actually calls

## Tax bracket maintenance

`engine/tax_brackets.py` hardcodes 2026 IRS figures (Revenue Procedure
2025-32): ordinary income brackets, standard deductions, and long-term
capital gains brackets, by filing status. The IRS adjusts these annually
for inflation, typically publishing the following year's figures around
October/November. **This file needs a manual update every tax year** —
`NEEDS_UPDATE_BY` at the top of the file marks when. In a production version
of this platform, this would be worth pulling from a maintained source
(a tax data API) rather than hand-updating a Python file, but that's out of
scope for this portfolio project.

## Running it

Requires `ANTHROPIC_API_KEY` set in your environment. Then:

```python
from api.client import chat

messages = [{"role": "user", "content": "Can I retire in 20 years?"}]
messages = chat(messages)
print(messages[-1]["content"])
```

Claude will ask for missing inputs before running any simulation, per the
system prompt in `api/client.py`, and will pick the right tool (or tools)
based on what's being asked — retirement readiness, withdrawal sequencing,
or rebalancing.

## Design notes

- Monte Carlo (accumulation) uses a simple normal-distribution return model
  (no fat tails, no year-to-year correlation) — worth flagging as a
  simplification if asked about it.
- Withdrawal sequencing and rebalancing both model taxable-account gains as
  a single blended gain fraction, not individual purchase lots with different
  cost bases/holding periods — a reasonable planning-tool approximation, not
  full lot-level accounting.
- Deterministic and Monte Carlo accumulation engines were cross-verified:
  at 0% volatility, Monte Carlo output matches the deterministic projection
  exactly.
- Withdrawal engine assumes withdrawals happen at the start of the year,
  then remaining balances grow for the year.
- Rebalancing assumes any asset class can be bought in any account (no
  investment-menu restrictions), and that cash raised by selling within an
  account can only fund buys within that same account (accounts can't fund
  each other's trades, matching how real brokerage/retirement accounts work).

## Next steps

- Advisor mode currently uses mock client data (`backend/mock_clients.py`)
  rather than real account aggregation, which is intentionally out of scope
  for this project.

## Deploying to Railway

Two Railway services off the same GitHub repo:

- **Backend**: root directory = repo root (it needs `engine/` and `api/` at
  the top level). `railway.json` at the repo root sets the start command.
  Env vars: `ANTHROPIC_API_KEY` (required), `ACCESS_CODE` (optional, gates
  the public API), `ALLOWED_ORIGIN` (set to the frontend's URL once it
  exists, to lock down CORS).
- **Frontend**: root directory = `/frontend`. `frontend/railway.json` sets
  the build/start commands (`npm run build` then `serve -s dist`). Env vars:
  `VITE_API_URL` (the backend's public URL), `VITE_ACCESS_CODE` (matching
  `ACCESS_CODE` if set). These are baked in at build time, so redeploy after
  changing them.

Generate a public domain for each service under Settings -> Networking.
Full step-by-step is in the deployment walkthrough from our conversation.
