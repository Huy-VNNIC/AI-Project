# API Documentation Guide

## 📚 Tổng quan

API của bạn hiện có **3 phiên bản documentation** với đầy đủ các tính năng:

1. **Swagger UI** (`/docs`) - Interactive API documentation với khả năng test trực tiếp
2. **ReDoc** (`/redoc`) - Alternative documentation với giao diện đẹp hơn
3. **JSON Schema** (`/api/schemas`) - Machine-readable schema definitions

## 🔗 Access URLs

### Production Server: http://103.141.177.146:8000

| Documentation Type | URL | Mô tả |
|-------------------|-----|-------|
| **Swagger UI** | http://103.141.177.146:8000/docs | Interactive API testing interface |
| **ReDoc** | http://103.141.177.146:8000/redoc | Beautiful API documentation |
| **OpenAPI JSON** | http://103.141.177.146:8000/openapi.json | OpenAPI 3.1.0 specification |
| **All Schemas** | http://103.141.177.146:8000/api/schemas | All JSON schemas (21 models) |
| **Single Schema** | http://103.141.177.146:8000/api/schemas/{model_name} | Specific model schema |

---

## 1️⃣ Swagger UI (`/docs`)

### ✨ Tính năng

- **Interactive Testing**: Test API endpoints trực tiếp từ browser
- **Auto-generated**: Tự động từ code, luôn sync với API
- **Try it out**: Execute requests và xem response ngay lập tức
- **Authentication**: Hỗ trợ API keys, OAuth, JWT
- **Schema validation**: Validate input/output theo schemas

### 📖 Cách sử dụng

#### Bước 1: Mở Swagger UI
```
http://103.141.177.146:8000/docs
```

#### Bước 2: Browse API Endpoints

API được tổ chức theo **Tags** (categories):

- 🏥 **Health**: Health check endpoints
- 📊 **V1 Estimation**: COCOMO II, LOC, Multi-model estimation
- 🤖 **Task Generation**: AI-powered task generation
- 🔄 **V2 Requirements Engineering**: Requirements pipeline (refine, gap detection, slicing)
- 🔌 **Integration**: Jira, Trello integration
- 📋 **Schemas**: JSON Schema definitions

#### Bước 3: Test một endpoint

1. Click vào endpoint muốn test (ví dụ: `POST /api/task-generation/generate`)
2. Click **"Try it out"**
3. Điền parameters vào form:
   ```json
   {
     "text": "User muốn đăng nhập bằng email và password",
     "max_tasks": 50,
     "requirement_threshold": 0.5
   }
   ```
4. Click **"Execute"**
5. Xem response ở phía dưới:
   - **Response body**: JSON response data
   - **Response headers**: HTTP headers
   - **Response code**: 200, 400, 500, etc.
   - **Curl command**: Copy để dùng trong terminal

### 🎯 Ví dụ thực tế

#### Test V1 Estimation
```
1. Mở: POST /estimate
2. Try it out
3. Request body:
   {
     "text": "Xây dựng hệ thống quản lý khách sạn với 50 chức năng",
     "method": "weighted_average"
   }
4. Execute
5. Kết quả: effort estimation với person-months, duration, team size
```

#### Test V2 Task Generation
```
1. Mở: POST /api/v2/task-generation/generate-from-file
2. Try it out
3. Upload file: requirements.txt
4. Set parameters: max_tasks=100
5. Execute
6. Kết quả: 
   - Refined requirements (user stories + AC)
   - Gap detection
   - Story slicing
   - INVEST scores
```

### 📸 Screenshots chính

- **Endpoint list**: Danh sách tất cả endpoints theo tags
- **Request form**: Form để điền parameters
- **Response viewer**: JSON response với syntax highlighting
- **Schema browser**: Click vào schema để xem chi tiết

---

## 2️⃣ ReDoc (`/redoc`)

### ✨ Tính năng

