# Giải Thích Chi Tiết: Task vs User Story & 7 Bước Pipeline

## 📚 Phần 1: Task vs User Story - Khác Biệt Cơ Bản

### 1.1 Định Nghĩa

#### **User Story (Câu chuyện người dùng)**
```
"As a [ROLE], I want to [ACTION], so that [BENEFIT]"
```

💡 **Ví dụ:**
```
"As a Patient, I want to register an appointment online, 
so that I don't need to call the clinic"
```

**Đặc điểm:**
- ✅ Từ góc nhìn của người dùng
- ✅ Tập trung vào giá trị/lợi ích
- ✅ Không kỹ thuật, dễ hiểu
- ✅ Có độ phức tạp trung bình (3-8 story points)

---

#### **Task (Công việc/Tác vụ)**
```
"Implement [TECHNICAL ACTION] to support [USER STORY]"
```

💡 **Ví dụ:**
```
"Create REST API endpoint POST /appointments to handle booking requests"
```

**Đặc điểm:**
- ✅ Từ góc nhìn kỹ thuật
- ✅ Tập trung vào cách thực hiện
- ✅ Χο developers biết phải làm gì
- ✅ Có độ phức tạp nhỏ (1-3 story points)

---

### 1.2 Sơ Đồ Quan Hệ

```
┌─────────────────────────────────────────────────────────────┐
│                    1 REQUIREMENT                            │
│   "Phải quản lý hồ sơ bệnh nhân trực tuyến"               │
└────────────────────┬────────────────────────────────────────┘
                     │
      ┌──────────────┴──────────────┬──────────────┐
      │                             │              │
      ▼                             ▼              ▼
┌─────────────────┐        ┌─────────────────┐  ┌──────────────┐
│  USER STORY 1   │        │  USER STORY 2   │  │ USER STORY 3 │
│  (Happy Path)   │        │ (Edge Cases)    │  │  (Validation)│
│                 │        │                 │  │              │
│ "As a Nurse, I  │        │ "As a System,   │  │ "As a Nurse, │
│  want to create │        │  I want to      │  │  I want to   │
│  patient record"│        │  handle invalid │  │  validate    │
└────────┬────────┘        │  patient data"  │  │  duplicate   │
         │                 └────────┬────────┘  │  IDs"        │
         │                          │           └──────┬───────┘
         │         ┌────────────────┴────────┐        │
         │         │                         │        │
         ▼         ▼                         ▼        ▼
    ┌────────────┐ ┌─────────────┐ ┌──────────────┐ ┌──────────┐
    │  TASK 1.1  │ │   TASK 1.2  │ │   TASK 1.3   │ │ TASK 1.4 │
    │            │ │             │ │              │ │          │
    │ Design DB  │ │ Create API  │ │ Build UI     │ │ Write    │
    │ Schema     │ │ Endpoint    │ │ Form         │ │ Tests    │
    └────────────┘ └─────────────┘ └──────────────┘ └──────────┘
```

---

### 1.3 Bảng So Sánh

| Khía cạnh | User Story | Task |
|-----------|-----------|------|
| **Người viết** | Product Owner | Developer/Architect |
| **Người dùng** | Business Analyst | Developers |
| **Tập trung vào** | "Cái gì" & "Tại sao" | "Cách làm" |
| **Ví dụ** | "Tính năng đặt lịch hẹn" | "API POST /appointments" |
| **Complexity** | Medium (3-8 SP) | Small (1-3 SP) |
| **Acceptance Criteria** | Business-focused | Technical-focused |
| **Duration** | 1-3 sprints | 1-2 days |

---

## 🔄 Phần 2: 7 Bước Pipeline Chi Tiết

### 2.1 Sơ Đồ Tổng Quan

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: INPUT REQUIREMENT                                        │
│ (Text, MD, DOCX, PDF)                                            │
└────────────────────┬─────────────────────────────────────────────┘
                     │ ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: AI GENERATE USER STORIES                                 │
│ (NLP + Semantic Analysis)                                        │
└────────────────────┬─────────────────────────────────────────────┘
                     │ ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: AI GENERATE TASKS                                        │
