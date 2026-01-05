# 📚 Software Effort Estimation API Documentation

## API Base URL
- **Gradio Interface**: https://huggingface.co/spaces/nhathuyyne/software-effort-estimation-api
- **API Base URL**: https://nhathuyyne-software-effort-estimation-api.hf.space
- **Interactive API Docs**: https://nhathuyyne-software-effort-estimation-api.hf.space/docs

## 🚀 Quick Start

### Using curl
```bash
curl -X POST "https://nhathuyyne-software-effort-estimation-api.hf.space/estimate" \
     -H "Content-Type: application/json" \
     -d '{"text": "Develop a web application with user authentication and reporting features", "method": "weighted_average"}'
```

### Using Python
```python
import requests
import json

# Text-based estimation
response = requests.post(
    "https://nhathuyyne-software-effort-estimation-api.hf.space/estimate",
    json={
        "text": "Develop a web application with user authentication and reporting features",
        "method": "weighted_average"
    }
)

result = response.json()
print(json.dumps(result, indent=2))
```

## 📋 API Endpoints

### 1. POST /estimate
Analyze requirements from text input and provide effort estimation.

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
    },
    "method": {
      "type": "string",
      "enum": ["weighted_average", "median", "mean", "max", "min"],
      "default": "weighted_average",
      "description": "Integration method for combining model estimates"
    }
  },
  "required": ["text"]
}
```

#### Example Request
```json
{
  "text": "Develop a web-based e-commerce platform with the following features:\n- User registration and authentication\n- Product catalog with search and filtering\n- Shopping cart functionality\n- Payment processing integration\n- Order management system\n- Admin dashboard for inventory management\n- Email notifications\n- Performance requirements: 1000 concurrent users\n- Security: PCI DSS compliance required\n- Technology: React frontend, Node.js backend, PostgreSQL database",
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
          "type": "number",
          "description": "Recommended team size"
        },
        "confidence_level": {
          "type": "string",
          "enum": ["Low", "Medium", "High"],
          "description": "Confidence level of the estimation"
        },
        "model_estimates": {
          "type": "object",
          "description": "Individual model estimation results"
        }
      }
    },
    "analysis": {
      "type": "object",
      "description": "Detailed requirement analysis results"
    }
  }
}
```

#### Example Response
```json
{
  "estimation": {
    "total_effort": 18.5,
    "duration": 8.2,
    "team_size": 2.3,
    "confidence_level": "Medium",
    "model_estimates": {
      "COCOMO_II": {
        "effort": 22.4,
        "confidence": 75,
        "type": "Parametric",
        "description": "COCOMO II estimation based on size and complexity factors"
      },
      "Function_Points": {
        "effort": 16.8,
        "confidence": 70,
        "type": "Functional",
        "description": "Function Points analysis"
      },
      "Use_Case_Points": {
        "effort": 14.2,
        "confidence": 65,
        "type": "Use Case",
        "description": "Use Case Points estimation"
      },
      "LOC_Linear": {
        "effort": 19.1,
        "confidence": 80,
        "type": "LOC",
        "description": "Lines of Code linear regression model"
      },
      "LOC_Random_Forest": {
        "effort": 20.3,
        "confidence": 85,
        "type": "LOC",
        "description": "Lines of Code random forest model"
      },
      "ML_Linear_Regression": {
        "effort": 17.9,
        "confidence": 78,
        "type": "Machine Learning",
        "description": "Linear regression ML model"
      },
      "ML_Random_Forest": {
        "effort": 18.7,
        "confidence": 82,
        "type": "Machine Learning", 
        "description": "Random forest ML model"
      }
    }
  },
  "analysis": {
    "cocomo": {
      "size": 15.8,
      "complexity": 1.2,
      "eaf": 1.15
    },
    "function_points": {
      "external_inputs": 8,
      "external_outputs": 6,
      "external_inquiries": 5,
      "internal_files": 4,
      "external_files": 3,
      "fp": 156
    },
    "priority_analysis": {
      "critical_requirements": 3,
      "high_priority": 5,
      "medium_priority": 7,
      "low_priority": 2
    }
  }
}
```

---

### 2. POST /upload-requirements
Upload and analyze requirements document files.

#### Request Format
- **Content-Type**: `multipart/form-data`
- **Supported file types**: `.txt`, `.md`, `.pdf`, `.doc`, `.docx`
- **Max file size**: 10MB

#### Form Parameters
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "file": {
      "type": "string",
      "format": "binary",
      "description": "Requirements document file"
    },
    "method": {
      "type": "string",
      "enum": ["weighted_average", "median", "mean", "max", "min"],
      "default": "weighted_average",
      "description": "Integration method for combining model estimates"
    }
  },
  "required": ["file"]
}
```

