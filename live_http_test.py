"""Live HTTP smoke test - runs against the running server at localhost:8000"""
import urllib.request, json, sys, logging
logging.disable(logging.CRITICAL)  # suppress all logging

BASE = "http://localhost:8000"
FIB = {1, 2, 3, 5, 8, 13, 21}
ok = 0; fail = 0

def c(name, cond, detail=""):
    global ok, fail
    sym = "PASS" if cond else "FAIL"
    print(f"  [{sym}] {name}" + (f" ({detail})" if detail else ""))
    if cond: ok += 1
    else: fail += 1

# A. Health
print("A. Health endpoint")
with urllib.request.urlopen(f"{BASE}/api/task-generation/health") as r:
    h = json.load(r)
c("model_ready=true",  h.get("model_ready") == True)
c("fibonacci=[1,2,3,5,8,13,21]", h.get("fibonacci") == [1,2,3,5,8,13,21])
c("startup_time<5s", (h.get("startup_time_s") or 0) < 5.0, str(h.get("startup_time_s")))

# B. Generate from text
print("B. Generate from text (POST /api/task-generation/generate)")
payload = json.dumps({"text": "System shall allow user registration with email.\nSystem must support secure login with JWT tokens.\nUsers may optionally view analytics dashboard.\nThe system should support password reset via email.\nAdmin must be able to manage user accounts.", "sprint_weeks": 2}).encode()
req = urllib.request.Request(f"{BASE}/api/task-generation/generate", data=payload,
    headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req) as r:
    resp = json.load(r)

flat = [us for t in resp.get("tasks", []) for us in t.get("user_stories", [])]
c("tasks_generated>0",      len(flat) > 0, f"got {len(flat)}")
c("language=en",            resp.get("language") == "en")
c("session_id_present",     bool(resp.get("history_session_id")))
c("all_SP_fibonacci",       all(t.get("story_points") in FIB for t in flat))
c("priority_variety>1",     len({t.get("priority") for t in flat}) > 1, str({t.get("priority") for t in flat}))
c("sprints_assigned",       any(t.get("sprint") for t in flat), str({t.get("sprint") for t in flat}))
print(f"   -> {len(flat)} stories | priorities={sorted({t.get('priority') for t in flat})} | sprints={sorted({t.get('sprint') for t in flat if t.get('sprint')})}")

# C. History
print("C. History (GET /api/task-generation/history)")
with urllib.request.urlopen(f"{BASE}/api/task-generation/history?limit=5") as r:
    hist = json.load(r)
sessions = hist.get("sessions", hist) if isinstance(hist, dict) else hist
c("history_is_dict_or_list", isinstance(hist, (dict, list)))
c("history_non_empty",       len(sessions) > 0, f"got {len(sessions)}")

# D. Reliability report
print("D. Reliability report (GET /api/task-generation/reliability-report)")
with urllib.request.urlopen(f"{BASE}/api/task-generation/reliability-report") as r:
    rel = json.load(r)
c("pillar_1_dataset",      "pillar_1_dataset_transparency" in rel)
c("pillar_2_model",        "pillar_2_production_model" in rel)
c("pillar_3_comparison",   "pillar_3_model_comparison" in rel)
p2 = rel.get("pillar_2_production_model", {})
cv_acc = p2.get("cv_accuracy_mean") or p2.get("cross_validation_accuracy_mean", "?")
c("cv_accuracy_reported",  cv_acc != "?", str(cv_acc))
print(f"   -> CV accuracy: {cv_acc}")

print(f"\n{'='*40}")
print(f"SUMMARY: {ok}/{ok+fail} checks passed")
sys.exit(0 if fail == 0 else 1)