│ (Decomposition Strategies: CRUD, Flow, Domain, Quality, Integration)
└────────────────────┬─────────────────────────────────────────────┘
                     │ ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: AI GENERATE ACCEPTANCE CRITERIA                          │
│ (BDD Format: Given-When-Then)                                    │
└────────────────────┬─────────────────────────────────────────────┘
                     │ ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: AI GENERATE TEST CASES                                   │
│ (Unit, Integration, E2E Tests)                                   │
└────────────────────┬─────────────────────────────────────────────┘
                     │ ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: AI ESTIMATE EFFORT                                       │
│ (Story Points, Function Points, Use Case Points)                 │
└────────────────────┬─────────────────────────────────────────────┘
                     │ ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 7: SHOW PROJECT DASHBOARD                                   │
│ (Analytics, Timeline, Risk Assessment)                           │
└──────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Chi Tiết Mỗi Bước

## **STEP 1: INPUT REQUIREMENT**

### 📥 Input Processing

**Mục đích:** Nhập yêu cầu từ các định dạng khác nhau

```
Định dạng hỗ trợ:
├── TXT (Plain text)
├── MD (Markdown)
├── DOCX (Microsoft Word)
└── PDF (PDF Document)
```

**Ví dụ Input:**
```markdown
# Healthcare Management System Requirements

## Appointment Management
Phải cho phép bệnh nhân đặt lịch hẹn khám bệnh trực tuyến
- Thời gian đặt lịch: trước 7 ngày
- Hỗ trợ thanh toán online
- Gửi SMS nhắc nhở 1 ngày trước

## Patient Record Management
Phải quản lý hồ sơ bệnh nhân đầy đủ với lịch sử bệnh án
- Lưu giữ thông tin cá nhân
- Theo dõi lịch sử điều trị
- Tích hợp kết quả xét nghiệm
```

**Kỹ Thuật Sử Dụng:**
```python
# File Parsing
├── python-docx → Extract DOCX
├── PyPDF2 → Extract PDF
├── Markdown parser → Parse MD
└── Plain text → Direct read

# Output
{
    "raw_text": "...",
    "requirements": [
        {
            "id": "REQ-001",
            "title": "Appointment Booking",
            "description": "...",
            "category": "Functional"
        }
    ]
}
```

---

## **STEP 2: AI GENERATE USER STORIES**

### 🎯 AI User Story Generation

**Mục đích:** Chuyển requirement thành user stories (As a... I want... So that...)

**Kỹ Thuật Sử Dụng:**

#### A. NLP Processing
```
1. Tokenization
   Input: "Phải cho phép bệnh nhân đặt lịch hẹn"
   Output: ["Phải", "cho", "phép", "bệnh", "nhân", "đặt", "lịch", "hẹn"]

2. Named Entity Recognition (NER)
   Input: "Phải cho phép bệnh nhân đặt lịch hẹn"
   Output: 
   - ENTITY: "bệnh nhân" (Patient)
   - ACTION: "đặt lịch hẹn" (book appointment)
   - CONTEXT: "trực tuyến" (online)

3. Dependency Parsing
   Input: "bệnh nhân đặt lịch hẹn"
   Output:
   - Subject: "bệnh nhân"
   - Predicate: "đặt"
   - Object: "lịch hẹn"
```

#### B. Semantic Analysis
```
- Extract ROLE: "Patient"
- Extract ACTION: "Book Appointment"
- Extract BENEFIT: "Schedule conveniently without calling"
- Extract CONTEXT: "Online, advance notice"
```

#### C. User Story Generation
```python
# Algorithm
user_story = f"As a {ROLE}, I want to {ACTION}, so that {BENEFIT}"

# Output
"As a Patient, I want to book an appointment online, 
so that I can schedule conveniently without calling the clinic"
```

**Ví Dụ Output:**