#### Example using curl
```bash
curl -X POST "https://nhathuyyne-software-effort-estimation-api.hf.space/upload-requirements" \
     -F "file=@requirements.pdf" \
     -F "method=weighted_average"
```

#### Example using Python
```python
import requests

with open('requirements.pdf', 'rb') as f:
    response = requests.post(
        "https://nhathuyyne-software-effort-estimation-api.hf.space/upload-requirements",
        files={'file': f},
        data={'method': 'weighted_average'}
    )

result = response.json()
```

#### Response Schema
Same as `/estimate` endpoint, plus additional document metadata:
```json
{
  "estimation": { /* ... same as above ... */ },
  "analysis": { /* ... same as above ... */ },
  "document": {
    "filename": "requirements.pdf",
    "file_type": ".pdf", 
    "size_bytes": 1024000,
    "text_length": 5432
  }
}
```

---

### 3. POST /estimate-cocomo
Detailed COCOMO II parametric estimation with comprehensive project parameters.

#### Request Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "software_size": {
      "type": "number",
      "minimum": 0.1,
      "maximum": 10000,
      "description": "Software size in KLOC (Thousands of Lines of Code)"
    },
    "precedentedness": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high", "extra_high"],
      "default": "nominal",
      "description": "Organizational familiarity with this type of project"
    },
    "development_flexibility": {
      "type": "string", 
      "enum": ["very_low", "low", "nominal", "high", "very_high", "extra_high"],
      "default": "nominal",
      "description": "Degree of flexibility in development process"
    },
    "architecture_risk_resolution": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high", "extra_high"],
      "default": "nominal",
      "description": "Risk analysis thoroughness"
    },
    "team_cohesion": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high", "extra_high"],
      "default": "nominal",
      "description": "Team collaboration effectiveness"
    },
    "process_maturity": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high", "extra_high"],
      "default": "nominal",
      "description": "Process maturity level (CMM, CMMI)"
    },
    "required_software_reliability": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high", "extra_high"],
      "default": "nominal",
      "description": "Required software reliability level"
    },
    "database_size": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high", "extra_high"],
      "default": "nominal",
      "description": "Database size relative to program size"
    },
    "product_complexity": {
      "type": "string",
      "enum": ["very_low", "low", "nominal", "high", "very_high", "extra_high"],
      "default": "nominal",
      "description": "Overall product complexity"
    },
    "cost_per_person_month": {
      "type": "number",
      "minimum": 3000,
      "maximum": 50000,
      "default": 5000,
      "description": "Average cost per person-month in USD"
    },
    "method": {
      "type": "string",
      "enum": ["weighted_average", "median", "mean", "max", "min"],
      "default": "weighted_average",
      "description": "Integration method for combining estimates"
    }
  },
  "required": ["software_size"]
}
```

#### Example Request
```json
{
  "software_size": 25.0,
  "precedentedness": "nominal",
  "development_flexibility": "high",
  "architecture_risk_resolution": "high",
  "team_cohesion": "high",
  "process_maturity": "nominal",
  "required_software_reliability": "high",
  "database_size": "nominal",
  "product_complexity": "nominal",
  "cost_per_person_month": 6000.0,
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
        "integrated_estimate": {
          "type": "number",
          "description": "Final integrated effort estimate in person-months"
        },
        "duration": {
          "type": "number",
          "description": "Project duration in months"
        },
        "team_size": {
          "type": "number",
          "description": "Recommended team size"
        },
        "confidence_level": {
          "type": "number",
          "description": "Confidence level percentage"
        }
      }
    },
    "cocomo_details": {
      "type": "object",
      "properties": {
        "software_size": {
          "type": "number",
          "description": "Input software size"
        },
        "effort_adjustment_factor": {
          "type": "number",
          "description": "Combined effort adjustment factor"
        },
        "scale_factor": {
          "type": "number",
          "description": "Combined scale factor"
        },
        "cocomo_effort": {
          "type": "number",
          "description": "Pure COCOMO effort estimate"
        },
        "cocomo_schedule": {
          "type": "number", 
          "description": "Pure COCOMO schedule estimate"
        },
        "total_cost": {
          "type": "number",
          "description": "Total project cost in USD"
        }
      }
    },
    "phase_distribution": {
      "type": "object",
      "description": "Effort distribution across development phases",
      "properties": {
        "inception": {
          "type": "object",
          "properties": {
            "effort": {"type": "number"},
            "schedule": {"type": "number"},
            "staff": {"type": "number"},
            "cost": {"type": "number"}
          }
        },
        "elaboration": {
          "type": "object",
          "properties": {
            "effort": {"type": "number"},
            "schedule": {"type": "number"},
            "staff": {"type": "number"},
            "cost": {"type": "number"}
          }
        },
        "construction": {
          "type": "object",
          "properties": {
            "effort": {"type": "number"},
            "schedule": {"type": "number"},
            "staff": {"type": "number"},
            "cost": {"type": "number"}
          }
        },
        "transition": {
          "type": "object",
          "properties": {
            "effort": {"type": "number"},
            "schedule": {"type": "number"},
            "staff": {"type": "number"},
            "cost": {"type": "number"}
          }
        }
      }
    }
  }
}
```

---

### 4. POST /estimate-from-tasks
Estimate effort from structured task list with priority analysis.

#### Request Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "Task title"
          },
          "description": {
            "type": "string",
            "description": "Task description"
          },
          "priority": {
            "type": "string",
            "enum": ["Critical", "High", "Medium", "Low"],
            "default": "Medium",
            "description": "Task priority level"
          },
          "complexity": {
            "type": "string",
            "enum": ["Low", "Medium", "High"],
            "default": "Medium",
            "description": "Technical complexity level"
          },
          "business_impact": {
            "type": "string",
            "enum": ["Low", "Medium", "High"],
            "default": "Medium",
            "description": "Business impact level"
          },
          "estimated_hours": {
            "type": "number",
            "minimum": 0,
            "description": "Optional: Initial time estimate in hours"
          }
        },
        "required": ["title", "description"]
      },
      "minItems": 1
    },
    "method": {
      "type": "string",
      "enum": ["weighted_average", "median", "mean", "max", "min"],
      "default": "weighted_average",
      "description": "Integration method for combining estimates"
    }
  },
  "required": ["tasks"]
}
```

