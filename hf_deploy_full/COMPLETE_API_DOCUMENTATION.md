# 🚀 Software Effort Estimation API - Complete Documentation

## 📋 Overview

Complete REST API for software effort estimation with multiple models including COCOMO II, Function Points, and ML-based estimation. Now deployed on HuggingFace Spaces with FastAPI backend.

**🔗 Live API URL:** https://nhathuyyne-software-effort-estimation-full-api.hf.space

**📖 Interactive Documentation:** https://nhathuyyne-software-effort-estimation-full-api.hf.space/docs

**📋 ReDoc Documentation:** https://nhathuyyne-software-effort-estimation-full-api.hf.space/redoc

---

## 🔧 Available Endpoints

### 1. **POST /analyze** - Requirement Analysis
Analyze software requirements and extract project parameters.

**Request Schema:**
```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "Software requirements text to analyze",
      "example": "Create a web application with user authentication, data visualization, and reporting features"
    },
    "project_name": {
      "type": "string",
      "description": "Optional project name",
      "example": "Web Dashboard",
      "default": "Unnamed Project"
    }
  },
  "required": ["text"]
}
```

**Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "project_name": {"type": "string"},
    "analysis": {
      "type": "object",
      "properties": {
        "analysis": {"type": "string"}
      }
    },
    "function_points": {
      "type": "object",
      "properties": {
        "function_points": {"type": "number"},
        "complexity": {"type": "string"}
      }
    },
    "status": {"type": "string", "enum": ["success", "error"]}
  }
}
```

**Example Request:**
```bash
curl -X POST "https://nhathuyyne-software-effort-estimation-full-api.hf.space/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create a web application with user authentication, data visualization, and reporting features",
    "project_name": "Web Dashboard"
  }'
```

**Example Response:**
```json
{
  "project_name": "Web Dashboard",
  "analysis": {
    "analysis": "Requirements analysis completed"
  },
  "function_points": {
    "function_points": 45,
    "complexity": "Medium"
  },
  "status": "success"
}
```

---

### 2. **POST /upload-requirements** - Document Upload
Upload and analyze requirement documents (PDF, DOCX, TXT).

**Request Schema:**
```json
{
  "type": "object",
  "properties": {
    "file": {
      "type": "string",
      "format": "binary",
      "description": "Requirement document file (PDF, DOCX, TXT)"
    }
  },
  "required": ["file"]
}
```

**Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "filename": {"type": "string"},
    "file_type": {"type": "string"},
    "analysis": {"type": "object"},
    "function_points": {"type": "object"},
    "status": {"type": "string"}
  }
}
```

**Example Request:**
```bash
curl -X POST "https://nhathuyyne-software-effort-estimation-full-api.hf.space/upload-requirements" \
  -F "file=@requirements.txt"
```

---

### 3. **POST /estimate-from-tasks** - Task-Based Estimation
Estimate effort from list of tasks using ML models.

**Request Schema:**
```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of project tasks",
      "example": ["User authentication", "Database design", "UI development", "Testing"]
    },
    "project_type": {
      "type": "string",
      "enum": ["web", "mobile", "desktop", "api"],
      "description": "Type of project",
      "default": "web"
    },
    "complexity": {
      "type": "string",
      "enum": ["low", "medium", "high"],
      "description": "Project complexity level",
      "default": "medium"
    }
  },
  "required": ["tasks"]
}
```

**Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "tasks": {"type": "array", "items": {"type": "string"}},
    "task_count": {"type": "number"},
    "project_type": {"type": "string"},
    "complexity": {"type": "string"},
    "estimated_hours": {"type": "number"},
    "estimated_days": {"type": "number"},
    "estimated_weeks": {"type": "number"},
    "status": {"type": "string"}
  }
}
```

**Example Request:**
```bash
curl -X POST "https://nhathuyyne-software-effort-estimation-full-api.hf.space/estimate-from-tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": ["User authentication", "Database design", "UI development", "API integration", "Testing"],
    "project_type": "web",
    "complexity": "medium"
  }'