```json
{
    "requirement_id": "REQ-001",
    "requirement_text": "Phải cho phép bệnh nhân đặt lịch hẹn",
    "user_stories": [
        {
            "id": "US-001",
            "title": "Appointment Booking - Happy Path",
            "user_story": "As a Patient, I want to book an appointment online, so that I can schedule conveniently",
            "role": "Patient",
            "action": "book appointment",
            "benefit": "schedule conveniently",
            "priority": "High",
            "type": "Feature"
        },
        {
            "id": "US-002",
            "title": "Appointment Booking - Validation",
            "user_story": "As a System, I want to validate booking requirements, so that only valid appointments are created",
            "role": "System",
            "action": "validate booking",
            "benefit": "ensure data quality",
            "priority": "High",
            "type": "Feature"
        }
    ]
}
```

---

## **STEP 3: AI GENERATE TASKS**

### 🔨 AI Task Decomposition

**Mục đích:** Chia user story thành các technical tasks

**5 Decomposition Strategies:**

### Strategy 1: CRUD (Create, Read, Update, Delete)
```
User Story: "Quản lý hồ sơ bệnh nhân"
    │
    ├─ Task: Create patient record (NEW PATIENT)
    ├─ Task: View patient records (LIST/SEARCH)
    ├─ Task: Update patient information (EDIT)
    └─ Task: Archive patient record (DELETE/ARCHIVE)
```

### Strategy 2: FLOW (Happy Path + Edge Cases)
```
User Story: "Đặt lịch hẹn khám bệnh"
    │
    ├─ Task: Happy Path
    │   ├ Patient logs in
    │   ├ Select doctor & time
    │   ├ Pay fees
    │   └ Receive confirmation
    │
    ├─ Task: Edge Cases & Validation
    │   ├ Slot already booked
    │   ├ Invalid payment
    │   └ Doctor unavailable
    │
    └─ Task: Error Handling
        ├ Network timeout
        ├ Payment gateway error
        └ Booking system down
```

### Strategy 3: DOMAIN (Theo miền chuyên biệt)
```
User Story: "Quản lý bệnh nhân" (Healthcare domain)
    │
    ├─ Task: Healthcare specific
    │   ├ HIPAA compliance
    │   ├ Medical history tracking
    │   └ Drug interaction checking
    │
    └─ Task: General features
        ├ Database CRUD
        ├ Authentication
        └ Logging
```

### Strategy 4: QUALITY (Quality aspects)
```
User Story: "Đặt lịch hẹn"
    │
    ├─ Task: Happy Path Implementation
    ├─ Task: Validation & Input Checking
    ├─ Task: Error Handling & Recovery
    ├─ Task: Performance Optimization
    ├─ Task: Security Hardening
    └─ Task: Logging & Monitoring
```

### Strategy 5: INTEGRATION (System integration)
```
User Story: "Tính toán viện phí"
    │
    ├─ Task: Core logic
    │   └ Calculate bill amount
    │
    ├─ Task: Integration
    │   ├ With Insurance system (API)
    │   ├ With Payment gateway (API)
    │   └ With Accounting system (API)
    │
    └─ Task: Fallback
        └ Offline calculation support
```

**Kỹ Thuật Sử Dụng:**

```python
# Machine Learning
1. Intent Recognition (NLU)
   - Identify CRUD operation type
   - Detect flow patterns
   
2. Semantic Matching
   - Find similar requirements
   - Group by domain
   
3. Rule-based Decomposition
   - Apply strategy based on type
   - Generate subtasks
```

**Ví Dụ Output:**

```json
{
    "user_story_id": "US-001",
    "user_story": "As a Patient, I want to book appointment",
    "decomposition_strategy": "FLOW",
    "tasks": [
        {
            "id": "TASK-001",
            "title": "Design appointment booking database schema",
            "type": "Technical",
            "complexity": "Medium",
            "story_points": 2,
            "description": "Create tables for appointments with doctor scheduling"
        },
        {
            "id": "TASK-002",
            "title": "Implement appointment API endpoint",
            "type": "Technical",
            "complexity": "Medium",
            "story_points": 3,
            "backend_work": "FastAPI route implementation"
        },
        {
            "id": "TASK-003",
            "title": "Build appointment booking UI form",
            "type": "Technical",
            "complexity": "Medium",
            "story_points": 3,
            "frontend_work": "React form component"
        },
        {
            "id": "TASK-004",
            "title": "Add appointment validation logic",
            "type": "Technical",
            "complexity": "Low",
            "story_points": 2,
            "validation_rules": "Date, time, patient, doctor"
        },
        {
            "id": "TASK-005",
            "title": "Write unit tests for booking",
            "type": "QA",
            "complexity": "Medium",
            "story_points": 2,
            "test_coverage": "> 90%"
        }
    ]
}
```

