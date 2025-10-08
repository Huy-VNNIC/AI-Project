# Software Requirement Analyzer API

## Mô hình và Phương pháp

API này sử dụng kết hợp nhiều mô hình máy học để phân tích yêu cầu phần mềm và ước lượng nỗ lực phát triển:

### Các mô hình được sử dụng:
- **Neural Network (nn_model.h5)**: Mô hình học sâu cho việc trích xuất đặc trưng từ yêu cầu
- **Random Forest**: Mô hình dự đoán nỗ lực dựa trên phương pháp COCOMO II mở rộng
- **Gradient Boosting**: Mô hình dự đoán nỗ lực thay thế
- **Decision Tree**: Mô hình phân tích đặc trưng
- **Linear Regression**: Mô hình cơ sở cho phân tích

### Phương pháp ước lượng:
- **weighted_average**: Kết hợp nhiều mô hình với trọng số khác nhau (mặc định)
- **function_points**: Ước lượng dựa trên điểm chức năng
- **lines_of_code**: Ước lượng dựa trên số dòng mã
- **use_case_points**: Ước lượng dựa trên điểm use case

## API Endpoints

### Endpoint: /api/estimate

**Method:** POST  
**Purpose:** Estimate development effort based on requirement text  

**Request Format:**
```json
{
  "text": "Your software requirement text here",
  "method": "weighted_average"
}
```

**Response Format:**
```json
{
  "effort_estimate": {
    "person_months": 12.5,
    "confidence": 0.75,
    "range": {
      "min": 10.2,
      "max": 15.8
    }
  },
  "analysis": {
    "complexity": "medium",
    "features": 8,
    "functional_points": 120
  }
}
```

### Endpoint: /api/upload-requirements

**Method:** POST  
**Purpose:** Upload a requirements document file for analysis  
**Content-Type:** multipart/form-data

**Request Format:**
- file: The requirements document file
- method: The estimation method (default: "weighted_average")

**Supported File Types:**
- .txt, .md: Plain text files
- .pdf: PDF documents
- .doc, .docx: Microsoft Word documents

**Response Format:**
Same as /api/estimate endpoint, plus document information:
```json
{
  "effort_estimate": {
    "person_months": 12.5,
    "confidence": 0.75,
    "range": {
      "min": 10.2,
      "max": 15.8
    }
  },
  "analysis": {
    "complexity": "medium",
    "features": 8,
    "functional_points": 120
  },
  "document": {
    "filename": "requirements.pdf",
    "file_type": ".pdf",
    "size_bytes": 245678,
    "text_length": 4500
  }
}
```

## Usage Examples

### Using curl

```bash
# Estimate using text
curl -X POST "https://your-domain/api/estimate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Develop hospital management system", "method": "weighted_average"}'

# Upload a document
curl -X POST "https://your-domain/api/upload-requirements" \
     -F "file=@path/to/requirements.pdf" \
     -F "method=weighted_average"
```

### Using Python

```python
import requests
import json

# Estimate using text
url = "https://your-domain/api/estimate"
payload = {
    "text": "Develop hospital management system",
    "method": "weighted_average"
}
response = requests.post(url, json=payload)
result = response.json()
print(json.dumps(result, indent=2))

# Upload a document
url = "https://your-domain/api/upload-requirements"
files = {"file": open("path/to/requirements.pdf", "rb")}
data = {"method": "weighted_average"}
response = requests.post(url, files=files, data=data)
result = response.json()
print(json.dumps(result, indent=2))
```