- **Beautiful UI**: Giao diện đẹp, responsive, dễ đọc
- **Three-column layout**: Menu > Content > Examples
- **Deep linking**: Share links đến specific endpoints
- **Search**: Tìm kiếm endpoints và schemas
- **Code samples**: Curl, Python, JavaScript examples
- **Print-friendly**: In thành PDF documentation

### 📖 Cách sử dụng

#### Bước 1: Mở ReDoc
```
http://103.141.177.146:8000/redoc
```

#### Bước 2: Browse Documentation

**Left sidebar:**
- Navigation menu với tất cả endpoints
- Group theo tags
- Click để jump đến endpoint

**Main content:**
- Endpoint description
- Parameters table
- Request/Response schemas
- HTTP status codes
- Examples

**Right sidebar:**
- Code samples (curl, httpie, etc.)
- JSON request/response examples

#### Bước 3: Search
- Dùng search box ở góc trên
- Search theo endpoint path, method, description
- Instant results với highlighting

### 🎯 Use cases

- **Developer onboarding**: Đọc docs để hiểu API
- **Client integration**: Copy code samples để integrate
- **API specification**: Share với stakeholders
- **Print documentation**: Print hoặc export PDF

---

## 3️⃣ JSON Schema Endpoints (`/api/schemas`)

### ✨ Tính năng

- **Machine-readable**: JSON Schema format standard
- **All models**: 21 data models (V1, V2, Task Generation)
- **Validation**: Dùng để validate data
- **Code generation**: Generate TypeScript, Python classes
- **API testing**: Schema-based testing

### 📖 Available Schemas

#### V1 Estimation Models (3)
- `RequirementText`: Text input for estimation
- `TaskList`: Task list input
- `COCOMOParameters`: COCOMO II parameters

#### Task Generation Models (3)
- `TaskGenerationRequest`: Task generation request
- `TaskGenerationResponse`: Generated tasks output
- `TaskFeedback`: User feedback on tasks

#### V2 Requirements Engineering Models (10)
- `Requirement`: Raw requirement
- `RefinementOutput`: Refined requirement with user story + AC
- `AcceptanceCriterion`: Single AC in Given/When/Then
- `Gap`: Detected gap/issue
- `GapReport`: Complete gap analysis
- `UserStory`: User story with subtasks
- `Subtask`: Individual implementation task
- `Slice`: Story slice with rationale
- `SlicingOutput`: Complete slicing output
- `INVESTScore`: INVEST scoring metrics

#### Enums (5)
- `SeverityLevel`: Low, Medium, High, Critical
- `RequirementType`: functional, non_functional, constraint, assumption
- `GapType`: missing_actor, contradiction, ambiguity, etc.
- `SliceRationale`: workflow, data, risk, platform, role
- `TaskRole`: Backend, Frontend, QA, DevOps, Security

### 🔌 API Endpoints

#### Get all schemas
```bash
GET /api/schemas

Response:
{
  "openapi_version": "3.1.0",
  "info": {
    "title": "Software Effort Estimation API - Data Models",
    "version": "2.0.0"
  },
  "schemas": {
    "RequirementText": { ... },
    "RefinementOutput": { ... },
    ...
  },
  "schema_count": 21,
  "categories": {
    "v1_estimation": [...],
    "task_generation": [...],
    "v2_requirements": [...],
    ...
  }
}
```

#### Get specific schema
```bash
GET /api/schemas/RefinementOutput

Response:
{
  "model_name": "RefinementOutput",
  "schema": {
    "type": "object",
    "properties": {
      "requirement_id": {"type": "string"},
      "title": {"type": "string", "minLength": 5},
      "user_story": {"type": "string"},
      "acceptance_criteria": {
        "type": "array",
        "items": {"$ref": "#/definitions/AcceptanceCriterion"}
      },
      ...
    },
    "required": ["requirement_id", "title", "user_story", "acceptance_criteria"]
  }
}
```

### 🎯 Use Cases

