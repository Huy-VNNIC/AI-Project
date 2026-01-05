# 📚 Software Effort Estimation API Documentation

## Overview

This API provides comprehensive software effort estimation using multiple models including COCOMO II, Function Points, Use Case Points, and Machine Learning models.

**Base URL**: `https://your-space-url.hf.space`

## 🔐 Authentication

No authentication required for public endpoints.

## 📋 Endpoints

### 1. POST `/analyze`

Analyze requirements text and extract project parameters.

#### Request Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "Requirements text to analyze",
      "minLength": 10,
      "maxLength": 50000
    }
  },
  "required": ["text"]
}
```

#### Example Request
```json
{
  "text": "Build a web application with user authentication, product catalog, shopping cart functionality, payment processing integration, and admin dashboard. The system should support 1000 concurrent users and integrate with external APIs."
}
```

#### Response Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "analysis": {
      "type": "object",
      "properties": {
        "complexity": {
          "type": "number",
          "description": "Project complexity score (0-1)"
        },
        "technology_risk": {
          "type": "number",
          "description": "Technology risk assessment"
        },
        "team_experience": {
          "type": "number",
          "description": "Required team experience level"
        },
        "requirements_clarity": {
          "type": "number",
          "description": "Requirements clarity score"
        }
      }
    },
    "extracted_features": {
      "type": "object",
      "properties": {
        "functional_requirements": {
          "type": "array",
          "items": {"type": "string"}
        },
        "non_functional_requirements": {
          "type": "array", 
          "items": {"type": "string"}
        },
        "technologies": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    }
  }
}
```

### 2. POST `/upload-requirements`

Upload and process requirement documents.

#### Request
- **Content-Type**: `multipart/form-data`
- **File**: Upload PDF, DOCX, or TXT file

#### Response Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema", 
  "type": "object",
  "properties": {
    "filename": {
      "type": "string",
      "description": "Uploaded filename"
    },
    "analysis": {
      "$ref": "#/components/schemas/AnalysisResult"
    },
    "extracted_text": {
      "type": "string",
      "description": "Extracted text from document"
    }
  }
}
```

### 3. POST `/estimate-from-tasks`

Estimate effort from task breakdown.

#### Request Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object", 
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 3
      },
      "minItems": 1,
      "description": "List of project tasks"
    },
    "method": {
      "type": "string",
      "enum": ["weighted_average", "median", "mean", "max", "min"],
      "default": "weighted_average",
      "description": "Estimation aggregation method"
    }
  },
  "required": ["tasks"]
}
```

#### Example Request
```json
{
  "tasks": [
    "Design database schema",
    "Implement user authentication",
    "Create product catalog API", 
    "Build shopping cart functionality",
    "Integrate payment gateway",
    "Develop admin dashboard",
    "Write unit tests",
    "Deploy to production"
  ],
  "method": "weighted_average"
}
```

#### Response Schema  
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "estimation": {
      "type": "object",
      "properties": {
        "total_effort": {
          "type": "number",
          "description": "Total effort in person-months"
        },
        "duration": {
          "type": "number", 
          "description": "Project duration in months"
        },
        "team_size": {
          "type": "integer",
          "description": "Recommended team size"
        },
        "confidence_level": {
          "type": "string",
          "enum": ["Low", "Medium", "High"],
          "description": "Estimation confidence"
        }
      }
    },
    "task_breakdown": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "task": {"type": "string"},
          "estimated_effort": {"type": "number"},
          "complexity": {"type": "string"}
        }
      }
    },
    "models_used": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of estimation models applied"
    }
  }
}
```

### 4. POST `/estimate-cocomo`

Detailed COCOMO II estimation with parameters.

#### Request Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "kloc": {
      "type": "number",
      "minimum": 0.1,
      "maximum": 10000,
      "description": "Thousands of Lines of Code"
    },
    "precedentedness": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high"],
      "description": "Project precedentedness level"
    },
    "development_flexibility": {
      "type": "string", 
      "enum": ["very_low", "low", "nominal", "high", "very_high"],
      "description": "Development flexibility level"
    },
    "architecture_risk_resolution": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high"], 
      "description": "Architecture/risk resolution level"
    },
    "team_cohesion": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high"],
      "description": "Team cohesion level"
    },
    "process_maturity": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high"],
      "description": "Process maturity level"
    },
    "required_reliability": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high"],
      "description": "Required software reliability"
    },
    "database_size": {
      "type": "string",
      "enum": ["low", "nominal", "high", "very_high"],
      "description": "Database size rating"
    },
    "product_complexity": {
      "type": "string", 
      "enum": ["very_low", "low", "nominal", "high", "very_high", "extra_high"],
      "description": "Product complexity rating"
    }
  },
  "required": ["kloc"]
}
```