---

## **STEP 4: AI GENERATE ACCEPTANCE CRITERIA**

### ✅ Acceptance Criteria Generation

**Format: BDD (Behavior Driven Development)**

```gherkin
Scenario: Patient books appointment successfully

Given:   Patient is logged in
And:     Doctor schedule is available
And:     Patient has valid insurance

When:    Patient selects available time slot
And:     Patient confirms booking
And:     Payment is processed

Then:    Appointment is created in system
And:     Confirmation email is sent
And:     SMS reminder is scheduled
And:     Appointment appears in patient dashboard
```

**Kỹ Thuật Sử Dụng:**

```python
# BDD Generation Algorithm
1. Extract preconditions (Given clauses)
   └─ From requirement constraints
   
2. Extract user actions (When clauses)
   └─ From requirement main flow
   
3. Extract expected outcomes (Then clauses)
   └─ From requirement benefits/goals
   
4. Generate alternative scenarios
   └─ Edge cases, error conditions
```

**Ví Dụ Output:**

```json
{
    "task_id": "TASK-002",
    "task_title": "Implement appointment API endpoint",
    "acceptance_criteria": [
        {
            "id": "AC-001",
            "title": "Validate appointment booking request",
            "given": "Patient sends booking request with valid data",
            "when": "API endpoint POST /appointments receives the request",
            "then": "Appointment should be created and return 200 OK with appointment ID",
            "test_case": "test_valid_appointment_booking"
        },
        {
            "id": "AC-002",
            "title": "Reject duplicate appointment",
            "given": "Patient already has appointment at same time",
            "when": "Patient attempts to book another appointment",
            "then": "API returns 409 Conflict with error message",
            "test_case": "test_duplicate_appointment_rejection"
        },
        {
            "id": "AC-003",
            "title": "Validate time constraint",
            "given": "Booking is for past date",
            "when": "API receives booking request",
            "then": "API returns 400 Bad Request with validation error",
            "test_case": "test_past_date_validation"
        },
        {
            "id": "AC-004",
            "title": "Process payment correctly",
            "given": "Appointment cost is calculated",
            "when": "Patient submits payment",
            "then": "Payment gateway is called and amount is deducted",
            "test_case": "test_payment_processing"
        }
    ]
}
```

---

## **STEP 5: AI GENERATE TEST CASES**

### 🧪 Test Case Generation

**Loại Test:**

### 1. Unit Tests
```python
def test_calculate_appointment_fee():
    """Test: Fee calculation for 30-min appointment"""
    # Arrange
    appointment_duration = 30  # minutes
    fee_per_minute = 1000  # VND
    
    # Act
    total_fee = calculate_fee(appointment_duration, fee_per_minute)
    
    # Assert
    assert total_fee == 30000
```

### 2. Integration Tests
```python
def test_appointment_booking_with_payment():
    """Test: Full booking flow with payment integration"""
    # Create appointment
    appointment = create_appointment(
        doctor_id=1,
        patient_id=1,
        time="2024-03-28 10:00"
    )
    
    # Process payment
    payment = process_payment(
        appointment_id=appointment.id,
        amount=appointment.fee
    )
    
    # Assert
    assert appointment.status == "confirmed"
    assert payment.status == "success"
```

