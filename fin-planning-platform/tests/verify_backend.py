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
print("Clients list:", resp.status_code, resp.json())
assert resp.status_code == 200
assert len(resp.json()) == 3
print("PASS: health and client listing work with no access gate set\n")

# Test 2: advisor mode without client_id should be rejected with 400
resp = client.post("/chat", json={"message": "hello", "mode": "advisor"})
print("Advisor mode, no client_id:", resp.status_code, resp.json())
assert resp.status_code == 400
print("PASS: advisor mode correctly requires client_id\n")

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
print("All backend endpoint checks passed (excluding /chat, which needs a live ANTHROPIC_API_KEY).")
