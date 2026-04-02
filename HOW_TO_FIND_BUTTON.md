# 📌 Hướng Dẫn Tìm Nút "Generate Test Cases"

## 🌐 **URL Web UI:**
```
http://localhost:8000/task-generation
```

## 🖼️ **Layout Web Page:**

```
┌─────────────────────────────────────────────────────────────────┐
│                   ⚙️ AI Task & Test Generator                   │
│                                                                 │
├────────────────────────────┬────────────────────────────────────┤
│                            │                                    │
│  📝 REQUIREMENTS INPUT     │  📋 GENERATED TEST CASES           │
│  ─────────────────────     │  ──────────────────────────        │
│                            │                                    │
│  [Textarea for writing]    │  [Test cases list showing]         │
│  requirements here         │  - Test ID                        │
│                            │  - Category (Security, etc)       │
│  Max Tasks:                │  - Description                    │
│  [50____________]          │  - Confidence                     │
│                            │  - Effort                        │
│  Detection Threshold:      │                                    │
│  [0.5___________]          │  Filter Tabs:                     │
│                            │  [All] [Security] [Perf] [Func]   │
│  ⚡ GENERATE TEST CASES ← ╱  │                                    │
│  [Blue Button Here]        │  Sample test case detail panel    │
│                            │                                    │
└────────────────────────────┴────────────────────────────────────┘
```

## ✨ **Nút "Generate Test Cases" Có Ở Đâu?**

**BÊN TRÁI (Input Panel):**
```
Dòng cuối của "Requirements Input" section
↓
┌─────────────────────────────────────────┐
│ Requirements Input                      │
│                                         │
│ [Textarea with your requirements]      │
│                                         │
│ Max Tasks: [50_____]                    │
│ Detection Threshold: [0.5____]          │
│                                         │
│ ⚡ GENERATE TEST CASES  ← ← ← ← ← NAY  │
│ [Nút xanh to full-width]               │
└─────────────────────────────────────────┘
```

## 🎨 **Chi Tiết Nút Button:**
- **Tên:** "⚡ Generate Test Cases"
- **Màu sắc:** Xanh dương (Primary color)
- **Chiều rộng:** Full width (100%)
- **Icon:** Lightning bolt ⚡
- **Vị trí:** Bên dưới input fields
- **Click:** Kích hoạt JavaScript `generateTestCases()` function

## 📱 **Các Bước Sử Dụng:**

1. **Truy cập URL:**
   ```
   http://localhost:8000/task-generation
   ```

2. **Nhập Requirements** vào textarea bên trái:
   ```
   The system shall allow users to login with email and password.
   The application must prevent SQL injection attacks.
   Users should be able to reset their password via email link.
   The system should support two-factor authentication.
   The platform must encrypt all sensitive user data at rest.
   ```

3. **Điều chỉnh Settings (Optional):**
   - Max Tasks: 50 (hoặc số tùy thích)
   - Detection Threshold: 0.5 (hoặc độ tin cậy tùy ý)

4. **Click Nút "⚡ GENERATE TEST CASES"** (Xanh dương to ở dưới)

5. **Chờ kết quả** - Bên phải sẽ hiển thị:
   - 📊 Statistics (Total, by Category, Avg Effort, Avg Confidence)
   - 🧪 Generated Test Cases (cards)
   - 🏷️ Filter buttons (All, Security, Performance, Functional)

6. **Click vào Test Case bất kỳ** để xem chi tiết ở side panel

---

## ⚠️ **Nếu Vẫn Chưa Thấy Nút:**

### **Cách 1: Hard Refresh Browser**
```
Ctrl + Shift + R  (Windows/Linux)
Cmd + Shift + R   (Mac)
```

### **Cách 2: Check Console**
- Mở DevTools: F12
- Vào tab "Console"
- Xem có error gì không

### **Cách 3: Check API Status**
```bash
python3 << 'EOF'
import urllib.request
import json

try:
    response = urllib.request.urlopen("http://localhost:8000/health")
    print("✅ API Running")
    
    # Test endpoint
    url2 = "http://localhost:8000/task-generation"
    response2 = urllib.request.urlopen(url2)
    html = response2.read().decode('utf-8')
    
    if "Generate Test Cases" in html:
        print("✅ Nút 'Generate Test Cases' có trong HTML")
    else:
        print("❌ Nút 'Generate Test Cases' KHÔNG có trong HTML")
        
except Exception as e:
    print(f"❌ API Error: {e}")
EOF
```

### **Cách 4: Xem Source HTML**
- Right-click → View Page Source
- Tìm "Generate Test Cases"
- Nếu có thì là CSS/JavaScript issue

---

## 🎯 **HTML Code của Nút:**

```html
<button class="btn btn-primary" onclick="generateTestCases()">
    <i class="bi bi-lightning-fill"></i> Generate Test Cases
</button>
```

**CSS Classes:**
- `.btn` - Button styling
- `.btn-primary` - Xanh dương color
- `onclick="generateTestCases()"` - Gọi JavaScript function

**JavaScript Function (trong file):**
```javascript
async function generateTestCases() {
    // Parse requirements
    // Call API: /api/v2/test-generation/generate-test-cases
    // Display results
}
```

---

## 🚀 **Quick Test URL:**

Nếu là localhost, hãy thử mở menu:
1. http://localhost:8000/ (Home page)
2. http://localhost:8000/task-generation (Test Generation page)
3. http://localhost:8000/docs (API Documentation)

---

**Nút "Generate Test Cases" phải có ở góc trái-dưới cùng input panel! 🎉**

Nếu vẫn không thấy, hãy báo lại!
