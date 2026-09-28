import httpx
from datetime import date

client = httpx.Client(base_url="http://127.0.0.1:8000")

print("=========================================================")
print("  LIVE FASTAPI & INVENTORY WORKFLOW INTEGRATION TEST    ")
print("=========================================================")

print("\n1. Testing Live Backend Health Check (/health)...")
h = client.get("/health")
assert h.status_code == 200
print("   [OK] Status 200:", h.json())

print("\n2. Testing Live Registration (Role: Food Quality Inspector)...")
reg_payload = {
    "full_name": "Dr. Elena Rostova",
    "email": "elena.inspector@freshguard.org",
    "password": "SecurePassword2026!",
    "role": "food_quality_inspector"
}
r = client.post("/auth/register", json=reg_payload)
if r.status_code == 409:
    print("   [OK] User already registered from previous run (HTTP 409 Conflict handled).")
else:
    assert r.status_code == 201
    print("   [OK] User registered successfully (HTTP 201 Created).")

print("\n3. Testing Live Login (/auth/login)...")
login_res = client.post("/auth/login", json={"email": reg_payload["email"], "password": reg_payload["password"]})
assert login_res.status_code == 200
token = login_res.json()["access_token"]
print("   [OK] Login successful (HTTP 200). JWT Bearer token received.")

print("\n4. Testing Live User Context (/auth/me)...")
me_res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
assert me_res.status_code == 200
user_data = me_res.json()
assert user_data["role"] == "food_quality_inspector"
print(f"   [OK] Authenticated User: {user_data['full_name']} | Role: {user_data['role']}")

print("\n5. Registering Food Items to PostgreSQL/Database via API...")
item1 = {
    "name": "Organic Strawberries",
    "category": "Fruits",
    "batch_number": "BATCH-FR-881",
    "quantity": 24,
    "expiry_date": "2026-09-15"
}
item2 = {
    "name": "Artisan Pasteurized Whole Milk",
    "category": "Dairy Products",
    "batch_number": "BATCH-DY-009",
    "quantity": 0,
    "expiry_date": "2026-08-15"
}

f1 = client.post("/inventory", json=item1, headers={"Authorization": f"Bearer {token}"})
assert f1.status_code == 201
print(f"   [OK] Created '{item1['name']}' (ID: {f1.json()['id']})")

f2 = client.post("/inventory", json=item2, headers={"Authorization": f"Bearer {token}"})
assert f2.status_code == 201
print(f"   [OK] Created '{item2['name']}' (ID: {f2.json()['id']})")

print("\n6. Retrieving and Validating Stored Inventory Records...")
inv = client.get("/inventory", headers={"Authorization": f"Bearer {token}"})
assert inv.status_code == 200
items = inv.json()
print(f"   [OK] Retrieved {len(items)} items from database:")

today_str = str(date.today())
for item in items:
    name = item["name"]
    cat = item["category"]
    batch = item["batch_number"]
    qty = item["quantity"]
    exp_date = item["expiry_date"]
    
    avail = "In Stock" if qty > 0 else "Out of Stock"
    if exp_date < today_str:
        exp_status = "Expired"
    elif exp_date == today_str:
        exp_status = "Expiring Today"
    else:
        exp_status = "Valid"
        
    print(f"   * {name} ({cat}) | Batch: {batch} | Qty: {qty} [{avail}] | Expiry: {exp_date} [{exp_status}]")

print("\n=========================================================")
print("  ALL LIVE API AND INVENTORY TESTS PASSED WITH 100% SUCCESS!")
print("=========================================================")