#### Example Request
```json
{
  "tasks": [
    {
      "title": "User Authentication System",
      "description": "Implement user registration, login, password reset functionality with JWT tokens",
      "priority": "Critical",
      "complexity": "Medium",
      "business_impact": "High"
    },
    {
      "title": "Product Catalog",
      "description": "Create product listing, search, filtering, and pagination features",
      "priority": "High",
      "complexity": "Medium",
      "business_impact": "High"
    },
    {
      "title": "Shopping Cart",
      "description": "Add to cart, remove items, quantity updates, persist cart state",
      "priority": "High", 
      "complexity": "Low",
      "business_impact": "High"
    },
    {
      "title": "Payment Processing",
      "description": "Integrate with payment gateway, handle transactions, refunds",
      "priority": "Critical",
      "complexity": "High",
      "business_impact": "High"
    },
    {
      "title": "Admin Dashboard",
      "description": "Dashboard for managing products, orders, and analytics",
      "priority": "Medium",
      "complexity": "Medium",
      "business_impact": "Medium"
    },
    {
      "title": "Email Notifications",
      "description": "Send order confirmations, shipping updates via email",
      "priority": "Medium",
      "complexity": "Low",
      "business_impact": "Medium"
    }
  ],
  "method": "weighted_average"
}
```

#### Response Schema
Same as `/estimate` endpoint, plus task analysis:
```json
{
  "estimation": { /* ... same structure as /estimate ... */ },
  "analysis": { /* ... same structure as /estimate ... */ },
  "tasks": [
    /* Original task list with additional analysis */
  ],
  "priority_breakdown": {
    "critical_tasks": 2,
    "high_priority_tasks": 2, 
    "medium_priority_tasks": 2,
    "low_priority_tasks": 0,
    "total_estimated_effort": 18.5,
    "effort_by_priority": {
      "critical": 8.2,
      "high": 6.1,
      "medium": 3.8,
      "low": 0.4
    }
  }
}
```

---

### 5. POST /analyze
Requirement analysis only (no estimation).

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