#### 1. Validate Input Data (Python)
```python
import requests
import jsonschema

# Get schema
schema_response = requests.get("http://103.141.177.146:8000/api/schemas/TaskGenerationRequest")
schema = schema_response.json()["schema"]

# Validate data
data = {
    "text": "User wants to login",
    "max_tasks": 50
}

try:
    jsonschema.validate(instance=data, schema=schema)
    print("✅ Valid!")
except jsonschema.ValidationError as e:
    print(f"❌ Invalid: {e.message}")
```

#### 2. Generate TypeScript Types
```bash
# Install quicktype
npm install -g quicktype

# Generate TypeScript from schema
curl http://103.141.177.146:8000/api/schemas/RefinementOutput \
  | jq '.schema' \
  | quicktype --src-lang schema --lang typescript --out RefinementOutput.ts
```

Result:
```typescript
export interface RefinementOutput {
    requirement_id: string;
    title: string;
    user_story: string;
    acceptance_criteria: AcceptanceCriterion[];
    assumptions: string[];
    constraints: string[];
    non_functional_requirements: string[];
    changes_summary: string;
}

export interface AcceptanceCriterion {
    ac_id: string;
    given: string;
    when: string;
    then: string;
    priority: SeverityLevel;
}
```

#### 3. Generate Python Pydantic Models
```bash
# Install datamodel-code-generator
pip install datamodel-code-generator

# Generate Python from all schemas
curl http://103.141.177.146:8000/api/schemas \
  | jq '.schemas' \
  | datamodel-codegen --input-file-type jsonschema --output models.py
```

#### 4. API Testing with Schema Validation
```python
import requests
from jsonschema import validate

# Test endpoint với schema validation
response = requests.post(
    "http://103.141.177.146:8000/api/task-generation/generate",
    json={"text": "User wants to login", "max_tasks": 50}
)

# Get response schema
schema_resp = requests.get("http://103.141.177.146:8000/api/schemas/TaskGenerationResponse")
schema = schema_resp.json()["schema"]

# Validate response
validate(instance=response.json(), schema=schema)
print("✅ API response matches schema!")
```

#### 5. Generate Mock Data
```python
from hypothesis import given
from hypothesis_jsonschema import from_schema
import requests

# Get schema
schema_resp = requests.get("http://103.141.177.146:8000/api/schemas/TaskGenerationRequest")
schema = schema_resp.json()["schema"]

# Generate mock data
@given(from_schema(schema))
def test_with_mock_data(data):
    print(f"Mock data: {data}")
    # Use for testing, demos, etc.
```

#### 6. Form Generation (Frontend)
```javascript
// Fetch schema
const schema = await fetch('http://103.141.177.146:8000/api/schemas/TaskGenerationRequest')
  .then(r => r.json())
  .then(data => data.schema);

// Use react-jsonschema-form
import Form from "@rjsf/core";

function MyForm() {
  return (
    <Form 
      schema={schema}
      onSubmit={({formData}) => {
        // Submit to API
        fetch('http://103.141.177.146:8000/api/task-generation/generate', {
          method: 'POST',
          body: JSON.stringify(formData)
        });
      }}
    />
  );
}
```

---

## 🔄 So sánh 3 phiên bản

| Feature | Swagger UI | ReDoc | JSON Schema |
|---------|-----------|-------|-------------|
| **Interactive testing** | ✅ Yes | ❌ No | ❌ No |
| **Beautiful UI** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ N/A |
| **Code samples** | ✅ Curl only | ✅ Multiple langs | ❌ No |
| **Search** | ✅ Basic | ✅ Advanced | ❌ No |
| **Deep linking** | ✅ Yes | ✅ Yes | ✅ Yes (by model) |
| **Print-friendly** | ❌ No | ✅ Yes | ❌ No |
| **Machine-readable** | ✅ OpenAPI JSON | ✅ OpenAPI JSON | ✅ JSON Schema |
| **Validation** | ✅ In UI | ❌ No | ✅ Programmatic |
| **Code generation** | ❌ No | ❌ No | ✅ Yes |

### 🎯 Khi nào dùng gì?

