# Hướng Dẫn Test Chức Năng Task Generation

## 🚀 Cách 1: Test Qua Web UI (Dễ Nhất)

### Bước 1: Mở trình duyệt
API đang chạy tại: **http://localhost:8000**

Có 2 trang để test:
1. **Trang chính**: http://localhost:8000
2. **Trang Task Generation**: http://localhost:8000/task-generation ⭐ (Dùng trang này!)

### Bước 2: Nhập Requirements

#### Cách 2a: Dùng Quick Examples (Nhanh nhất)
1. Kéo xuống phần "Quick Examples" bên trái
2. Click vào một trong các nút:
   - 🛒 **E-commerce System**
   - 🔒 **Authentication Module** 
   - ❤️ **Healthcare App**

3. Văn bản mẫu sẽ tự động điền vào ô text
4. Click nút **"Generate Tasks"** màu xanh

#### Cách 2b: Nhập Text Tự Do
1. Trong ô "Requirements Document", nhập các yêu cầu (mỗi dòng 1 requirement):

```
The system must allow users to login with email and password.
The application shall send verification emails upon registration.
Users should be able to reset their password via email link.
The system shall support two-factor authentication.
The platform must encrypt all sensitive user data at rest.
```

2. Click **"Generate Tasks"**

### Bước 3: Xem Kết Quả

Sau vài giây, bạn sẽ thấy:

**Phần Summary (Trên cùng):**
- Tổng số tasks đã tạo
- Thời gian xử lý (processing time)
- Nút Export JSON/CSV

**Phần Tasks (Danh sách):**
Mỗi task hiển thị dạng card với:
- ✅ **Title**: Tên task (vd: "Implement user login authentication")
- 🏷️ **Type**: functional, security, performance, interface, data
- ⚡ **Priority**: high, medium, low
- 🏢 **Domain**: authentication, payment, healthcare, v.v.
- 📊 **Story Points**: 1-13

**Click vào header của card** để mở rộng và xem:
- **User Story**: "As a [role], I want to [action], so that [benefit]"
- **Description**: Mô tả chi tiết
- **Acceptance Criteria**: 3-6 điều kiện chấp nhận

### Bước 4: Thử Các Chức Năng

#### Filter Tasks
Phần "Filter" phía trên danh sách:
- Click **All** - Hiện tất cả
- Click **Functional** - Chỉ hiện functional requirements
- Click **Security** - Chỉ hiện security requirements
- Tương tự cho Performance, Interface

#### Export Results
- Click **JSON** - Download file tasks.json
- Click **CSV** - Download file tasks.csv (mở bằng Excel)

#### Copy Task
Mỗi task có 3 nút:
- 👁️ **View Details** - Xem modal chi tiết
- 📋 **Copy** - Copy task ra clipboard
- ⬇️ **Export** - Export task đó thành file JSON

---

## 🧪 Cách 2: Test Qua API (Nâng Cao)

### Test 1: Generate từ Text

```bash
curl -X POST "http://localhost:8000/api/task-generation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The system must allow users to login with email and password. The application shall send password reset emails.",
    "max_tasks": 50,
    "requirement_threshold": 0.5
  }'
```

**Kết quả mong đợi:**
```json
{
  "tasks": [
    {
      "title": "Implement user login authentication",
      "description": "The system needs to implement...",
      "type": "security",
      "priority": "high",
      "domain": "authentication",
      "role": "user",
      "story_points": 5,
      "acceptance_criteria": [
        "User can enter email and password",
        "System validates credentials",
        "..."
      ]
    }
  ],
  "total_sentences": 2,
  "requirements_detected": 2,
  "processing_time": 0.34
}
```

### Test 2: Check Status

```bash
curl http://localhost:8000/api/task-generation/status
```

**Kết quả mong đợi:**
```json
{
  "available": true,
  "mode": "model",
  "generator_class": "ModelBasedTaskGenerator",
  "message": "Task generation ready (mode: model)"
}
```

### Test 3: Upload File

Tạo file test `requirements.txt`:
```bash
echo "The system must allow users to login with email and password.
The application shall send verification emails upon registration.
Users should be able to reset their password via email link." > /tmp/requirements.txt
```

Upload và generate:
```bash
curl -X POST "http://localhost:8000/api/task-generation/generate-from-file" \
  -F "file=@/tmp/requirements.txt" \
  -F "max_tasks=50"
```

---

## 📊 Cách 3: Test với Python Script

Tạo file `test_task_gen_demo.py`:

```python
import requests
import json

# API endpoint
API_URL = "http://localhost:8000/api/task-generation/generate"

# Requirements text
requirements = """
The system must verify user identity through two-factor authentication.
Users should be able to reset their password via email link.
The application shall log all authentication attempts for security audit.
The platform must encrypt all sensitive user data at rest and in transit.
"""

# Generate tasks
response = requests.post(
    API_URL,
    json={
        "text": requirements,
        "max_tasks": 50,
        "requirement_threshold": 0.5
    }
)

result = response.json()

# Print results
print(f"✅ Generated {len(result['tasks'])} tasks")
print(f"⏱️  Processing time: {result['processing_time']:.2f}s")
print(f"📊 Requirements detected: {result['requirements_detected']}/{result['total_sentences']}")
print("\n" + "="*80)

for i, task in enumerate(result['tasks'], 1):
    print(f"\n{i}. {task['title']}")
    print(f"   Type: {task['type']} | Priority: {task['priority']} | Points: {task['story_points']}")
    print(f"   Description: {task['description'][:100]}...")
    print(f"   Acceptance Criteria ({len(task['acceptance_criteria'])} items):")
    for j, ac in enumerate(task['acceptance_criteria'][:3], 1):
        print(f"      {j}. {ac}")
```