#### Response Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "requirements": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "text": {"type": "string"},
          "type": {"type": "string"},
          "priority": {"type": "string"},
          "complexity": {"type": "string"},
          "business_impact": {"type": "string"}
        }
      }
    },
    "features": {
      "type": "object",
      "properties": {
        "functional_requirements": {"type": "number"},
        "non_functional_requirements": {"type": "number"},
        "estimated_size": {"type": "number"},
        "complexity_score": {"type": "number"},
        "technologies_mentioned": {"type": "array", "items": {"type": "string"}}
      }
    },
    "priority_analysis": {
      "type": "object",
      "properties": {
        "critical": {"type": "number"},
        "high": {"type": "number"},
        "medium": {"type": "number"},
        "low": {"type": "number"}
      }
    }
  }
}
```

---

## 🔧 Integration Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

const API_BASE = 'https://nhathuyyne-software-effort-estimation-api.hf.space';

async function estimateProject(requirements) {
  try {
    const response = await axios.post(`${API_BASE}/estimate`, {
      text: requirements,
      method: 'weighted_average'
    });
    
    const { estimation, analysis } = response.data;
    
    console.log(`Estimated Effort: ${estimation.total_effort} person-months`);
    console.log(`Duration: ${estimation.duration} months`);
    console.log(`Team Size: ${estimation.team_size} people`);
    console.log(`Confidence: ${estimation.confidence_level}`);
    
    return response.data;
  } catch (error) {
    console.error('Estimation failed:', error.message);
    throw error;
  }
}

// Usage
estimateProject(`
  Develop a customer relationship management (CRM) system with:
  - Contact management
  - Lead tracking
  - Sales pipeline
  - Email integration
  - Reporting dashboard
  - Mobile app
  Expected users: 500 concurrent
  Technology: React, Node.js, MongoDB
`);
```

### Python with requests
```python
import requests
import json

API_BASE = 'https://nhathuyyne-software-effort-estimation-api.hf.space'

def estimate_cocomo_project(size_kloc, complexity='nominal', reliability='nominal'):
    """Estimate using COCOMO II parameters"""
    
    params = {
        'software_size': size_kloc,
        'precedentedness': 'nominal',
        'development_flexibility': 'nominal', 
        'architecture_risk_resolution': 'nominal',
        'team_cohesion': 'nominal',
        'process_maturity': 'nominal',
        'required_software_reliability': reliability,
        'database_size': 'nominal',
        'product_complexity': complexity,
        'cost_per_person_month': 5000.0,
        'method': 'weighted_average'
    }
    
    response = requests.post(f'{API_BASE}/estimate-cocomo', json=params)
    
    if response.status_code == 200:
        data = response.json()
        estimation = data['estimation']
        cocomo = data['cocomo_details']
        
        print(f"Project Size: {cocomo['software_size']} KLOC")
        print(f"Estimated Effort: {estimation['integrated_estimate']:.1f} person-months")
        print(f"Duration: {estimation['duration']:.1f} months") 
        print(f"Total Cost: ${cocomo['total_cost']:,.0f}")
        print(f"Confidence: {estimation['confidence_level']}%")
        
        return data
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

# Usage
result = estimate_cocomo_project(
    size_kloc=30.0,
    complexity='high',
    reliability='high'
)
```

### Python async with aiohttp
```python
import asyncio
import aiohttp
import json

async def estimate_from_file(file_path, method='weighted_average'):
    """Upload and analyze requirements document"""
    
    API_BASE = 'https://nhathuyyne-software-effort-estimation-api.hf.space'
    
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as f:
            form_data = aiohttp.FormData()
            form_data.add_field('file', f, filename=file_path.split('/')[-1])
            form_data.add_field('method', method)
            
            async with session.post(f'{API_BASE}/upload-requirements', data=form_data) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    text = await response.text()
                    raise Exception(f"API Error: {response.status} - {text}")

# Usage
async def main():
    result = await estimate_from_file('project_requirements.pdf')
    print(json.dumps(result, indent=2))

asyncio.run(main())
```

---