### 3. E2E Tests
```python
def test_patient_books_appointment_e2e():
    """Test: Patient books appointment from UI to database"""
    # 1. User logs in
    login(email="patient@example.com", password="123456")
    
    # 2. Navigate to booking page
    click("Book Appointment")
    
    # 3. Select doctor & time
    select_doctor("Dr. Nguyen")
    select_time("2024-03-28 10:00")
    
    # 4. Confirm booking
    click("Confirm Booking")
    
    # 5. Verify in database
    appointment = get_appointment_from_db(patient_id=1)
    assert appointment.status == "confirmed"
```

**Kỹ Thuật Sử Dụng:**

```python
# Test Generation Algorithm
1. Extract test inputs from AC
2. Generate positive test cases (Happy Path)
3. Generate negative test cases (Edge Cases)
4. Generate boundary test cases
5. Generate performance test cases
6. Generate security test cases

# Test Coverage Calculation
coverage = (executed_statements / total_statements) * 100
target_coverage = 85-90%
```

**Ví Dụ Output:**

```json
{
    "task_id": "TASK-002",
    "test_suite": {
        "unit_tests": [
            {
                "id": "UT-001",
                "title": "Test appointment fee calculation",
                "test_framework": "pytest",
                "input": {"duration": 30, "rate": 1000},
                "expected_output": 30000,
                "priority": "P0"
            },
            {
                "id": "UT-002",
                "title": "Test invalid appointment validation",
                "input": {"date": "2020-01-01"},
                "expected_output": "ERROR_PAST_DATE",
                "priority": "P0"
            }
        ],
        "integration_tests": [
            {
                "id": "IT-001",
                "title": "Test booking with payment gateway",
                "components": ["API", "PaymentGateway", "Database"],
                "priority": "P0"
            }
        ],
        "e2e_tests": [
            {
                "id": "E2E-001",
                "title": "Patient books appointment complete flow",
                "steps": [
                    "Login",
                    "Navigate to booking",
                    "Select doctor and time",
                    "Confirm booking",
                    "Verify confirmation"
                ],
                "priority": "P0"
            }
        ]
    }
}
```

---

## **STEP 6: AI ESTIMATE EFFORT**

### 📊 Effort Estimation

**3 Phương Pháp Ước Tính:**

### 1. Story Points (Agile)
```
Story Points Scale: 1, 2, 3, 5, 8, 13, 21, 34

Ví dụ:
- 1-2 SP: Simple changes, bug fixes
- 3-5 SP: New features, moderate complexity  ← Thường dùng
- 8-13 SP: Complex features, integration
- 21+ SP: Quá phức tạp, cần chia nhỏ
```

### 2. Function Points (FP)
```
FP = (Sum of ILF, EIF, EI, EO, EQ) × VAF

Ví dụ:
- Appointment booking: 25 FP
- Effort = 25 FP × 2 hours/FP = 50 hours
```

### 3. Use Case Points (UCP)
```
UCP = UUCW × TCF × EF

Ví dụ:
- Appointment system: 45 UCP
- Effort = 45 UCP × 20 hours/UCP = 900 hours
```

**Kỹ Thuật Sử Dụng:**

```python
# AI-based Estimation
1. Historical Data Analysis
   - Compare with similar past tasks
   - Use team velocity
   
2. Complexity Scoring
   - Analyze technical complexity
   - Check integration points
   - Assess risk factors
   
3. Machine Learning
   - Trained on historical projects
   - Feature extraction
   - Predict effort with confidence interval

# Formula
estimated_hours = base_hours + complexity_factor + risk_factor
confidence_interval = estimated_hours ± (estimated_hours * uncertainty_percentage)
```

**Ví Dụ Output:**

```json
{
    "task_id": "TASK-002",
    "effort_estimation": {
        "story_points": 5,
        "function_points": 28,
        "estimated_hours": 40,
        "estimated_days": 5,
        "estimation_methods": {
            "story_points": {
                "value": 5,
                "reasoning": "Medium complexity API development with payment integration",
                "confidence": "85%"
            },
            "function_points": {
                "value": 28,
                "inputs": 4,
                "outputs": 3,
                "inquiries": 2,
                "files": 2,
                "interfaces": 1,
                "complexity_adjustment": 1.2
            }
        },
        "development_breakdown": {
            "design": 5,
            "development": 25,
            "testing": 8,
            "code_review": 2
        },
        "risk_factors": [
            {"name": "Payment gateway integration", "impact": "Medium", "mitigation": "Use mock API first"},
            {"name": "Database performance", "impact": "High", "mitigation": "Query optimization"}
        ],
        "schedule": {
            "start_date": "2024-03-21",
            "end_date": "2024-03-28",
            "critical_path": "Payment gateway testing"
        }
    }
}
```