```

**Example Response:**
```json
{
  "tasks": ["User authentication", "Database design", "UI development", "API integration", "Testing"],
  "task_count": 5,
  "project_type": "web",
  "complexity": "medium",
  "estimated_hours": 40.0,
  "estimated_days": 5.0,
  "estimated_weeks": 1.0,
  "status": "success"
}
```

---

### 4. **POST /estimate-cocomo** - COCOMO II Estimation
Estimate effort using COCOMO II model with scale factors and effort multipliers.

**Request Schema:**
```json
{
  "type": "object",
  "properties": {
    "kloc": {
      "type": "number",
      "description": "Thousands of Lines of Code",
      "example": 10.5,
      "minimum": 0.1
    },
    "scale_factors": {
      "type": "object",
      "description": "COCOMO II Scale Factors (1-6 scale)",
      "properties": {
        "precedentedness": {"type": "number", "minimum": 1.0, "maximum": 6.0, "default": 3.72},
        "development_flexibility": {"type": "number", "minimum": 1.0, "maximum": 6.0, "default": 3.04},
        "architecture_risk_resolution": {"type": "number", "minimum": 1.0, "maximum": 6.0, "default": 4.24},
        "team_cohesion": {"type": "number", "minimum": 1.0, "maximum": 6.0, "default": 3.29},
        "process_maturity": {"type": "number", "minimum": 1.0, "maximum": 6.0, "default": 4.68}
      }
    },
    "effort_multipliers": {
      "type": "object",
      "description": "COCOMO II Effort Multipliers (0.5-2.0 scale)",
      "properties": {
        "required_software_reliability": {"type": "number", "default": 1.0},
        "database_size": {"type": "number", "default": 1.0},
        "product_complexity": {"type": "number", "default": 1.0},
        "required_reusability": {"type": "number", "default": 1.0},
        "documentation_match_to_lifecycle": {"type": "number", "default": 1.0},
        "execution_time_constraint": {"type": "number", "default": 1.0},
        "main_storage_constraint": {"type": "number", "default": 1.0},
        "platform_volatility": {"type": "number", "default": 1.0},
        "analyst_capability": {"type": "number", "default": 1.0},
        "programmer_capability": {"type": "number", "default": 1.0},
        "application_experience": {"type": "number", "default": 1.0},
        "platform_experience": {"type": "number", "default": 1.0},
        "language_and_toolset_experience": {"type": "number", "default": 1.0},
        "personnel_continuity": {"type": "number", "default": 1.0},
        "use_of_software_tools": {"type": "number", "default": 1.0},
        "multisite_development": {"type": "number", "default": 1.0},
        "required_development_schedule": {"type": "number", "default": 1.0}
      }
    }
  },
  "required": ["kloc"]
}
```

**Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "kloc": {"type": "number"},
    "scale_factors": {"type": "object"},
    "effort_multipliers": {"type": "object"},
    "estimation": {
      "type": "object",
      "properties": {
        "effort_person_months": {"type": "number"},
        "development_time_months": {"type": "number"},
        "people_required": {"type": "number"}
      }
    },
    "status": {"type": "string"},
    "note": {"type": "string"}
  }
}
```

**Example Request - Basic:**
```bash
curl -X POST "https://nhathuyyne-software-effort-estimation-full-api.hf.space/estimate-cocomo" \
  -H "Content-Type: application/json" \
  -d '{"kloc": 10.5}'
```

**Example Request - Advanced:**
```bash
curl -X POST "https://nhathuyyne-software-effort-estimation-full-api.hf.space/estimate-cocomo" \
  -H "Content-Type: application/json" \
  -d '{
    "kloc": 15.3,
    "scale_factors": {
      "precedentedness": 2.5,
      "development_flexibility": 4.0,
      "architecture_risk_resolution": 3.5,
      "team_cohesion": 4.2,
      "process_maturity": 3.8
    },
    "effort_multipliers": {
      "required_software_reliability": 1.1,
      "product_complexity": 1.3,
      "analyst_capability": 0.9,
      "programmer_capability": 0.85,
      "use_of_software_tools": 0.9
    }
  }'
```

