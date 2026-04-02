"""
Test Case Generation Router
Generate test cases with detailed scenarios and coverage analysis
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import json
from typing import Optional

router = APIRouter(prefix="/testcase", tags=["testcase"])

PROJECT_ROOT = Path(__file__).parent.parent.parent


@router.get("/", response_class=HTMLResponse)
async def testcase_home():
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
            button:active {
                transform: translateY(0);
            }
            button.secondary {
                background: #764ba2;
            }
            button.secondary:hover {
                background: #633f7f;
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
                margin-right: 8px;
            }
            .status {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                margin-top: 15px;
            }
            .status-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #4caf50;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .status-text {
                color: #333;
                font-weight: 600;
            }
            .controls {
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-top: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .controls h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            @media (max-width: 1024px) {
                .content {
                    grid-template-columns: 1fr;
                }
            }
            .coverage {
                margin-top: 20px;
                padding: 15px;
                background: #f5f5f5;
                border-radius: 8px;
            }
            .coverage h4 {
                color: #333;
                margin-bottom: 10px;
            }
            .coverage-bar {
                width: 100%;
                height: 20px;
                background: #ddd;
                border-radius: 10px;
                overflow: hidden;
                margin: 8px 0;
            }
            .coverage-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 11px;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧬 Test Case Generator</h1>
                <p>Generate comprehensive test cases from requirements with automated scenario generation and coverage analysis</p>
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

                    <div class="form-group">
                        <label>Test Types to Generate</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <label style="display: flex; align-items: center; cursor: pointer; font-weight: normal;">
                                <input type="checkbox" id="typePositive" checked> Positive Tests
                            </label>
                            <label style="display: flex; align-items: center; cursor: pointer; font-weight: normal;">
                                <input type="checkbox" id="typeNegative" checked> Negative Tests
                            </label>
                            <label style="display: flex; align-items: center; cursor: pointer; font-weight: normal;">
                                <input type="checkbox" id="typeBoundary" checked> Boundary Tests
                            </label>
                            <label style="display: flex; align-items: center; cursor: pointer; font-weight: normal;">
                                <input type="checkbox" id="typeSecurity"> Security Tests
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Coverage Requirements (%)</label>
                        <input type="number" id="coverage" min="0" max="100" value="80" placeholder="80">
                    </div>

                    <div class="btn-group">
                        <button id="generateBtn" onclick="generateTestCases()">Generate Test Cases</button>
                        <button class="secondary" onclick="clearAll()">Clear</button>
                    </div>

                    <div class="status">
                        <div class="status-indicator"></div>
                        <div class="status-text">System Ready</div>
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
                        <p style="font-size: 12px; margin-top: 10px;">Fill in the requirements and click "Generate Test Cases"</p>
                    </div>
                </div>
            </div>

            <!-- Coverage & Controls -->
            <div class="controls">
                <h3>Test Coverage & Export</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div id="coverageSection" style="display: none;">
                        <div class="coverage">
                            <h4>Overall Coverage</h4>
                            <div class="coverage-bar">
                                <div class="coverage-fill" id="coverageFill" style="width: 0%">0%</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button onclick="exportAsJSON()" style="background: #4caf50;">📥 Export JSON</button>
                    <button onclick="exportAsCSV()" style="background: #ff9800;">📊 Export CSV</button>
                    <button onclick="copyToClipboard()" style="background: #2196f3;">📋 Copy Results</button>
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

                const testData = {
                    requirements: requirements,
                    max_tests: 50,
                    threshold: 0.5
                };

                try {
                    const btn = document.getElementById('generateBtn');
                    btn.textContent = 'Generating...';
                    btn.disabled = true;
                    
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

                    displayTestCases(data, {});
                    btn.disabled = false;
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error generating test cases:\n' + error.message);
                    const btn = document.getElementById('generateBtn');
                    btn.textContent = 'Generate Test Cases';
                    btn.disabled = false;
                }
            }

            function displayTestCases(data, types) {
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
                            <p><strong>Preconditions:</strong> ${testCase.preconditions || 'None specified'}</p>
                            <p><strong>Steps:</strong></p>
                            <ol style="margin-left: 20px; color: #666; font-size: 12px;">
                                ${(testCase.steps || ['No steps provided']).map(step => `<li>${step}</li>`).join('')}
                            </ol>
                            <p style="margin-top: 8px;"><strong>Expected Result:</strong> ${testCase.expected_result || 'Not specified'}</p>
                            ${testCase.confidence ? `<p><strong>Confidence:</strong> ${(testCase.confidence * 100).toFixed(0)}%</p>` : ''}
                        </div>
                    `;
                });

                container.innerHTML = html;
                results.classList.add('show');
                empty.style.display = 'none';

                // Update coverage if available
                if (data.coverage_percentage) {
                    document.getElementById('coverageSection').style.display = 'block';
                    const coverageFill = document.getElementById('coverageFill');
                    const coverage = data.coverage_percentage;
                    coverageFill.style.width = coverage + '%';
                    coverageFill.textContent = coverage.toFixed(1) + '%';
                }

                // Store for export
                window.lastGeneratedData = data;
            }

            function clearAll() {
                document.getElementById('requirements').value = '';
                document.getElementById('testCasesContainer').innerHTML = '';
                document.getElementById('results').classList.remove('show');
                document.getElementById('emptyState').style.display = 'block';
                document.getElementById('coverageSection').style.display = 'none';
            }

            function exportAsJSON() {
                if (!window.lastGeneratedData) {
                    alert('Generate test cases first');
                    return;
                }
                const json = JSON.stringify(window.lastGeneratedData, null, 2);
                downloadFile(json, 'test-cases.json', 'application/json');
            }

            function exportAsCSV() {
                if (!window.lastGeneratedData) {
                    alert('Generate test cases first');
                    return;
                }
                
                let csv = 'TC ID,Title,Type,Preconditions,Steps,Expected Result,Confidence\\n';
                window.lastGeneratedData.test_cases.forEach((tc, i) => {
                    csv += `TC-${String(i + 1).padStart(3, '0')},`;
                    csv += `"${tc.title || ''}",`;
                    csv += `"${tc.type || 'Functional'}",`;
                    csv += `"${tc.preconditions || ''}",`;
                    csv += `"${(tc.steps || []).join('; ')}",`;
                    csv += `"${tc.expected_result || ''}",`;
                    csv += `${tc.confidence ? (tc.confidence * 100).toFixed(0) : ''}\\n`;
                });
                
                downloadFile(csv, 'test-cases.csv', 'text/csv');
            }

            function downloadFile(content, filename, type) {
                const blob = new Blob([content], { type });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                URL.revokeObjectURL(url);
            }

            function copyToClipboard() {
                if (!window.lastGeneratedData) {
                    alert('Generate test cases first');
                    return;
                }
                const text = JSON.stringify(window.lastGeneratedData, null, 2);
                navigator.clipboard.writeText(text).then(() => {
                    alert('Test cases copied to clipboard!');
                });
            }
        </script>
    </body>
    </html>
    """