---

## **STEP 7: SHOW PROJECT DASHBOARD**

### 📈 Project Dashboard & Analytics

**Dashboard Components:**

### 1. Project Overview
```
┌─────────────────────────────────────────────────┐
│ PROJECT: Healthcare Appointment System          │
├─────────────────────────────────────────────────┤
│ Total Requirements:        91                   │
│ Total User Stories:       182                   │
│ Total Tasks:              435                   │
│ Total Test Cases:         520                   │
│ Total Estimated Hours:   2,840 hours (355 days)│
│ Development Team Size:     15 people            │
│ Estimated Duration:        6-7 months           │
└─────────────────────────────────────────────────┘
```

### 2. Breakdown by Type
```
Task Types:
├─ Feature Implementation:     280 (64%)
├─ Bug Fixes:                   65 (15%)
├─ Technical Debt:              45 (10%)
├─ Documentation:               30 (7%)
└─ Infrastructure:              15 (4%)

Priority Distribution:
├─ P0 (Critical):              156 tasks
├─ P1 (High):                  182 tasks
├─ P2 (Medium):                 75 tasks
└─ P3 (Low):                    22 tasks
```

### 3. Timeline & Milestones
```
Sprint Planning:
├─ Sprint 1 (2 weeks):  US-001 to US-010  [180 SP]
├─ Sprint 2 (2 weeks):  US-011 to US-025  [165 SP]
├─ Sprint 3 (2 weeks):  US-026 to US-045  [185 SP]
├─ Sprint 4 (2 weeks):  US-046 to US-065  [170 SP]
└─ Sprint 5 (2 weeks):  US-066 to US-100  [180 SP]

Critical Path:
1. Authentication & Authorization (Sprint 1)
2. Patient/Doctor Management (Sprint 2)
3. Appointment Booking (Sprint 3)
4. Payment Integration (Sprint 4)
5. Reporting & Analytics (Sprint 5)
```

### 4. Risk Assessment
```
Risk Analysis:
┌──────────────────────────┬────────┬──────────────┐
│ Risk                     │ Impact │ Probability  │
├──────────────────────────┼────────┼──────────────┤
│ Payment gateway delay    │ High   │ Medium (40%) │
│ HIPAA compliance         │ High   │ Low (20%)    │
│ Database performance     │ Medium │ Medium (30%) │
│ Team availability        │ Medium │ Low (10%)    │
│ Requirement changes      │ High   │ High (60%)   │
└──────────────────────────┴────────┴──────────────┘

Risk Score: 6.8/10 (Medium-High Risk)
```

### 5. Quality Metrics
```
Code Quality Goals:
├─ Test Coverage:         > 85%
├─ Code Duplication:      < 5%
├─ Cyclomatic Complexity: < 10
├─ Maintainability Index: > 70
└─ Security Issues:       0 (Critical)

Expected Quality:
├─ Defect Density:        < 5 per 1000 LOC
├─ Bug Escape Rate:       < 2%
└─ Customer Satisfaction: > 4.5/5.0
```

### 6. Cost Estimation
```
Cost Breakdown (Assuming $100/hour):
├─ Development:         $180,000 (1,800 hours)
├─ Testing:              $65,000 (650 hours)
├─ Deployment:           $20,000 (200 hours)
├─ Documentation:        $15,000 (150 hours)
├─ Contingency (10%):    $28,000
└─ TOTAL:               $308,000

ROI Analysis:
├─ Annual savings (automation):  $500,000
├─ Payback period: 7-8 months
└─ 3-year ROI: 450%
```

**Kỹ Thuật Sử Dụng:**

