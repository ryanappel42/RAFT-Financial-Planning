import sys, os
sys.path.insert(0, "/home/claude/fin-planning-platform")

from fastapi.testclient import TestClient

# Test 1: no access code set -> gate disabled, endpoints work freely
os.environ.pop("ACCESS_CODE", None)
import importlib
import backend.main as main_module
importlib.reload(main_module)
client = TestClient(main_module.app)

resp = client.get("/")
print("Health check:", resp.status_code, resp.json())
assert resp.status_code == 200

resp = client.get("/clients")
print("Clients list:", resp.status_code, list(resp.json().keys()))
assert resp.status_code == 200
assert len(resp.json()) == 3
assert all("name" in c and "accounts" in c for c in resp.json().values()), "expected full client records, not just names"
print("PASS: health and client listing (full records) work with no access gate set\n")

# Test 2: advisor mode without a client record should be rejected with 400
resp = client.post("/chat", json={"message": "hello", "mode": "advisor"})
print("Advisor mode, no client:", resp.status_code, resp.json())
assert resp.status_code == 400
print("PASS: advisor mode correctly requires a client record\n")

# Test 3: access gate, set ACCESS_CODE and confirm requests are rejected without it
os.environ["ACCESS_CODE"] = "test-secret-123"
importlib.reload(main_module)
gated_client = TestClient(main_module.app)

resp = gated_client.get("/clients")
print("Gated request, no access code header:", resp.status_code)
assert resp.status_code == 401

resp = gated_client.get("/clients", headers={"x-access-code": "wrong-code"})
print("Gated request, wrong access code:", resp.status_code)
assert resp.status_code == 401

resp = gated_client.get("/clients", headers={"x-access-code": "test-secret-123"})
print("Gated request, correct access code:", resp.status_code)
assert resp.status_code == 200
print("PASS: access gate correctly blocks missing/wrong codes and allows the right one\n")

os.environ.pop("ACCESS_CODE", None)

# Test 4: a client the advisor "adds" in their browser (not one of the 3 built-ins)
# should work identically, since context is now built from whatever record is sent
from backend.mock_clients import format_client_context

new_client = {
    "id": "local-1234",
    "name": "Priya Nair",
    "age": 41,
    "filing_status": "single",
    "target_retirement_age": 62,
    "accounts": {
        "taxable_balance": 90_000,
        "taxable_cost_basis": 60_000,
        "tax_deferred_balance": 210_000,
        "roth_balance": 40_000,
    },
    "target_allocation": {"us_stocks": 0.7, "bonds": 0.3},
    "notes": "New client, aggressive growth target.",
}
ctx = format_client_context(new_client)
assert "Priya Nair" in ctx
assert "$90,000" in ctx
print("PASS: a locally-added client (not a built-in mock) formats into context correctly\n")

print("All backend endpoint checks passed (excluding /chat, which needs a live ANTHROPIC_API_KEY).")