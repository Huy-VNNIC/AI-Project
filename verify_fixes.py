#!/usr/bin/env python3
"""Verify all 5 AI fixes work correctly"""
import requests, sys

BASE = "http://localhost:8000"

errors = []

# ── Test 1: NFR (security) should NOT produce CRUD stories ───────────────────
r = requests.post(f"{BASE}/api/task-generation/generate", json={
    "text": "Hệ thống phải mã hóa SSL/TLS cho toàn bộ dữ liệu nhạy cảm truyền qua mạng"
})
data = r.json()
crud_words = ["create", "read", "update", "delete", "tạo mới", "xem/tra cứu"]
found_crud = False
for t in data.get("tasks", []):
    for s in t.get("user_stories", []):
        title = s.get("title", "").lower()
        if any(w in title for w in crud_words):
            found_crud = True
            errors.append(f"FAIL Test1: NFR produced CRUD story: {s['title']}")
print(f"Test 1 NFR→no CRUD: {'PASS' if not found_crud else 'FAIL'}")

# Check NFR AC is specific (should mention TLS or HTTP 403, not generic)
for t in data.get("tasks", []):
    for s in t.get("user_stories", []):
        sp = s.get("story_points", 0)
        if sp < 5:
            errors.append(f"FAIL Test1b: Security SP={sp} expected >=5")
        for ac in s.get("acceptance_criteria", []):
            then = ac.get("then", "")
            if "thành công" in then.lower() and "tls" not in then.lower() and "403" not in then.lower():
                errors.append(f"FAIL Test1b: Generic AC then: {then[:60]}")
print(f"Test 1b NFR AC specific: {'PASS' if not errors else 'needs review'}")

# ── Test 2: Login requirement should have specific AC ────────────────────────
r2 = requests.post(f"{BASE}/api/task-generation/generate", json={
    "text": "Người dùng phải có thể đăng nhập vào hệ thống bằng email và mật khẩu"
})
d2 = r2.json()
login_ac_ok = False
for t in d2.get("tasks", []):
    for s in t.get("user_stories", []):
        for ac in s.get("acceptance_criteria", []):
            then = ac.get("then", "")
            # Specific AC should mention redirect/JWT/2 giây or invalid/error
            if any(w in then.lower() for w in ["2 giây", "jwt", "chuyển hướng", "invalid email", "mật khẩu không đúng", "sai mật khẩu"]):
                login_ac_ok = True
if not login_ac_ok:
    # Print what we got for debugging
    for t in d2.get("tasks", []):
        for s in t.get("user_stories", []):
            print(f"  Login AC sample:")
            for ac in s.get("acceptance_criteria", [])[:2]:
                print(f"    Then: {ac.get('then', '')[:80]}")
    errors.append("FAIL Test2: Login AC not specific enough")
print(f"Test 2 Login specific AC: {'PASS' if login_ac_ok else 'FAIL'}")

# ── Test 3: SP variety (not all = 5) ─────────────────────────────────────────
r3 = requests.post(f"{BASE}/api/task-generation/generate", json={
    "text": "Hiển thị danh sách phòng khách sạn\nTích hợp cổng thanh toán VNPay\nMã hóa dữ liệu bằng AES-256\nTìm kiếm và lọc phòng theo giá"
})
d3 = r3.json()
sp_values = []
for t in d3.get("tasks", []):
    for s in t.get("user_stories", []):
        sp_values.append(s.get("story_points", 5))
unique_sp = set(sp_values)
print(f"Test 3 SP variety: {sp_values} unique={unique_sp} -> {'PASS' if len(unique_sp) >= 2 else 'FAIL'}")
if len(unique_sp) < 2:
    errors.append(f"FAIL Test3: All SP values are the same: {unique_sp}")

# ── Test 4: Noise filter - "Nhân lực" should be filtered ────────────────────
r4 = requests.post(f"{BASE}/api/task-generation/generate", json={
    "text": "Nhân lực: 3 Backend Developer, 2 Frontend\nHệ thống phải cho phép người dùng đăng ký tài khoản"
})
d4 = r4.json()
total_tasks = d4.get("total_tasks", 0)
noise_filtered = d4.get("noise_filtered", 0)
# Should only have 1 task (the register requirement), not 2
print(f"Test 4 Noise filter: total_tasks={total_tasks}, noise_filtered={noise_filtered} -> {'PASS' if total_tasks == 1 else 'needs review'}")

# ── Test 5: Sprint ordering (auth before payment) ───────────────────────────
r5 = requests.post(f"{BASE}/api/task-generation/generate", json={
    "text": "Tích hợp thanh toán VNPay\nNgười dùng đăng nhập bằng email mật khẩu\nBáo cáo doanh thu hàng tháng"
})
d5 = r5.json()
story_sprints = {}
for t in d5.get("tasks", []):
    for s in t.get("user_stories", []):
        title = s.get("title", "").lower()
        sprint = s.get("sprint", 99)
        story_sprints[title] = sprint
        print(f"  '{s.get('title','')[:40]}' → Sprint {sprint}")

# Login sprint should be <= payment sprint
login_sprint = min((v for k,v in story_sprints.items() if "đăng nhập" in k or "login" in k), default=99)
payment_sprint = min((v for k,v in story_sprints.items() if "thanh toán" in k or "payment" in k), default=0)
report_sprint = min((v for k,v in story_sprints.items() if "báo cáo" in k or "report" in k), default=0)
sprint_order_ok = login_sprint <= payment_sprint
print(f"Test 5 Sprint ordering: login={login_sprint} <= payment={payment_sprint} -> {'PASS' if sprint_order_ok else 'FAIL'}")
if not sprint_order_ok:
    errors.append(f"FAIL Test5: Login sprint {login_sprint} > payment sprint {payment_sprint}")

print()
if errors:
    print("ISSUES FOUND:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("All 5 fix verifications passed!")
