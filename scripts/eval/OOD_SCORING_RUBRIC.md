# OOD Evaluation Scoring Rubric

**Version**: 1.0  
**Purpose**: Đánh giá chất lượng task generation trên out-of-domain requirements  
**Target**: Production Ready (avg ≥ 3.5/5, type/domain accuracy ≥ 80%)

---

## 1. Title Clarity (`score_title_clarity`) — Scale 1-5

Đánh giá xem task title có rõ ràng, actionable và đúng ý requirement không.

### Tiêu chí chấm điểm:

- **5 — Excellent**
  - Title là câu hành động **rõ ràng, cụ thể**, đúng ý requirement
  - Có **action verb** (implement, enable, add, validate) + **object cụ thể**
  - Không dùng từ generic (`system`, `application`, `platform`, `feature`)
  - **Ví dụ**: 
    - ✅ "Enable two-factor authentication for user login"
    - ✅ "Calculate shipping costs based on delivery address"
    - ✅ "Send email notifications for high-value transactions"

- **4 — Good**
  - Đúng ý nhưng hơi **chung chung** / thiếu chi tiết
  - Action verb đúng nhưng object không cụ thể lắm
  - **Ví dụ**:
    - "Support two-factor authentication" (thiếu "for user login")
    - "Track order status" (thiếu "in real-time from warehouse to delivery")

- **3 — Acceptable**
  - Có liên quan nhưng **mơ hồ**, động từ/đối tượng lệch nhẹ
  - Dùng từ generic như "system", "application"
  - **Ví dụ**:
    - "Verify the system" (nên là "Verify user identity")
    - "Support the application functionality" (quá chung chung)

- **2 — Poor**
  - Title gần như **generic boilerplate** / sai trọng tâm
  - Action/object không khớp requirement
  - **Ví dụ**:
    - "Build customers capability" (không rõ build cái gì)
    - "Add users transfer" (grammar lỗi + không rõ nghĩa)

- **1 — Unacceptable**
  - Sai ý hoàn toàn / không đọc được / vô nghĩa
  - **Ví dụ**:
    - "Need admin users" (modal verb làm action)
    - "feature works correctly" (không phải title)

---

## 2. Description Correctness (`score_desc_correctness`) — Scale 1-5

Đánh giá xem description có diễn giải đúng requirement, đủ bối cảnh và scope không.

### Tiêu chí chấm điểm:

- **5 — Excellent**
  - Description **diễn giải đúng** requirement (không copy y nguyên)
  - Đủ **context + scope** hợp lý (use case, constraints, expected outcome)
  - Không có boilerplate vô nghĩa
  - **Ví dụ**:
    - ✅ "The system must verify user identity using two-factor authentication via SMS or authenticator app. Users will receive a verification code after entering their password."

- **4 — Good**
  - Đúng ý nhưng **thiếu một phần** scope/chi tiết
  - Context đầy đủ nhưng hơi chung chung
  - **Ví dụ**:
    - "Users can transfer funds between accounts with real-time updates." (thiếu validation rules, limits)

- **3 — Acceptable**
  - Liên quan nhưng có **chỗ sai/thiếu đáng kể**
  - Quá ngắn hoặc quá chung chung
  - **Ví dụ**:
    - "The system needs to verify users. This feature will support operations."

- **2 — Poor**
  - **Nhiều phần sai** / lạc đề / không khớp requirement
  - Copy boilerplate: "This feature will support {domain} operations. Include proper validation..."
  - **Ví dụ**:
    - "We need to implement need customers. This feature will support ecommerce operations."

- **1 — Unacceptable**
  - **Sai hoàn toàn** / không liên quan gì đến requirement
  - Chỉ toàn boilerplate

---

## 3. Acceptance Criteria Testability (`score_ac_testability`) — Scale 1-5

Đánh giá xem acceptance criteria có **testable** (đo/verify được) không.

### Tiêu chí chấm điểm:

- **5 — Excellent**
  - AC có thể **đo/verify rõ ràng** (Given/When/Then hoặc checklist cụ thể)
  - **Ít hoặc không có boilerplate** generic
  - AC liên quan trực tiếp đến requirement
  - **Ví dụ**:
    - ✅ "User receives SMS with 6-digit code within 30 seconds"
    - ✅ "System blocks login after 3 failed attempts for 15 minutes"
    - ✅ "Transaction encrypted with AES-256 before transmission"

- **4 — Good**
  - Test được nhưng **còn 1-2 ý chung chung**
  - Phần lớn AC cụ thể, có một vài boilerplate
  - **Ví dụ**:
    - "Two-factor code sent successfully" (ok nhưng thiếu timing)
    - "User can view transaction history" (thiếu filter/limit)

- **3 — Acceptable**
  - **Một nửa test được, một nửa chung chung**
  - Có mix giữa specific AC và boilerplate
  - **Ví dụ**:
    - "Feature works correctly" ❌ (boilerplate)
    - "Response time under 2 seconds" ✅ (testable)

- **2 — Poor**
  - **Chủ yếu boilerplate**, không đo được
  - AC không liên quan đến requirement
  - **Ví dụ**:
    - "Works correctly for verify the system"
    - "All error conditions handled gracefully"
    - "System validates all input before processing"

- **1 — Unacceptable**
  - **Hầu như không test được** / toàn boilerplate
  - AC sai hoặc không liên quan

---

