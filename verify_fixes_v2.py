#!/usr/bin/env python3
"""Verify round-2 committee fixes:
  A. Tech-stack / timeline noise filter
  B. NFR user story reframing
  C. RBAC AC (not security AC) for phân quyền
  D. RISK story naming (no more "Security & Risk Mitigation" spam)
  E. Sprint count reduced (velocity 40 vs 30)
"""
import sys
sys.path.insert(0, ".")

from requirement_analyzer.task_gen.refinement import RequirementRefiner
from requirement_analyzer.task_gen.schemas_v2 import Requirement
from requirement_analyzer.api_v2_handler import V2TaskGenerator as V2TaskGenHandler

passed = failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"PASS  {name}")
        passed += 1
    else:
        print(f"FAIL  {name}  {detail}")
        failed += 1

# ── A: Tech-stack / timeline noise ────────────────────────────────────────────
h = V2TaskGenHandler.__new__(V2TaskGenHandler)
import re

tech_noise = [
    "Ngôn ngữ phát triển: Java/Spring Boot",
    "Cơ sở dữ liệu: PostgreSQL",
    "- Triển khai: Docker, Kubernetes",
    "1. Phân tích yêu cầu: 2 tuần",
    "2. Thiết kế hệ thống: 4 tuần",
    "- Giai đoạn 1: Analysis",
    "- java",
    "Tech stack: React, NodeJS",
    "Kiến trúc: Microservices",
    "Platform: Web-based",
]
for line in tech_noise:
    check(f"Noise filter: '{line[:50]}'", h._is_noise(line))

legit = "Người dùng cần đăng nhập vào hệ thống"
check(f"NOT noise: '{legit}'", not h._is_noise(legit))

# ── B: NFR user story reframing ───────────────────────────────────────────────
r = RequirementRefiner()

ssl_req = Requirement(requirement_id="B1",
    original_text="Hệ thống cần mã hóa dữ liệu truyền tải bằng SSL/TLS 1.2",
    language="vi")
ssl_out = r.refine(ssl_req)
check("NFR reframing: no 'ssl' or 'tls' in user story",
      "ssl" not in ssl_out.user_story.lower() and "tls" not in ssl_out.user_story.lower(),
      detail=ssl_out.user_story)
check("NFR reframing: mentions 'bảo vệ' or 'an toàn'",
      any(kw in ssl_out.user_story.lower() for kw in ["bảo vệ", "an toàn", "bảo mật", "securely", "protected"]),
      detail=ssl_out.user_story)

# ── C: RBAC AC branch ─────────────────────────────────────────────────────────
rbac_req = Requirement(requirement_id="C1",
    original_text="Hệ thống phân quyền truy cập theo vai trò admin và user thường",
    language="vi")
rbac_out = r.refine(rbac_req)
ac_texts = " ".join([ac.given + ac.when + ac.then for ac in rbac_out.acceptance_criteria]).lower()
check("RBAC AC: no TLS/403/15 min lockout in AC",
      not any(kw in ac_texts for kw in ["tls", "tls 1.2", "15 phút", "403"]),
      detail=ac_texts[:120])
check("RBAC AC: mentions role/permission terms",
      any(kw in ac_texts for kw in ["vai trò", "quyền", "admin", "permission", "role"]),
      detail=ac_texts[:120])

# ── D: RISK story naming ──────────────────────────────────────────────────────
from requirement_analyzer.task_gen.slicer import SmartSlicer
from requirement_analyzer.task_gen.schemas_v2 import RefinementOutput, AcceptanceCriterion, SeverityLevel

_dummy_ac = [AcceptanceCriterion(ac_id="AC1", given="Given valid state", when="When action occurs", then="Then system responds", priority=SeverityLevel.HIGH)]

slicer = SmartSlicer()

# Functional payment req: should produce "Error Handling & Rollback" not "Security & Risk Mitigation"
pay_ref = RefinementOutput(
    requirement_id="D1",
    title="Thanh toán đơn hàng",
    user_story="Là một khách hàng, tôi muốn thanh toán đơn hàng",
    acceptance_criteria=_dummy_ac,
    assumptions=[],
    constraints=[],
    non_functional_requirements=[],
    changes_summary=""
)
pay_slices = slicer.slice_requirement(pay_ref)
risk_titles = [s.title for sl in pay_slices.slices for s in sl.stories if "Risk Mitigation" in s.title or "Security & Risk" in s.title]
check("RISK story: no 'Security & Risk Mitigation' for payment req",
      len(risk_titles) == 0,
      detail=str(risk_titles))

# Non-CRUD functional req: should NOT get a RISK story at all
plain_ref = RefinementOutput(
    requirement_id="D2",
    title="Gửi thông báo email",
    user_story="Là một hệ thống, tôi muốn gửi thông báo email cho người dùng",
    acceptance_criteria=_dummy_ac,
    assumptions=[],
    constraints=[],
    non_functional_requirements=[],
    changes_summary=""
)
plain_slices = slicer.slice_requirement(plain_ref)
all_titles = [s.title for sl in plain_slices.slices for s in sl.stories]
spam_risk = [t for t in all_titles if "Security & Risk Mitigation" in t]
check("RISK story: no 'Security & Risk Mitigation' for generic notification req",
      len(spam_risk) == 0,
      detail=str(spam_risk))

# ── E: Sprint count (team_velocity now 40) ────────────────────────────────────
import inspect
sig = inspect.signature(V2TaskGenHandler.generate_from_text)
default_vel = sig.parameters.get("team_velocity")
check("Sprint velocity default = 40",
      default_vel is not None and default_vel.default == 40,
      detail=f"got {default_vel.default if default_vel else '?'}")

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{passed} passed, {failed} failed out of {passed+failed} checks")
sys.exit(0 if failed == 0 else 1)