@router.get("/generation", response_class=HTMLResponse)
async def testcase_generation():
    """Redirect to main testcase page"""
    return await testcase_home()


@router.post("/generate")
async def generate_testcases(requirements: str = None):
    """API endpoint for test case generation"""
    if not requirements:
        raise HTTPException(status_code=400, detail="Requirements text required")
    
    try:
        # Call the backend API
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'http://localhost:8000/api/v2/test-generation/generate-test-cases',
                data={'requirements': requirements}
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Generation failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_class=HTMLResponse)
async def testcase_dashboard():
    """Test case generation dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Test Case Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: #f5f5f5;
                font-family: monospace;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
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
            .stat-number {
                font-size: 32px;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 10px;
            }
            .stat-label {
                color: #999;
                font-size: 12px;
            }
            .quick-actions {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .quick-actions h2 {
                margin-bottom: 15px;
                color: #667eea;
            }
            .action-buttons {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            .action-btn {
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            }
            .action-btn:hover {
                background: #5568d3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Test Case Generation Dashboard</h1>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">1,250</div>
                    <div class="stat-label">Total Test Cases Generated</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">87%</div>
                    <div class="stat-label">Average Coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">45</div>
                    <div class="stat-label">Projects Tested</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">92%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>

            <div class="quick-actions">
                <h2>Quick Actions</h2>
                <div class="action-buttons">
                    <a href="/testcase" class="action-btn">New Test Generation</a>
                    <a href="/test/comparison" class="action-btn">Compare Systems</a>
                    <a href="/docs" class="action-btn">API Documentation</a>
                    <a href="/test" class="action-btn">Back to Test Hub</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