```python
# Dashboard Data Processing
1. Aggregation
   - Sum all story points
   - Calculate team velocity
   - Group by priority/type
   
2. Analytics
   - Trend analysis (burndown chart)
   - Velocity prediction
   - Risk scoring
   
3. Visualization
   - Charts, graphs, tables
   - Real-time updates
   - Export reports (PDF, Excel)
```

**Ví Dụ Output - JSON Dashboard Data:**

```json
{
    "dashboard": {
        "project_summary": {
            "name": "Healthcare Appointment System",
            "total_requirements": 91,
            "total_user_stories": 182,
            "total_tasks": 435,
            "total_story_points": 1880,
            "estimated_hours": 2840,
            "estimated_months": 6.5
        },
        "timeline": {
            "start_date": "2024-03-21",
            "end_date": "2024-10-15",
            "sprints": 13,
            "sprint_duration_days": 14
        },
        "breakdown": {
            "by_type": {
                "Feature": {count: 280, percentage: 64},
                "Bug Fix": {count: 65, percentage: 15},
                "Tech Debt": {count: 45, percentage: 10},
                "Doc": {count: 30, percentage: 7},
                "Infra": {count: 15, percentage: 4}
            },
            "by_priority": {
                "P0": 156,
                "P1": 182,
                "P2": 75,
                "P3": 22
            }
        },
        "risks": [
            {
                "name": "Payment gateway integration",
                "impact": "High",
                "probability": "40%",
                "score": 8,
                "mitigation": "Start early, use mock API"
            }
        ],
        "quality_metrics": {
            "test_coverage_target": "85%",
            "defect_density_target": "5 per 1000 LOC",
            "bug_escape_rate_target": "2%"
        },
        "cost_estimation": {
            "total": 308000,
            "currency": "USD",
            "breakdown": {
                "development": 180000,
                "testing": 65000,
                "deployment": 20000,
                "documentation": 15000,
                "contingency": 28000
            }
        }
    }
}
```

---

## 🎯 Phần 3: Ví Dụ Thực Tế - Healthcare Requirement

### Input Requirement:
```
"Phải cho phép bệnh nhân đặt lịch hẹn khám bệnh trực tuyến
- Thời gian đặt lịch: trước 7 ngày
- Gửi SMS nhắc nhở 1 ngày trước
- Hỗ trợ thanh toán online (credit card, bank transfer)
- Hiển thị bác sĩ có sẵn
- Xác nhận booking qua email"
```

### Pipeline Output:

#### **STEP 1: Input Parsing**
```
✓ Extract text from PDF
✓ Identify 5 key requirements
✓ Categorize as: Functional
```

#### **STEP 2: Generate User Stories**
```
USER STORY 1 - Happy Path:
"As a Patient, I want to browse available doctors and book an appointment 
online, so that I can schedule a convenient time without calling clinic"

USER STORY 2 - Edge Cases:
"As a System, I want to validate booking constraints (7-day advance notice), 
so that only valid appointments are created"

USER STORY 3 - Notification:
"As a Patient, I want to receive SMS and email reminders, 
so that I don't miss my appointment"

USER STORY 4 - Payment:
"As a Patient, I want to pay for appointment online, 
so that I can complete booking without going to clinic"
```

#### **STEP 3: Generate Tasks**
```
For User Story 1:
  ├─ TASK: Design appointment scheduling database schema (2 SP)
  ├─ TASK: Implement doctor availability API (3 SP)
  ├─ TASK: Build appointment booking form UI (3 SP)
  ├─ TASK: Integrate email confirmation (2 SP)
  └─ TASK: Write unit tests (2 SP)

For User Story 2:
  ├─ TASK: Implement date validation (1 SP)
  ├─ TASK: Check doctor availability conflicts (2 SP)
  └─ TASK: Add error handling (1 SP)

For User Story 3:
  ├─ TASK: Integrate SMS gateway (3 SP)
  ├─ TASK: Implement reminder scheduler (2 SP)
  └─ TASK: Setup notification templates (1 SP)

For User Story 4:
  ├─ TASK: Integrate payment gateway (3 SP)
  ├─ TASK: Implement payment validation (2 SP)
  └─ TASK: Add transaction logging (1 SP)
```