## 🚨 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Unsupported file format. Please upload one of: .txt, .doc, .docx, .pdf, .md"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "text"],
      "msg": "String should have at least 10 characters",
      "input": "test"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred during estimation"
}
```

### Retry Logic Example
```python
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "POST"],
        backoff_factor=1
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def estimate_with_retry(requirements_text):
    session = create_session_with_retries()
    
    try:
        response = session.post(
            'https://nhathuyyne-software-effort-estimation-api.hf.space/estimate',
            json={'text': requirements_text, 'method': 'weighted_average'},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise
```

---

## 📊 Understanding the Results

### Effort Estimation Units
- **Person-Months**: Total effort required (e.g., 12 person-months = 1 person for 12 months or 2 people for 6 months)
- **Duration**: Calendar time from start to finish
- **Team Size**: Average number of people needed simultaneously

### Confidence Levels
- **Low (< 50%)**: Limited information, high uncertainty
- **Medium (50-75%)**: Moderate information quality
- **High (> 75%)**: Comprehensive requirements, good historical data

### Model Types
- **COCOMO II**: Industry-standard parametric model
- **Function Points**: Functional size measurement
- **Use Case Points**: Use case driven estimation
- **LOC Models**: Lines of code prediction models  
- **ML Models**: Machine learning regression models

### Priority Categories
- **Critical**: Must-have for minimum viable product
- **High**: Important for full functionality
- **Medium**: Valuable but not essential
- **Low**: Nice-to-have features

---

## 🎯 Best Practices

### 1. Input Quality
- Provide detailed requirements with specific functionality
- Include non-functional requirements (performance, security)
- Mention technology preferences and constraints
- Specify user types and usage patterns

### 2. Validation
- Cross-validate estimates using multiple methods
- Compare with historical project data
- Review assumptions and parameters
- Consider risk factors and contingencies

### 3. Iteration
- Refine estimates as requirements evolve
- Update parameters based on team experience
- Incorporate feedback from actual progress
- Adjust for changing project conditions

### 4. Integration
- Use estimates as starting points, not absolute truth
- Combine with expert judgment
- Consider market and business constraints
- Plan for uncertainty with buffers

---

## 🔍 Advanced Features

### Custom Model Weights
The API supports custom model weighting for organizations with specific preferences:

```python
# Future feature - custom weights
custom_weights = {
    'COCOMO_II': 0.3,
    'Function_Points': 0.2,
    'ML_Random_Forest': 0.3, 
    'LOC_Random_Forest': 0.2
}

response = requests.post(
    f'{API_BASE}/estimate',
    json={
        'text': requirements_text,
        'method': 'custom_weights',
        'model_weights': custom_weights
    }
)
```

### Batch Processing
For processing multiple projects efficiently:

```python
# Future feature - batch estimation
projects = [
    {'id': 'proj1', 'text': 'Requirements for project 1...'},
    {'id': 'proj2', 'text': 'Requirements for project 2...'},
    {'id': 'proj3', 'text': 'Requirements for project 3...'}
]

response = requests.post(
    f'{API_BASE}/batch-estimate',
    json={'projects': projects, 'method': 'weighted_average'}
)
```

### Historical Data Integration
Improve accuracy by leveraging organizational historical data:

```python
# Future feature - historical data
historical_projects = [
    {'actual_effort': 24.5, 'estimated_effort': 22.1, 'features': {...}},
    {'actual_effort': 18.2, 'estimated_effort': 19.8, 'features': {...}}
]

response = requests.post(
    f'{API_BASE}/estimate-with-history',
    json={
        'text': requirements_text,
        'historical_data': historical_projects,
        'method': 'adaptive_learning'
    }
)
```

---

## 📞 Support & Feedback

### Getting Help
- **Documentation**: This comprehensive guide
- **Interactive API**: Visit the Swagger docs at `/docs`
- **Examples**: See the examples in this documentation
- **Issues**: Report bugs and request features

### Contributing
- Model improvements and new estimation methods
- Additional language support for requirements analysis
- Performance optimizations
- Documentation enhancements

### Rate Limits
- **Free tier**: 1000 requests per day
- **Response time**: 5-30 seconds depending on complexity
- **File size limit**: 10MB for document uploads
- **Text limit**: 50,000 characters per request

---

## 🏁 Quick Reference

### Essential Endpoints
```bash
# Text estimation
POST /estimate

# File upload
POST /upload-requirements  

# COCOMO parameters
POST /estimate-cocomo

# Task list
POST /estimate-from-tasks

# Analysis only
POST /analyze
```

### Key Response Fields
```javascript
{
  estimation: {
    total_effort,     // person-months
    duration,         // months
    team_size,        // people
    confidence_level  // Low/Medium/High
  }
}
```

### Common Use Cases
- 📋 **Quick estimates**: Use `/estimate` with text requirements
- 📄 **Document analysis**: Use `/upload-requirements` for files
- 🧮 **Detailed planning**: Use `/estimate-cocomo` for parametric estimation
- 📊 **Task breakdown**: Use `/estimate-from-tasks` for structured analysis

This comprehensive API enables accurate software effort estimation using state-of-the-art methodologies, helping teams plan better and deliver projects successfully.