#### Example Request
```json
{
  "kloc": 50,
  "precedentedness": "nominal",
  "development_flexibility": "high", 
  "architecture_risk_resolution": "nominal",
  "team_cohesion": "high",
  "process_maturity": "nominal",
  "required_reliability": "high",
  "database_size": "high",
  "product_complexity": "nominal"
}
```

#### Response Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "cocomo_estimation": {
      "type": "object", 
      "properties": {
        "effort_person_months": {
          "type": "number",
          "description": "Effort in person-months"
        },
        "schedule_months": {
          "type": "number",
          "description": "Schedule in months"
        },
        "team_size": {
          "type": "number",
          "description": "Average team size"
        },
        "productivity": {
          "type": "number", 
          "description": "Productivity in KLOC/person-month"
        }
      }
    },
    "scale_factors": {
      "type": "object",
      "properties": {
        "precedentedness": {"type": "number"},
        "development_flexibility": {"type": "number"},
        "architecture_risk_resolution": {"type": "number"},
        "team_cohesion": {"type": "number"}, 
        "process_maturity": {"type": "number"}
      }
    },
    "effort_multipliers": {
      "type": "object",
      "additionalProperties": {"type": "number"}
    },
    "confidence_interval": {
      "type": "object",
      "properties": {
        "lower_bound": {"type": "number"},
        "upper_bound": {"type": "number"},
        "confidence_level": {"type": "string"}
      }
    }
  }
}
```

## 🚀 Usage Examples

### cURL Examples

#### Analyze Requirements
```bash
curl -X POST "https://your-space-url.hf.space/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Build a web application with user authentication and reporting dashboard"
     }'
```

#### Upload Document
```bash
curl -X POST "https://your-space-url.hf.space/upload-requirements" \
     -F "file=@requirements.pdf"
```

#### Task-Based Estimation
```bash
curl -X POST "https://your-space-url.hf.space/estimate-from-tasks" \
     -H "Content-Type: application/json" \
     -d '{
       "tasks": ["User registration", "Login system", "Dashboard", "Reports"],
       "method": "weighted_average"
     }'
```

#### COCOMO Estimation
```bash
curl -X POST "https://your-space-url.hf.space/estimate-cocomo" \
     -H "Content-Type: application/json" \
     -d '{
       "kloc": 25,
       "precedentedness": "nominal",
       "team_cohesion": "high"
     }'
```

### Python Examples

```python
import requests

# Analyze requirements
response = requests.post(
    "https://your-space-url.hf.space/analyze",
    json={"text": "Create a mobile app with user profiles and messaging"}
)
print(response.json())

# Task estimation
response = requests.post(
    "https://your-space-url.hf.space/estimate-from-tasks", 
    json={
        "tasks": ["Database design", "API development", "Frontend"],
        "method": "weighted_average"
    }
)
print(response.json())
```

### JavaScript Examples

```javascript
// Analyze requirements
fetch('https://your-space-url.hf.space/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        text: 'Develop an e-commerce platform with payment integration'
    })
})
.then(response => response.json())
.then(data => console.log(data));

// COCOMO estimation
fetch('https://your-space-url.hf.space/estimate-cocomo', {
    method: 'POST', 
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        kloc: 40,
        precedentedness: 'nominal',
        team_cohesion: 'high'
    })
})
.then(response => response.json()) 
.then(data => console.log(data));
```

## 📊 Model Information

### COCOMO II Model
- Based on Barry Boehm's COCOMO II methodology
- Uses scale factors and effort multipliers
- Suitable for projects 2-1000 KLOC

### Function Points
- Measures functional size of software
- Based on inputs, outputs, inquiries, files, interfaces
- Language independent measurement

### Use Case Points  
- Estimates effort based on use cases
- Considers actors and use case complexity
- Good for object-oriented projects

### Machine Learning Models
- Trained on historical project data
- Uses ensemble methods for better accuracy
- Continuously improved with feedback

## ⚠️ Error Responses

All endpoints return errors in the following format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional error details"
  }
}
```

### Common Error Codes
- `INVALID_INPUT`: Invalid or missing input parameters
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `PROCESSING_ERROR`: Error during analysis or estimation
- `UNSUPPORTED_FORMAT`: Unsupported file format

## 🔧 Rate Limits

- 100 requests per minute per IP
- Maximum file size: 10MB
- Maximum text length: 50,000 characters

## 📞 Support

For technical support or questions about the API, please refer to the documentation or contact the development team.