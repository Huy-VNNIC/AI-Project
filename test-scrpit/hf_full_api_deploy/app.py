""""""

Software Effort Estimation API - Hugging Face Spaces DeploymentFull FastAPI + Gradio deployment for Software Effort Estimation

Full FastAPI backend with all estimation endpoints"""

"""

import gradio as gr

import sysimport requests

from pathlib import Pathimport json

import threading

# Add current directory to Python pathimport time

sys.path.append(str(Path(__file__).parent))import uvicorn

import sys

# Import and run the FastAPI app directlyimport os

from requirement_analyzer.api import appfrom pathlib import Path



if __name__ == "__main__":# Add current directory to path for imports

    import uvicornsys.path.append(str(Path(__file__).parent))

    # For Hugging Face Spaces, the app runs automatically

    # This is just to define the app for the ASGI server# Import the FastAPI app

    print("🚀 Software Effort Estimation API is starting...")from requirement_analyzer.api import app as fastapi_app

    print("📍 Available endpoints:")

    print("   POST /estimate - Text-based estimation")# Global server thread

    print("   POST /upload-requirements - Document upload")server_thread = None

    print("   POST /estimate-from-tasks - Task-based estimation") api_port = 8000

    print("   POST /estimate-cocomo - COCOMO II parameters")

    print("   GET / - Main interface")def start_fastapi_server():

    print("   GET /docs - API documentation")    """Start FastAPI server in background"""

        global server_thread

    # For local testing    if server_thread is None or not server_thread.is_alive():

    uvicorn.run(app, host="0.0.0.0", port=7860)        server_thread = threading.Thread(
            target=lambda: uvicorn.run(fastapi_app, host="0.0.0.0", port=api_port, log_level="warning"),
            daemon=True
        )
        server_thread.start()
        time.sleep(3)  # Wait for server to start

def call_api(endpoint, data=None, method="POST"):
    """Helper function to call FastAPI endpoints"""
    try:
        start_fastapi_server()
        url = f"http://localhost:{api_port}/{endpoint}"
        
        if method == "POST":
            response = requests.post(url, json=data, timeout=60)
        else:
            response = requests.get(url, timeout=60)
            
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def analyze_requirements_text(text, method="weighted_average"):
    """Analyze requirements from text"""
    if not text or len(text.strip()) < 5:
        return "Please provide some requirements text.", ""
    
    result = call_api("estimate", {"text": text, "method": method})
    
    if "error" in result:
        return f"Error: {result['error']}", ""
    
    # Format results for display
    estimation = result.get('estimation', {})
    output = f"""**📊 Estimation Results**

**Total Effort**: {estimation.get('total_effort', 'N/A')} person-months
**Duration**: {estimation.get('duration', 'N/A')} months
**Team Size**: {estimation.get('team_size', 'N/A')} people
**Confidence Level**: {estimation.get('confidence_level', 'N/A')}%

**Model Results**:
"""
    
    model_estimates = result.get('model_estimates', {})
    for model, value in model_estimates.items():
        output += f"• **{model}**: {value:.2f} person-months\n"
    
    return output, json.dumps(result, indent=2)

