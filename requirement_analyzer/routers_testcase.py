"""
Test Case Generation Routes
Tích hợp vào requirement_analyzer.api
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional

router = APIRouter(prefix="", tags=["testcase"])


@router.get("/testcase", response_class=HTMLResponse)
async def testcase_page():
    """Test case generation main page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Case Generator</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 32px;
            }
            .header p {
                color: #666;
                margin: 0;
            }
            .content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            .panel {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .panel h2 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 22px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
                color: #333;
            }
            textarea, input, select {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-family: monospace;
                font-size: 13px;
                transition: border-color 0.3s;
            }
            textarea:focus, input:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            textarea {
                min-height: 150px;
                resize: vertical;
            }
            .btn-group {
                display: flex;
                gap: 12px;
                margin-top: 20px;
            }
            button {
                flex: 1;
                padding: 12px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s;
            }
            button:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .results {
                display: none;
                margin-top: 20px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .results.show {
                display: block;
            }
            .results h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            .test-case {
                background: white;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }
            .test-case h4 {
                color: #333;
                margin-bottom: 8px;
            }
            .test-case p {
                color: #666;
                font-size: 12px;
                margin: 4px 0;
            }
            .test-type {
                display: inline-block;
                padding: 4px 8px;
                background: #e3f2fd;
                color: #667eea;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
            }
            @media (max-width: 1024px) {
                .content {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧬 Test Case Generator</h1>
                <p>Generate comprehensive test cases from requirements with automated scenario generation</p>
            </div>

            <div class="content">
                <!-- Input Panel -->
                <div class="panel">
                    <h2>Input Requirements</h2>
                    
                    <div class="form-group">
                        <label>Requirements Description</label>
                        <textarea id="requirements" placeholder="Enter your requirements...

Example:

Feature: User Login
- Users can login with email and password
- System validates email format
- Password must be at least 8 characters
- Failed login attempts are logged
- Account locks after 5 failed attempts
- Users can reset password via email"></textarea>
                    </div>

                    <div class="btn-group">
                        <button onclick="generateTestCases()">Generate Test Cases</button>
                    </div>
                </div>

                <!-- Results Panel -->
                <div class="panel">
                    <h2>Generated Test Cases</h2>
                    <div id="results" class="results">
                        <div id="testCasesContainer"></div>
                    </div>
                    <div id="emptyState" style="text-align: center; color: #999; padding: 40px 20px;">
                        <p style="font-size: 14px;">No test cases generated yet</p>
                        <p style="font-size: 12px; margin-top: 10px;">Fill in requirements and click "Generate Test Cases"</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function generateTestCases() {
                const requirements = document.getElementById('requirements').value;
                if (!requirements.trim()) {
                    alert('Please enter requirements');
                    return;
                }

                try {
                    document.querySelector('button').textContent = 'Generating...';
                    
                    const formData = new FormData();
                    formData.append('requirements', requirements);

                    const response = await fetch('/api/v2/test-generation/generate-test-cases', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error('API error: ' + response.statusText);
                    }

                    const data = await response.json();
                    displayTestCases(data);
                    
                } catch (error) {
                    alert('Error: ' + error.message);
                } finally {
                    document.querySelector('button').textContent = 'Generate Test Cases';
                }
            }

            function displayTestCases(data) {
                const container = document.getElementById('testCasesContainer');
                const empty = document.getElementById('emptyState');
                const results = document.getElementById('results');

                container.innerHTML = '';

                if (!data.test_cases || data.test_cases.length === 0) {
                    alert('No test cases generated');
                    return;
                }

                let html = `<h3>Generated Test Cases (${data.test_cases.length} total)</h3>`;

                data.test_cases.forEach((testCase, index) => {
                    html += `
                        <div class="test-case">
                            <h4>TC-${String(index + 1).padStart(3, '0')}: ${testCase.title || 'Test Case ' + (index + 1)}</h4>
                            <p><strong>Type:</strong> <span class="test-type">${testCase.type || 'Functional'}</span></p>
                            <p><strong>Preconditions:</strong> ${testCase.preconditions || 'None'}</p>
                            <p><strong>Steps:</strong> ${(testCase.steps || ['No steps']).join(' → ')}</p>
                            <p><strong>Expected:</strong> ${testCase.expected_result || 'Not specified'}</p>
                        </div>
                    `;
                });

                container.innerHTML = html;
                results.classList.add('show');
                empty.style.display = 'none';
            }
        </script>
    </body>
    </html>
    """


@router.get("/test/analyzer", response_class=HTMLResponse)
async def test_analyzer():
    """Test analyzer page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Requirement Analyzer Test</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background: #f5f5f5; font-family: monospace; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            h1 { color: #667eea; margin-bottom: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; }
            textarea, input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-family: monospace; }
            button { background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
            button:hover { background: #5568d3; }
            pre { background: #f9f9f9; padding: 15px; border-radius: 6px; overflow-x: auto; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Requirement Analyzer - Test Page</h1>
            <div class="form-group">
                <label>Requirements Text</label>
                <textarea id="requirements" placeholder="Enter requirements..."></textarea>
            </div>
            <button onclick="analyzeRequirements()">Analyze Requirements</button>
            <pre id="results" style="display:none;"></pre>
        </div>
        <script>
            async function analyzeRequirements() {
                const requirements = document.getElementById('requirements').value;
                if (!requirements.trim()) { alert('Enter requirements'); return; }
                try {
                    const formData = new FormData();
                    formData.append('text', requirements);
                    const response = await fetch('/api/v3/generate', { method: 'POST', body: formData });
                    const data = await response.json();
                    document.getElementById('results').textContent = JSON.stringify(data, null, 2);
                    document.getElementById('results').style.display = 'block';
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """


@router.get("/test/testgen", response_class=HTMLResponse)
async def test_testgen():
    """Test testgen page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Test Generator Test</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background: #f5f5f5; font-family: monospace; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #764ba2; margin-bottom: 20px; }
            textarea { width: 100%; padding: 12px; border: 1px solid #ddd; min-height: 150px; }
            button { background: #764ba2; color: white; padding: 12px 30px; border: none; border-radius: 6px; cursor: pointer; margin-top: 10px; }
            pre { background: #f9f9f9; padding: 15px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧬 Test Case Generator</h1>
            <textarea id="requirements" placeholder="Enter requirements..."></textarea><br>
            <button onclick="generateTests()">Generate Test Cases</button>
            <pre id="results" style="display:none;"></pre>
        </div>
        <script>
            async function generateTests() {
                const requirements = document.getElementById('requirements').value;
                if (!requirements.trim()) { 
                    alert('Enter requirements'); 
                    return; 
                }
                try {
                    const testData = {
                        requirements: requirements,
                        max_tests: 50,
                        threshold: 0.5
                    };
                    
                    console.log('Sending request:', testData);
                    
                    const response = await fetch('/api/v2/test-generation/generate-test-cases', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify(testData)
                    });
                    
                    console.log('Response status:', response.status);
                    
                    const data = await response.json();
                    console.log('Response data:', data);
                    
                    if (!response.ok) {
                        const errorMsg = data.detail ? 
                            (Array.isArray(data.detail) ? JSON.stringify(data.detail) : data.detail) : 
                            response.statusText;
                        throw new Error('API error: ' + errorMsg);
                    }
                    
                    document.getElementById('results').textContent = JSON.stringify(data, null, 2);
                    document.getElementById('results').style.display = 'block';
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """


@router.get("/test", response_class=HTMLResponse)
async def test_hub():
    """Main test hub page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Test Hub</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace;
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header {
                color: white;
                text-align: center;
                margin-bottom: 40px;
                padding: 40px 20px;
            }
            .header h1 { font-size: 40px; margin-bottom: 10px; }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-decoration: none;
                color: inherit;
                cursor: pointer;
                transition: all 0.3s;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            }
            .card h2 { color: #667eea; margin-bottom: 10px; }
            .card p { color: #666; font-size: 14px; margin-bottom: 20px; }
            .card button {
                display: inline-block;
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            }
            .card button:hover { background: #5568d3; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧪 Test Hub</h1>
                <p>Comprehensive Testing Platform</p>
            </div>

            <div class="grid">
                <a href="/testcase" class="card">
                    <h2>Advanced Test Generator</h2>
                    <p>Generate comprehensive test cases with coverage analysis and export capabilities.</p>
                    <button>Open</button>
                </a>

                <a href="/test/analyzer" class="card">
                    <h2>Analyzer Test</h2>
                    <p>Test the requirement analyzer directly.</p>
                    <button>Open</button>
                </a>

                <a href="/test/testgen" class="card">
                    <h2>Test Generator</h2>
                    <p>Generate test cases from requirements.</p>
                    <button>Open</button>
                </a>
            </div>
        </div>
    </body>
    </html>
    """


@router.get("/testcase/dashboard", response_class=HTMLResponse)
async def testcase_dashboard():
    """Test case dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Test Case Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { background: #f5f5f5; font-family: monospace; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { color: #667eea; margin-bottom: 30px; }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stat-number { font-size: 32px; font-weight: 700; color: #667eea; margin-bottom: 10px; }
            .stat-label { color: #999; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Test Case Dashboard</h1>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">1,250</div>
                    <div class="stat-label">Total Test Cases</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">87%</div>
                    <div class="stat-label">Avg Coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">45</div>
                    <div class="stat-label">Projects Tested</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