## 4. Label Accuracy — Binary (0/1)

### A. Type Label (`score_label_type`)

Đánh giá xem type label có đúng không.

**Scoring**:
- **1** = Type đúng (functional/interface/security/performance/integration)
- **0** = Type sai

**Expected types theo requirement**:
- `functional`: Business logic, CRUD, workflows
- `interface`: UI/UX, accessibility, forms, navigation
- `security`: Authentication, authorization, encryption, audit
- `performance`: Speed, scalability, load
- `integration`: External APIs, third-party services

**Note**: Nếu requirement애매 (có thể là nhiều type), cho **1** nếu type hợp lý.

### B. Domain Label (`score_label_domain`)

Đánh giá xem domain label có đúng không.

**QUAN TRỌNG**: Model chỉ biết **5 domains**: {ecommerce, finance, healthcare, iot, education}

**Scoring**:
- **1** = Domain đúng (trong scope 5 domains)
- **0** = Domain sai
- **N/A** = Domain ngoài scope (HR, gaming, real estate, logistics...)

**Thêm cột `domain_applicable`**:
- `domain_applicable=1`: Requirement thuộc 1 trong 5 domains
- `domain_applicable=0`: Requirement OOD (HR, gaming, real estate...)

**Lưu ý**: Nếu `domain_applicable=0`, **bỏ qua domain accuracy** trong tổng kết (hoặc tính riêng).

### C. Priority Label (`score_priority_reasonable`)

Đánh giá xem priority có hợp lý không.

**Scoring**:
- **1** = Priority hợp lý (High/Medium/Low khớp với risk/urgency)
- **0** = Priority vô lý

**Heuristic**:
- **High**: Security, compliance, payment, critical business logic
- **Medium**: Features, workflows, nice-to-have
- **Low**: Cosmetic, convenience features

---

## 5. Quality Flags — Binary (0/1)

### A. Duplicates (`has_duplicates`)

**Scoring**:
- **1** = Có AC trùng nhau (same meaning)
- **0** = Không có duplicate

**Ví dụ trùng**:
- "Feature works correctly for X"
- "Feature works correctly for Y"

### B. Generic Boilerplate (`flag_generic`)

**Scoring**:
- **1** = ≥50% AC là boilerplate generic
- **0** = AC mostly specific

**Boilerplate phrases**:
- "works correctly"
- "handled gracefully"
- "validates all input"
- "response time under 2 seconds" (không liên quan)

### C. Wrong Intent (`flag_wrong_intent`)

**Scoring**:
- **1** = Task **hoàn toàn hiểu sai** requirement
- **0** = Intent đúng (dù có thể execution kém)

---

## 6. Aggregate Metrics

### Overall Quality Score

Tính trung bình của 3 quality scores:

```
avg_quality = (score_title_clarity + score_desc_correctness + score_ac_testability) / 3
```

### Pass Criteria (Production Ready)

✅ **avg_quality ≥ 3.5/5**  
✅ **duplicate_rate ≤ 10%**  
✅ **type_accuracy ≥ 80%**  
✅ **domain_accuracy ≥ 80%** (chỉ tính in-scope domains)

---

## 7. Notes Column

Ghi ngắn gọn **1 dòng** về vấn đề chính:

**Ví dụ**:
- "Title too generic - should be 'Enable 2FA' not 'Verify system'"
- "Domain wrong: should be banking, not ecommerce"
- "AC all boilerplate, not testable"
- "Understood requirement correctly but poor execution"

---

## 8. How to Use This Rubric

### Phase 1: Pilot Evaluation (50 rows)

1. **Random sample 50 rows** từ 184 success rows
2. **Chấm theo rubric** (10-15 phút/row)
3. **Run**: `python scripts/eval/02_summarize_ood_scores.py scripts/eval/ood_pilot.csv`
4. **Checkpoint**:
   - If `avg_quality < 3.2` → **STOP**, cải tiến generator trước
   - If `avg_quality ≥ 3.5` → Proceed to full eval

### Phase 2: Full Evaluation (184 rows)

Chấm hết 184 rows khi pilot pass.

### Phase 3: Failure Analysis (66 rows)

Categorize 66 failed rows:
- **No requirement detected** (threshold issue)
- **Not a requirement** (description/note/example)
- **Generator error** (crash/exception)
- **Too complex** (multiple clauses, long spec)

---

## 9. Common Issues & Quick Fixes

| Issue | Example | Quick Fix |
|-------|---------|-----------|
| **Modal verb in title** | "Need users authentication" | Filter modal verbs from action extraction |
| **Generic object** | "Verify the system" | Skip `{system, application, platform}` objects |
| **Wrong domain** | Banking → ecommerce | Retrain domain classifier with more data |
| **WCAG in non-UI** | Security task + WCAG 2.1 | Filter WCAG criteria if `type != interface` |
| **Boilerplate AC** | "Works correctly..." | Dedupe + filter generic phrases |

---

## 10. Scoring Template (CSV columns)

```csv
id,requirement_sentence,generated_title,generated_description,
score_title_clarity,score_desc_correctness,score_ac_testability,
score_label_type,score_label_domain,score_priority_reasonable,
domain_applicable,has_duplicates,flag_generic,flag_wrong_intent,notes
```

---

**Prepared by**: AI Task Generation Team  
**Date**: 2026-01-20  
**Review**: Before running full OOD eval