**Example Response:**
```json
{
  "kloc": 15.3,
  "scale_factors": {
    "precedentedness": 2.5,
    "development_flexibility": 4.0,
    "architecture_risk_resolution": 3.5,
    "team_cohesion": 4.2,
    "process_maturity": 3.8
  },
  "effort_multipliers": {
    "required_software_reliability": 1.1,
    "product_complexity": 1.3,
    "analyst_capability": 0.9,
    "programmer_capability": 0.85,
    "use_of_software_tools": 0.9
  },
  "estimation": {
    "effort_person_months": 45.0,
    "development_time_months": 8.5,
    "people_required": 5.3
  },
  "status": "success"
}
```

---

### 5. **GET /health** - Health Check
Simple health check endpoint.

**Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "status": {"type": "string", "enum": ["healthy", "unhealthy"]},
    "message": {"type": "string"}
  }
}
```

**Example Request:**
```bash
curl "https://nhathuyyne-software-effort-estimation-full-api.hf.space/health"
```

**Example Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

---

## 🎯 Dynamic Image Specification Documentation

### COCOMO II Scale Factors (1-6 Scale)

| Factor | Very Low (1.0) | Low (2.0) | Nominal (3.0) | High (4.0) | Very High (5.0) | Extra High (6.0) |
|--------|----------------|-----------|---------------|------------|----------------|------------------|
| **Precedentedness** | Unprecedented | Largely unprecedented | Somewhat unprecedented | Generally familiar | Largely familiar | Highly familiar |
| **Development Flexibility** | Rigorous | Occasional relaxation | Some relaxation | General conformity | Some conformity | General goals |
| **Architecture/Risk Resolution** | Little (20%) | Some (40%) | Often (60%) | Generally (75%) | Mostly (90%) | Full (100%) |
| **Team Cohesion** | Very difficult | Some difficult | Basically cooperative | Largely cooperative | Highly cooperative | Seamless |
| **Process Maturity** | Level 1 Lower | Level 1 Upper | Level 2 | Level 3 | Level 4 | Level 5 |

### COCOMO II Effort Multipliers (0.5-2.0 Scale)

#### Product Factors
| Factor | Very Low | Low | Nominal | High | Very High | Extra High |
|--------|----------|-----|---------|------|-----------|------------|
| **Required Software Reliability** | 0.75 | 0.88 | 1.00 | 1.15 | 1.40 | - |
| **Database Size** | - | 0.93 | 1.00 | 1.05 | 1.17 | - |
| **Product Complexity** | 0.70 | 0.85 | 1.00 | 1.15 | 1.30 | 1.65 |
| **Required Reusability** | - | 0.91 | 1.00 | 1.14 | 1.29 | - |
| **Documentation Match to Lifecycle** | 0.89 | 0.95 | 1.00 | 1.06 | 1.13 | - |

#### Computer Factors
| Factor | Very Low | Low | Nominal | High | Very High | Extra High |
|--------|----------|-----|---------|------|-----------|------------|
| **Execution Time Constraint** | - | - | 1.00 | 1.11 | 1.30 | 1.66 |
| **Main Storage Constraint** | - | - | 1.00 | 1.06 | 1.21 | 1.57 |
| **Platform Volatility** | - | 0.87 | 1.00 | 1.15 | 1.30 | - |

#### Personnel Factors
| Factor | Very Low | Low | Nominal | High | Very High | Extra High |
|--------|----------|-----|---------|------|-----------|------------|
| **Analyst Capability** | 1.46 | 1.19 | 1.00 | 0.85 | 0.71 | - |
| **Programmer Capability** | 1.34 | 1.15 | 1.00 | 0.88 | 0.76 | - |
| **Application Experience** | 1.22 | 1.10 | 1.00 | 0.90 | 0.81 | - |
| **Platform Experience** | 1.19 | 1.09 | 1.00 | 0.91 | 0.85 | - |
| **Language and Toolset Experience** | 1.20 | 1.09 | 1.00 | 0.91 | 0.84 | - |
| **Personnel Continuity** | 1.29 | 1.12 | 1.00 | 0.90 | 0.81 | - |

#### Project Factors
| Factor | Very Low | Low | Nominal | High | Very High | Extra High |
|--------|----------|-----|---------|------|-----------|------------|
| **Use of Software Tools** | 1.17 | 1.09 | 1.00 | 0.90 | 0.78 | - |
| **Multisite Development** | 1.22 | 1.09 | 1.00 | 0.93 | 0.86 | 0.80 |
| **Required Development Schedule** | 1.43 | 1.14 | 1.00 | 1.00 | 1.00 | - |

---

## 🔄 Complete Workflow Examples

### Example 1: Full Project Analysis Workflow
```bash
# Step 1: Analyze requirements
curl -X POST "https://nhathuyyne-software-effort-estimation-full-api.hf.space/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Build an e-commerce platform with user management, product catalog, shopping cart, payment processing, order management, and admin dashboard",
    "project_name": "E-commerce Platform"
  }'