Chạy:
```bash
cd /home/dtu/AI-Project/AI-Project
python test_task_gen_demo.py
```

---

## ✅ Test Cases Nên Thử

### Test Case 1: Basic Functional Requirements
```
The system must allow users to browse products by category.
Users should be able to add products to shopping cart.
The application shall calculate total price including taxes.
```

**Kỳ vọng:**
- 3 tasks được tạo
- Type: functional
- Priority: medium
- Domain: ecommerce

### Test Case 2: Security Requirements
```
The system must implement user authentication with email and password.
The application shall enforce strong password requirements.
The platform must implement two-factor authentication.
Sessions should expire after 30 minutes of inactivity.
```

**Kỳ vọng:**
- 4 tasks được tạo
- Type: security
- Priority: high
- Có acceptance criteria về authentication

### Test Case 3: Mixed Requirements
```
The system must allow users to login with email and password.
The application should display dashboard with charts and graphs.
The platform must encrypt all data at rest.
Users can export reports to PDF and Excel formats.
```

**Kỳ vọng:**
- 4 tasks với types khác nhau: security, interface, security, data
- Priorities khác nhau
- Story points từ 3-8

### Test Case 4: Edge Cases
```
This is a note about the system architecture.
Users should be able to do something.
The platform.
```

**Kỳ vọng:**
- Chỉ 1 task (câu 2) được tạo
- Câu 1: không phải requirement (filtered out)
- Câu 3: không đủ thông tin (filtered out)

---

## 🐛 Troubleshooting

### Lỗi: "No tasks generated"
**Nguyên nhân:**
- Requirements không rõ ràng
- Threshold quá cao (0.5)

**Giải pháp:**
- Viết requirements rõ ràng hơn với "must", "shall", "should"
- Giảm threshold xuống 0.3:
```json
{
  "text": "...",
  "requirement_threshold": 0.3
}
```

### Lỗi: "Generic titles" (60%)
**Hiện tượng:** Titles như "Build user login capability"

**Đây là known issue:**
- Đang trong roadmap để fix
- Không ảnh hưởng chức năng chính
- Target: giảm xuống 25-30%

### Lỗi: Models not loading
**Check:**
```bash
ls requirement_analyzer/models/task_gen/models/*.joblib
```

**Phải thấy 8 files:**
- requirement_detector_model.joblib
- requirement_detector_vectorizer.joblib
- type_model.joblib
- type_vectorizer.joblib
- priority_model.joblib
- priority_vectorizer.joblib
- domain_model.joblib
- domain_vectorizer.joblib

---

## 📈 Đánh Giá Chất Lượng

Sau khi generate tasks, check các điểm sau:

### ✅ Good Quality Indicators
- Titles cụ thể (không có "capability", "functionality", "feature")
- Descriptions rõ ràng, không generic
- Acceptance criteria testable (có thể test được)
- Story points hợp lý (3-8 cho functional, 2-5 cho bug fixes)
- Type/domain/priority chính xác

### ⚠️ Quality Issues
- Generic titles (chứa "capability", "feature")
- Acceptance criteria trùng lặp
- Story points quá cao/thấp
- Type phân loại sai

---

## 🎯 Demo Cho Presentation

**Script 5 phút:**

1. **Mở trang** (10s)
   - http://localhost:8000/task-generation
   
2. **Load example** (10s)
   - Click "Authentication Module"
   
3. **Generate** (5s)
   - Click "Generate Tasks"
   - Đợi processing
   
4. **Show results** (60s)
   - Scroll qua các tasks
   - Click mở 2-3 cards
   - Highlight acceptance criteria
   
5. **Filter** (20s)
   - Click "Security" filter
   - Show chỉ security tasks
   
6. **Export** (10s)
   - Click "Export JSON"
   - Show file downloaded
   
7. **Explain architecture** (3 phút)
   - Show là ML models (không phải LLM)
   - 5 bước: Segment → Detect → Classify → Generate → Postprocess
   - Pattern-based NLG (spaCy + rules)

---

## 📝 Checklist Before Demo

- [ ] API đang chạy: `curl http://localhost:8000/health`
- [ ] Models loaded: Check logs không có ERROR
- [ ] Web UI accessible: Mở http://localhost:8000/task-generation
- [ ] Quick examples work: Test 3 examples
- [ ] Export functions work: Test JSON và CSV
- [ ] Filters work: Test All, Functional, Security
- [ ] Prepare talking points về Production Candidate status

---

**Chúc bạn test thành công! 🎉**

Nếu gặp vấn đề gì, check logs hoặc hỏi thêm nhé!