**Swagger UI (`/docs`):**
- Khi cần **test API** ngay lập tức
- Developer đang **develop/debug**
- Demo API cho team
- Quick prototype testing

**ReDoc (`/redoc`):**
- Khi cần **đọc documentation**
- Share với stakeholders, clients
- Onboarding developers mới
- Print/export documentation
- Beautiful presentation

**JSON Schema (`/api/schemas`):**
- Khi cần **validate data** programmatically
- Generate code (TypeScript, Python, etc.)
- API testing automation
- Form generation
- Mock data generation
- Integration with tools (Postman, Insomnia)

---

## 🛠️ Integration Examples

### Postman Collection

1. Import OpenAPI spec vào Postman:
   ```
   File > Import > Link
   http://103.141.177.146:8000/openapi.json
   ```

2. Postman tự động tạo collection với tất cả endpoints

3. Test với schemas:
   - Postman có built-in schema validation
   - Copy schema từ `/api/schemas` vào Tests tab

### Insomnia

1. Import OpenAPI:
   ```
   Dashboard > Import/Export > From URL
   http://103.141.177.146:8000/openapi.json
   ```

2. Insomnia tạo workspace với all requests

### VS Code REST Client

Create `.http` file:
```http
### Get all schemas
GET http://103.141.177.146:8000/api/schemas

### Generate tasks
POST http://103.141.177.146:8000/api/task-generation/generate
Content-Type: application/json

{
  "text": "User wants to login with email and password",
  "max_tasks": 50
}

### Get specific schema
GET http://103.141.177.146:8000/api/schemas/RefinementOutput
```

---

## 📊 API Statistics

### Current Coverage

- **Total endpoints**: 30+
- **Total schemas**: 21
- **Categories**: 6 (Health, V1, Task Gen, V2, Integration, Schemas)
- **Documentation formats**: 3 (Swagger, ReDoc, JSON Schema)

### Endpoints by Category

| Category | Count | Examples |
|----------|-------|----------|
| Health | 2 | `/health`, `/api/health` |
| V1 Estimation | 6 | `/estimate`, `/estimate-from-file`, `/upload-requirements` |
| Task Generation | 4 | `/api/task-generation/generate`, `/api/task-generation/generate-from-file` |
| V2 Requirements | 5 | `/api/v2/task-generation/*` (refine, detect-gaps, slice) |
| Integration | 4 | Jira, Trello import endpoints |
| Schemas | 2 | `/api/schemas`, `/api/schemas/{model_name}` |

---

## 🚀 Best Practices

### For API Consumers

1. **Start with Swagger UI** để hiểu API flow
2. **Read ReDoc** để hiểu chi tiết schemas và business logic
3. **Use JSON Schema** để validate và generate code
4. **Cache schemas** - chỉ fetch 1 lần, reuse trong app
5. **Validate inputs** trước khi call API để avoid errors

### For API Developers

1. **Keep schemas in sync** - Pydantic models tự động sync
2. **Add descriptions** - Docstrings become API docs
3. **Use tags** - Organize endpoints logically
4. **Version APIs** - Use `/api/v1/`, `/api/v2/` prefixes
5. **Test with Swagger** - Manual testing before automation

---

## 📞 Support

### Documentation URLs
- **Swagger UI**: http://103.141.177.146:8000/docs
- **ReDoc**: http://103.141.177.146:8000/redoc
- **All Schemas**: http://103.141.177.146:8000/api/schemas

### Quick Commands

```bash
# Test health
curl http://103.141.177.146:8000/health

# Get all schemas
curl http://103.141.177.146:8000/api/schemas | jq

# Get specific schema
curl http://103.141.177.146:8000/api/schemas/RefinementOutput | jq

# Download OpenAPI spec
curl http://103.141.177.146:8000/openapi.json -o openapi.json

# Test endpoint
curl -X POST http://103.141.177.146:8000/api/task-generation/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "User wants to login", "max_tasks": 50}'
```

---

**Last Updated**: 2026-01-29  
**API Version**: 2.0.0  
**Server**: http://103.141.177.146:8000