def analyze_uploaded_file(file, method="weighted_average"):
    """Analyze uploaded requirements file"""
    if not file:
        return "Please upload a file.", ""
    
    try:
        # Read file content  
        with open(file.name, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if not content.strip():
            return "File appears to be empty.", ""
        
        # Use text analysis
        return analyze_requirements_text(content, method)
    except Exception as e:
        return f"Error reading file: {str(e)}", ""

def estimate_cocomo_form(software_size, precedentedness, development_flexibility, 
                        architecture_risk, team_cohesion, process_maturity,
                        required_reliability, database_size, product_complexity,
                        analyst_capability, programmer_capability, 
                        platform_experience, use_of_tools, method="weighted_average"):
    """Estimate using COCOMO II parameters"""
    
    cocomo_params = {
        "software_size": software_size,
        "precedentedness": precedentedness,
        "development_flexibility": development_flexibility,
        "architecture_risk_resolution": architecture_risk,
        "team_cohesion": team_cohesion,
        "process_maturity": process_maturity,
        "required_software_reliability": required_reliability,
        "database_size": database_size,
        "product_complexity": product_complexity,
        "analyst_capability": analyst_capability,
        "programmer_capability": programmer_capability,
        "platform_experience": platform_experience,
        "use_of_software_tools": use_of_tools,
        "method": method
    }
    
    result = call_api("estimate-cocomo", cocomo_params)
    
    if "error" in result:
        return f"Error: {result['error']}", ""
    
    # Format COCOMO results
    estimation = result.get('estimation', {})
    cocomo_details = result.get('cocomo_details', {})
    
    output = f"""**📊 COCOMO II Estimation Results**

**Integrated Estimate**: {estimation.get('integrated_estimate', 'N/A')} person-months
**Duration**: {estimation.get('duration', 'N/A')} months
**Team Size**: {estimation.get('team_size', 'N/A')} people
**Total Cost**: ${cocomo_details.get('total_cost', 'N/A'):,.0f}

**COCOMO Details**:
• **Software Size**: {cocomo_details.get('software_size', 'N/A')} KLOC
• **Effort Adjustment Factor**: {cocomo_details.get('effort_adjustment_factor', 'N/A')}
• **Scale Factor**: {cocomo_details.get('scale_factor', 'N/A')}

**Phase Distribution**:
"""
    
    phases = result.get('phase_distribution', {})
    for phase, details in phases.items():
        output += f"• **{phase.title()}**: {details.get('effort', 0):.1f} PM, {details.get('schedule', 0):.1f} months\n"
    
    return output, json.dumps(result, indent=2)

# Create Gradio interface
with gr.Blocks(title="Software Effort Estimation API", theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>🚀 Software Effort Estimation API</h1>
        <p><strong>Advanced project estimation with multiple models and COCOMO II</strong></p>
    </div>
    """)
    
    with gr.Tabs():
        # Text Analysis Tab
        with gr.TabItem("📝 Text Analysis"):
            gr.Markdown("### Analyze requirements from text")
            with gr.Row():
                with gr.Column(scale=1):
                    text_input = gr.Textbox(
                        label="Requirements Text",
                        lines=8,
                        placeholder="Enter your project requirements here...",
                        value="Build a web application for e-commerce with user authentication, product catalog, shopping cart, payment processing, and admin dashboard. The system should support 1000 concurrent users and integrate with third-party APIs."
                    )
                    text_method = gr.Dropdown(
                        choices=["weighted_average", "median", "mean", "max", "min"],
                        value="weighted_average",
                        label="Estimation Method"
                    )
                    text_btn = gr.Button("🔍 Analyze Requirements", variant="primary")
                
                with gr.Column(scale=1):
                    text_output = gr.Markdown(label="Results")
                    text_json = gr.Code(label="JSON Response", language="json")
            
            text_btn.click(
                analyze_requirements_text,
                inputs=[text_input, text_method],
                outputs=[text_output, text_json]
            )
        
        # File Upload Tab
        with gr.TabItem("📄 File Upload"):
            gr.Markdown("### Upload requirements document")
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(
                        label="Upload Requirements File",
                        file_types=[".txt", ".md", ".pdf", ".doc", ".docx"]
                    )
                    file_method = gr.Dropdown(
                        choices=["weighted_average", "median", "mean", "max", "min"],
                        value="weighted_average",
                        label="Estimation Method"
                    )
                    file_btn = gr.Button("📤 Analyze Document", variant="primary")
                
                with gr.Column(scale=1):
                    file_output = gr.Markdown(label="Results")
                    file_json = gr.Code(label="JSON Response", language="json")
            
            file_btn.click(
                analyze_uploaded_file,
                inputs=[file_input, file_method],
                outputs=[file_output, file_json]
            )
        
        # COCOMO II Parameters Tab
        with gr.TabItem("🧮 COCOMO II Parameters"):
            gr.Markdown("### Detailed COCOMO II estimation with custom parameters")
            with gr.Row():
                with gr.Column(scale=1):
                    software_size = gr.Number(
                        label="Software Size (KLOC)",
                        value=10.0,
                        minimum=0.1,
                        maximum=1000
                    )
                    
                    gr.Markdown("**Scale Drivers**")
                    precedentedness = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Precedentedness"
                    )
                    development_flexibility = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Development Flexibility"
                    )
                    architecture_risk = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Architecture Risk Resolution"
                    )
                    team_cohesion = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Team Cohesion"
                    )
                    process_maturity = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Process Maturity"
                    )
                    
                    gr.Markdown("**Cost Drivers**")
                    required_reliability = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Required Software Reliability"
                    )
                    database_size = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Database Size"
                    )
                    product_complexity = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Product Complexity"
                    )
                    analyst_capability = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Analyst Capability"
                    )
                    programmer_capability = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Programmer Capability"
                    )
                    platform_experience = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Platform Experience"
                    )
                    use_of_tools = gr.Dropdown(
                        choices=["very_low", "low", "nominal", "high", "very_high"],
                        value="nominal",
                        label="Use of Software Tools"
                    )
                    
                    cocomo_method = gr.Dropdown(
                        choices=["weighted_average", "median", "mean"],
                        value="weighted_average",
                        label="Estimation Method"
                    )
                    
                    cocomo_btn = gr.Button("🧮 Calculate COCOMO II", variant="primary")
                
                with gr.Column(scale=1):
                    cocomo_output = gr.Markdown(label="COCOMO Results")
                    cocomo_json = gr.Code(label="Detailed JSON", language="json")
            
            cocomo_btn.click(
                estimate_cocomo_form,
                inputs=[
                    software_size, precedentedness, development_flexibility,
                    architecture_risk, team_cohesion, process_maturity,
                    required_reliability, database_size, product_complexity,
                    analyst_capability, programmer_capability,
                    platform_experience, use_of_tools, cocomo_method
                ],
                outputs=[cocomo_output, cocomo_json]
            )
        
        # API Documentation Tab
        with gr.TabItem("📚 API Endpoints"):
            gr.Markdown("""
## 🔌 Available API Endpoints

This application provides comprehensive FastAPI endpoints for software effort estimation:

### **POST /estimate**
Analyze requirements text and estimate effort.

**Request:**
```json
{
    "text": "Your requirements text here",
    "method": "weighted_average"
}
```

### **POST /upload-requirements**
Upload and analyze requirements documents (.txt, .md, .pdf, .doc, .docx).

### **POST /estimate-from-tasks**
Estimate from structured task lists.

**Request:**
```json
{
    "tasks": [
        {"name": "User Authentication", "complexity": 3},
        {"name": "Dashboard", "complexity": 2}
    ],
    "method": "weighted_average"
}
```

### **POST /estimate-cocomo**
Detailed COCOMO II parameter-based estimation.

**Request:**
```json
{
    "software_size": 10.0,
    "precedentedness": "nominal",
    "development_flexibility": "nominal",
    "method": "weighted_average"
}
```

### **🛠️ Estimation Models**

- **COCOMO II**: Industry-standard parametric model with scale drivers and cost factors
- **Function Points**: Functional size measurement based on system complexity
- **Use Case Points**: Use case driven estimation with actor and use case complexity
- **LOC Models**: Lines of code prediction using linear regression and random forest
- **ML Models**: Machine learning models trained on historical project data

### **📊 Features**

✅ **Multi-Model Integration**: Combines 6+ estimation approaches  
✅ **COCOMO II Support**: Full parameter customization  
✅ **Document Processing**: PDF, Word, text file support  
✅ **Task Management**: Integration with project management tools  
✅ **Priority Analysis**: Smart requirement categorization  
✅ **Confidence Scoring**: Reliability metrics for all estimates  

### **🌐 Base URL**
```
https://nhathuyyne-software-effort-estimation-api.hf.space
```

### **💡 Usage Examples**

**cURL:**
```bash
curl -X POST "https://nhathuyyne-software-effort-estimation-api.hf.space/estimate" \\
     -H "Content-Type: application/json" \\
     -d '{"text": "Build a mobile app with user authentication"}'
```

**Python:**
```python
import requests

# Text estimation
response = requests.post(
    "https://nhathuyyne-software-effort-estimation-api.hf.space/estimate",
    json={"text": "Create a web dashboard with charts and reports"}
)

# COCOMO estimation
cocomo_response = requests.post(
    "https://nhathuyyne-software-effort-estimation-api.hf.space/estimate-cocomo",
    json={
        "software_size": 15.0,
        "product_complexity": "high",
        "analyst_capability": "high"
    }
)

print(response.json())
```
            """)

# Start FastAPI server when app loads
start_fastapi_server()

if __name__ == "__main__":
    demo.launch()