# Step 2: Task-based estimation
curl -X POST "https://nhathuyyne-software-effort-estimation-full-api.hf.space/estimate-from-tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      "User registration and authentication",
      "Product catalog management",
      "Shopping cart functionality",
      "Payment gateway integration",
      "Order processing system",
      "Admin dashboard",
      "Database design",
      "API development",
      "Frontend development",
      "Testing and deployment"
    ],
    "project_type": "web",
    "complexity": "high"
  }'

# Step 3: COCOMO II estimation (assuming 25 KLOC)
curl -X POST "https://nhathuyyne-software-effort-estimation-full-api.hf.space/estimate-cocomo" \
  -H "Content-Type: application/json" \
  -d '{
    "kloc": 25.0,
    "scale_factors": {
      "precedentedness": 3.0,
      "development_flexibility": 3.5,
      "architecture_risk_resolution": 4.0,
      "team_cohesion": 4.5,
      "process_maturity": 3.5
    },
    "effort_multipliers": {
      "required_software_reliability": 1.15,
      "database_size": 1.05,
      "product_complexity": 1.30,
      "analyst_capability": 0.85,
      "programmer_capability": 0.88,
      "application_experience": 0.90,
      "use_of_software_tools": 0.90
    }
  }'
```

---

## 🛠️ Error Handling

All endpoints return standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid input)
- **422**: Validation Error
- **500**: Internal Server Error

**Error Response Schema:**
```json
{
  "type": "object",
  "properties": {
    "detail": {
      "type": "string",
      "description": "Error message"
    }
  }
}
```

---

## 📊 Model Information

### Supported Estimation Models:
1. **COCOMO II** - Industry standard parametric estimation
2. **Function Points** - Based on functional requirements
3. **Use Case Points** - Object-oriented approach
4. **Machine Learning** - Trained on historical project data
5. **Task-based** - Bottom-up estimation from task lists

### Supported Document Formats:
- **.txt** - Plain text requirements
- **.pdf** - PDF documents
- **.docx** - Microsoft Word documents

---

## 🚀 Deployment Information

- **Platform**: HuggingFace Spaces
- **Runtime**: Python 3.10
- **Framework**: FastAPI + Docker
- **Available 24/7**: Yes
- **Auto-scaling**: Yes

**Base URL**: `https://nhathuyyne-software-effort-estimation-full-api.hf.space`

**Interactive Docs**: `https://nhathuyyne-software-effort-estimation-full-api.hf.space/docs`

---

*Updated: January 2025 | Version: 2.0.0 | FastAPI Full Deployment*