#### **STEP 4: Generate Acceptance Criteria**
```
For TASK: Implement doctor availability API

AC-001: Return available doctors
  Given: Doctor schedule exists in system
  When: API endpoint GET /doctors/available is called
  Then: Return list of available doctors with time slots
  
AC-002: Validate doctor credentials
  Given: Doctor has valid license
  When: Doctor is checked in system
  Then: Doctor appears in available list
  
AC-003: Handle no availability
  Given: No doctors are available on requested date
  When: Availability check is performed
  Then: Return empty list with message "No available doctors"
```

#### **STEP 5: Generate Test Cases**
```
UNIT TESTS:
  ✓ test_calculate_appointment_fee()
  ✓ test_validate_future_date()
  ✓ test_validate_doctor_availability()
  ✓ test_validate_payment_amount()

INTEGRATION TESTS:
  ✓ test_booking_with_payment_flow()
  ✓ test_sms_notification_sending()
  ✓ test_email_confirmation_flow()

E2E TESTS:
  ✓ test_patient_booking_complete_flow()
  ✓ test_doctor_availability_update()
```

#### **STEP 6: Estimate Effort**
```
Total Story Points: 28 SP
Total Hours: 42 hours (6 days)
Team Size: 3 developers
Sprint Duration: 1 sprint

Breakdown:
├─ Design & Planning:      6 hours
├─ Frontend Development:   12 hours
├─ Backend Development:    18 hours
├─ Testing:                 4 hours
└─ Code Review:             2 hours
```

#### **STEP 7: Show Dashboard**
```
APPOINTMENT BOOKING FEATURE
├─ Tasks: 15
├─ Test Cases: 25
├─ Estimated Hours: 42
├─ Priority: P0 (Critical)
├─ Risk Level: Medium
├─ Timeline: 1 Sprint
└─ Team: 3 Developers
```

---

## 💡 Tóm Tắt

| Bước | Tên | Mục đích | Input | Output |
|------|-----|---------|-------|--------|
| 1 | Input Requirement | Parse file | TXT/MD/DOCX/PDF | Structured requirements |
| 2 | User Stories | Chuyển sang story format | Requirement text | "As a... I want... So that..." |
| 3 | Tasks | Chia thành technical tasks | User stories | Technical implementation tasks |
| 4 | Acceptance Criteria | Define verification | Tasks | BDD format (Given-When-Then) |
| 5 | Test Cases | Create tests | AC | Unit/Integration/E2E tests |
| 6 | Effort Estimation | Ước tính công suất | Tasks | Story points, Hours, Timeline |
| 7 | Dashboard | Tóm tắt project | All data | Timeline, Risk, Cost, Quality metrics |

---

## 🔧 Kỹ Thuật AI Sử Dụng

```
STEP 1: File parsing libraries
STEP 2: NLP (spaCy), Semantic analysis, ML models
STEP 3: Decomposition algorithms, Rule-based systems
STEP 4: BDD template generation, NLP for clarity
STEP 5: Test generation patterns, Coverage analysis
STEP 6: ML regression, Historical data, Complexity scoring
STEP 7: Data aggregation, Analytics, Visualization
```

---

## 📚 Kết Luận

**Workflow của bạn:**
1. ✅ INPUT REQUIREMENT (93 requirements)
2. ✅ AI GENERATE USER STORIES (186 stories, 2 per requirement)
3. ✅ AI GENERATE TASKS (465 tasks, ~2.5 per story)
4. ✅ AI GENERATE ACCEPTANCE CRITERIA (Each task has 3-5 AC)
5. ✅ AI GENERATE TEST CASES (Unit + Integration + E2E)
6. ✅ AI ESTIMATE EFFORT (Story points + Hours)
7. ✅ SHOW PROJECT DASHBOARD (Timeline, Risk, Cost)

**Kết quả:** Từ 91 requirements → **1,500+ actionable tasks** với đầy đủ documentation, testing plan, và effort estimation, sẵn sàng cho development team!

