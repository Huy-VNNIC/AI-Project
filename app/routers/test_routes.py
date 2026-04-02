"""
Test Routes - Add multiple testing pages and endpoints
Trang test để kiểm tra toàn bộ hệ thống
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import os

router = APIRouter(prefix="/test", tags=["testing"])

PROJECT_ROOT = Path(__file__).parent.parent.parent


@router.get("/", response_class=HTMLResponse)
async def test_home():
    """Test home page - navigation to all test pages"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test & Development Center</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                color: white;
                text-align: center;
                margin-bottom: 40px;
                padding: 40px 20px;
            }
            .header h1 {
                font-size: 40px;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                font-size: 18px;
                opacity: 0.9;
            }
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
                transition: all 0.3s;
                text-decoration: none;
                color: inherit;
                cursor: pointer;
                border-left: 4px solid #667eea;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.3);
            }
            .card.analyzer {
                border-left-color: #667eea;
            }
            .card.testgen {
                border-left-color: #764ba2;
            }
            .card.unified {
                border-left-color: #f093fb;
            }
            .card.comparison {
                border-left-color: #4facfe;
            }
            .card h2 {
                font-size: 20px;
                margin-bottom: 10px;
                color: #333;
            }
            .card p {
                color: #666;
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 20px;
            }
            .card-btn {
                display: inline-block;
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s;
                border: none;
                cursor: pointer;
                font-size: 14px;
            }
            .card.analyzer .card-btn {
                background: #667eea;
            }
            .card.testgen .card-btn {
                background: #764ba2;
            }
            .card.unified .card-btn {
                background: #f093fb;
            }
            .card.comparison .card-btn {
                background: #4facfe;
            }
            .card-btn:hover {
                opacity: 0.9;
                transform: translateX(3px);
            }
            .section-title {
                color: white;
                font-size: 24px;
                margin-top: 40px;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            .api-section {
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .api-section h3 {
                color: #667eea;
                margin-bottom: 15px;
                font-size: 18px;
            }
            .api-list {
                list-style: none;
            }
            .api-list li {
                padding: 10px 0;
                border-bottom: 1px solid #f0f0f0;
                font-family: monospace;
                font-size: 13px;
                color: #333;
            }
            .api-list li:last-child {
                border-bottom: none;
            }
            .api-method {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 3px;
                font-weight: 600;
                margin-right: 10px;
                font-size: 11px;
                text-transform: uppercase;
            }
            .api-method.get {
                background: #61affe;
                color: white;
            }
            .api-method.post {
                background: #49cc90;
                color: white;
            }
            .footer {
                color: white;
                text-align: center;
                padding: 20px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧪 Test & Development Center</h1>
                <p>Comprehensive Testing Platform for AI-Project</p>
            </div>

            <div class="section-title">Main Testing Tools</div>
            <div class="grid">
                <a href="/test/analyzer" class="card analyzer">
                    <h2>📊 Requirement Analyzer</h2>
                    <p>Test the requirement analysis engine. Parse requirements, extract tasks, and analyze NLP patterns.</p>
                    <button class="card-btn">Test Analyzer</button>
                </a>

                <a href="/test/testgen" class="card testgen">
                    <h2>🧬 Test Generator</h2>
                    <p>Generate comprehensive test cases from requirements. Support multiple test types and export formats.</p>
                    <button class="card-btn">Test Generator</button>
                </a>

                <a href="/test/unified" class="card unified">
                    <h2>🔗 Unified Interface</h2>
                    <p>Side-by-side testing of both analyzer and test generator. Compare results in real-time.</p>
                    <button class="card-btn">Open Unified</button>
                </a>

                <a href="/test/comparison" class="card comparison">
                    <h2>⚖️ Comparison Tool</h2>
                    <p>Compare outputs from analyzer and test generator. Analyze differences and coverage gaps.</p>
                    <button class="card-btn">Compare</button>
                </a>
            </div>

            <div class="section-title">Available APIs</div>
            <div class="api-section">
                <h3>Requirement Analyzer APIs</h3>
                <ul class="api-list">
                    <li><span class="api-method post">POST</span> /api/v3/generate - Generate tasks from requirements</li>
                    <li><span class="api-method post">POST</span> /api/v2/test-generation/generate-test-cases - Generate test cases</li>
                    <li><span class="api-method get">GET</span> /api/unified/health - Check system health</li>
                    <li><span class="api-method get">GET</span> /docs - Interactive API documentation (Swagger)</li>
                </ul>
            </div>

            <div class="api-section">
                <h3>Test Endpoints</h3>
                <ul class="api-list">
                    <li><span class="api-method get">GET</span> /test - This page (home)</li>
                    <li><span class="api-method get">GET</span> /test/analyzer - Analyzer test page</li>
                    <li><span class="api-method get">GET</span> /test/testgen - Test generator page</li>
                    <li><span class="api-method get">GET</span> /test/unified - Unified interface</li>
                    <li><span class="api-method get">GET</span> /test/comparison - Comparison tool</li>
                    <li><span class="api-method get">GET</span> /test/api - API testing page</li>
                </ul>
            </div>

            <div class="section-title">Quick Access</div>
            <div class="api-section">
                <h3>System Pages</h3>
                <ul class="api-list">
                    <li><span class="api-method get">GET</span> / - Main dashboard</li>
                    <li><span class="api-method get">GET</span> /dashboard - System dashboard</li>
                    <li><span class="api-method get">GET</span> /task-generation - Task generation UI</li>
                    <li><span class="api-method get">GET</span> /unified - Unified test UI</li>
                    <li><span class="api-method get">GET</span> /docs - Swagger API docs</li>
                    <li><span class="api-method get">GET</span> /redoc - ReDoc API docs</li>
                </ul>
            </div>

            <div class="footer">
                <p>AI-Project Testing Suite | All systems operational</p>
                <p style="margin-top: 10px; font-size: 12px;">Last updated: 2026-04-02</p>
            </div>
        </div>
    </body>
    </html>
    """


@router.get("/analyzer", response_class=HTMLResponse)
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
            body {
                background: #f5f5f5;
                font-family: monospace;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            h1 { color: #667eea; margin-bottom: 20px; }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            textarea, input, select {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-family: monospace;
                font-size: 13px;
            }
            textarea {
                min-height: 200px;
                resize: vertical;
            }
            button {
                background: #667eea;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                font-size: 14px;
            }
            button:hover {
                background: #5568d3;
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 6px;
                border-left: 4px solid #667eea;
                display: none;
            }
            .results.show {
                display: block;
            }
            .results pre {
                overflow-x: auto;
                background: white;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            .loading {
                color: #667eea;
                font-weight: 600;
            }
            .error {
                color: #d32f2f;
                background: #ffebee;
                padding: 10px;
                border-radius: 4px;
                margin-top: 10px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Requirement Analyzer - Test Page</h1>
            
            <div class="form-group">
                <label>Requirements Text</label>
                <textarea id="requirements" placeholder="Enter your requirements here...
Example:
- Users should be able to login with email
- System must validate password strength
- All data must be encrypted"></textarea>
            </div>

            <div class="form-group">
                <label>Format Type</label>
                <select id="format">
                    <option value="free_text">Free Text</option>
                    <option value="user_story">User Story</option>
                    <option value="use_case">Use Case</option>
                </select>
            </div>

            <button onclick="analyzeRequirements()">Analyze Requirements</button>

            <div id="error" class="error"></div>

            <div id="results" class="results">
                <h2>Analysis Results</h2>
                <pre id="resultsContent"></pre>
            </div>
        </div>

        <script>
            async function analyzeRequirements() {
                const requirements = document.getElementById('requirements').value;
                const format = document.getElementById('format').value;
                const errorDiv = document.getElementById('error');
                const resultsDiv = document.getElementById('results');
                
                if (!requirements.trim()) {
                    errorDiv.textContent = 'Please enter requirements';
                    errorDiv.style.display = 'block';
                    return;
                }

                errorDiv.style.display = 'none';
                const originalText = document.querySelector('button').textContent;
                document.querySelector('button').textContent = 'Analyzing...';

                try {
                    const formData = new FormData();
                    formData.append('text', requirements);
                    formData.append('format', format);

                    const response = await fetch('/api/v3/generate', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error('Analysis failed: ' + response.statusText);
                    }

                    const data = await response.json();
                    document.getElementById('resultsContent').textContent = JSON.stringify(data, null, 2);
                    resultsDiv.classList.add('show');
                } catch (error) {
                    errorDiv.textContent = 'Error: ' + error.message;
                    errorDiv.style.display = 'block';
                } finally {
                    document.querySelector('button').textContent = originalText;
                }
            }
        </script>
    </body>
    </html>
    """


@router.get("/testgen", response_class=HTMLResponse)
async def test_testgen():
    """Test generator page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Test Generator Test</title>
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
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            h1 { color: #764ba2; margin-bottom: 20px; }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }
            textarea, input, select {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-family: monospace;
                font-size: 13px;
            }
            textarea {
                min-height: 200px;
            }
            button {
                background: #764ba2;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            }
            button:hover {
                background: #633f7f;
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 6px;
                border-left: 4px solid #764ba2;
                display: none;
            }
            .results.show {
                display: block;
            }
            .results pre {
                overflow-x: auto;
                background: white;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            .error {
                color: #d32f2f;
                background: #ffebee;
                padding: 10px;
                border-radius: 4px;
                margin-top: 10px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧬 Test Case Generator - Test Page</h1>
            
            <div class="form-group">
                <label>Requirements Text</label>
                <textarea id="requirements" placeholder="Enter requirements for test generation...
Example:
- User login functionality
- Password validation
- Session management"></textarea>
            </div>

            <div class="form-group">
                <label>Format Type</label>
                <select id="format">
                    <option value="free_text">Free Text</option>
                    <option value="user_story">User Story</option>
                    <option value="use_case">Use Case</option>
                </select>
            </div>

            <button onclick="generateTestCases()">Generate Test Cases</button>

            <div id="error" class="error"></div>

            <div id="results" class="results">
                <h2>Generated Test Cases</h2>
                <pre id="resultsContent"></pre>
            </div>
        </div>

        <script>
            async function generateTestCases() {
                const requirements = document.getElementById('requirements').value;
                const format = document.getElementById('format').value;
                const errorDiv = document.getElementById('error');
                const resultsDiv = document.getElementById('results');
                
                if (!requirements.trim()) {
                    errorDiv.textContent = 'Please enter requirements';
                    errorDiv.style.display = 'block';
                    return;
                }

                errorDiv.style.display = 'none';
                const originalText = document.querySelector('button').textContent;
                document.querySelector('button').textContent = 'Generating...';

                try {
                    const formData = new FormData();
                    formData.append('requirements', requirements);

                    const response = await fetch('/api/v2/test-generation/generate-test-cases', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error('Generation failed: ' + response.statusText);
                    }

                    const data = await response.json();
                    document.getElementById('resultsContent').textContent = JSON.stringify(data, null, 2);
                    resultsDiv.classList.add('show');
                } catch (error) {
                    errorDiv.textContent = 'Error: ' + error.message;
                    errorDiv.style.display = 'block';
                } finally {
                    document.querySelector('button').textContent = originalText;
                }
            }
        </script>
    </body>
    </html>
    """


@router.get("/unified")
async def test_unified():
    """Redirect to unified UI"""
    unified_file = PROJECT_ROOT / "templates" / "unified_ui.html"
    if unified_file.exists():
        return FileResponse(unified_file, media_type="text/html")
    return HTMLResponse("<h1>Unified UI not found</h1>", status_code=404)


@router.get("/comparison", response_class=HTMLResponse)
async def test_comparison():
    """Comparison tool page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Analyzer vs Test Generator Comparison</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: #f5f5f5;
                font-family: monospace;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            h1 { color: #4facfe; margin-bottom: 20px; }
            .form-group {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
            }
            textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-family: monospace;
                min-height: 150px;
            }
            button {
                background: #4facfe;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                margin-top: 10px;
            }
            button:hover {
                background: #3d92d4;
            }
            .comparison-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 20px;
            }
            .panel {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .panel h2 {
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #ddd;
            }
            .panel.analyzer h2 {
                color: #667eea;
            }
            .panel.testgen h2 {
                color: #764ba2;
            }
            .results-content {
                background: #f9f9f9;
                padding: 15px;
                border-radius: 6px;
                max-height: 400px;
                overflow-y: auto;
                font-size: 12px;
                line-height: 1.5;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .loading {
                color: #4facfe;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚖️ Analyzer vs Test Generator - Comparison Tool</h1>
            
            <div class="form-group">
                <label>Test Requirements (will be sent to both systems)</label>
                <textarea id="requirements" placeholder="Enter requirements here..."></textarea>
                <button onclick="compareResults()">Compare Both Systems</button>
            </div>

            <div class="comparison-grid">
                <div class="panel analyzer">
                    <h2>📊 Requirement Analyzer Results</h2>
                    <div id="analyzerResults" class="results-content">
                        <p class="loading">Waiting for input...</p>
                    </div>
                </div>

                <div class="panel testgen">
                    <h2>🧬 Test Generator Results</h2>
                    <div id="testgenResults" class="results-content">
                        <p class="loading">Waiting for input...</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function compareResults() {
                const requirements = document.getElementById('requirements').value;
                if (!requirements.trim()) {
                    alert('Please enter requirements');
                    return;
                }

                document.getElementById('analyzerResults').innerHTML = '<p class="loading">Analyzing...</p>';
                document.getElementById('testgenResults').innerHTML = '<p class="loading">Generating...</p>';

                try {
                    // Run both in parallel
                    const [analyzerData, testgenData] = await Promise.all([
                        runAnalyzer(requirements),
                        runTestGen(requirements)
                    ]);

                    document.getElementById('analyzerResults').innerHTML = '<pre>' + JSON.stringify(analyzerData, null, 2) + '</pre>';
                    document.getElementById('testgenResults').innerHTML = '<pre>' + JSON.stringify(testgenData, null, 2) + '</pre>';
                } catch (error) {
                    document.getElementById('analyzerResults').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
                    document.getElementById('testgenResults').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
                }
            }

            async function runAnalyzer(requirements) {
                const formData = new FormData();
                formData.append('text', requirements);
                formData.append('format', 'free_text');

                const response = await fetch('/api/v3/generate', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('Analyzer error');
                return await response.json();
            }

            async function runTestGen(requirements) {
                const formData = new FormData();
                formData.append('requirements', requirements);

                const response = await fetch('/api/v2/test-generation/generate-test-cases', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('Test Generator error');
                return await response.json();
            }
        </script>
    </body>
    </html>
    """


@router.get("/api", response_class=HTMLResponse)
async def test_api():
    """API testing page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>API Testing Tool</title>
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
            h1 { color: #333; margin-bottom: 20px; }
            .endpoints {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .endpoint {
                padding: 15px;
                border-bottom: 1px solid #eee;
                cursor: pointer;
                transition: background 0.3s;
            }
            .endpoint:hover {
                background: #f9f9f9;
            }
            .endpoint:last-child {
                border-bottom: none;
            }
            .method {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
                margin-right: 10px;
                font-size: 12px;
                color: white;
            }
            .method.get {
                background: #61affe;
            }
            .method.post {
                background: #49cc90;
            }
            .path {
                font-family: monospace;
                color: #333;
                font-weight: 600;
            }
            .description {
                color: #666;
                font-size: 13px;
                margin-top: 5px;
            }
            .test-section {
                margin-top: 20px;
                padding: 20px;
                background: white;
                border-radius: 10px;
                display: none;
            }
            .test-section.show {
                display: block;
            }
            input[type="text"], input[type="url"], textarea {
                width: 100%;
                padding: 10px;
                margin-bottom: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            textarea {
                min-height: 100px;
                font-family: monospace;
            }
            button {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }
            .response {
                margin-top: 15px;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 6px;
                border-left: 4px solid #667eea;
            }
            pre {
                overflow-x: auto;
                background: white;
                padding: 10px;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔌 API Testing Tool</h1>
            
            <div class="endpoints">
                <div class="endpoint" onclick="selectEndpoint('health')">
                    <span class="method get">GET</span>
                    <span class="path">/api/unified/health</span>
                    <div class="description">Check if all systems are online</div>
                </div>
                <div class="endpoint" onclick="selectEndpoint('analyze')">
                    <span class="method post">POST</span>
                    <span class="path">/api/v3/generate</span>
                    <div class="description">Analyze requirements</div>
                </div>
                <div class="endpoint" onclick="selectEndpoint('testgen')">
                    <span class="method post">POST</span>
                    <span class="path">/api/v2/test-generation/generate-test-cases</span>
                    <div class="description">Generate test cases</div>
                </div>
                <div class="endpoint" onclick="selectEndpoint('unified')">
                    <span class="method post">POST</span>
                    <span class="path">/api/unified/generate</span>
                    <div class="description">Run both systems</div>
                </div>
                <div class="endpoint" onclick="selectEndpoint('docs')">
                    <span class="method get">GET</span>
                    <span class="path">/docs</span>
                    <div class="description">Interactive API documentation (Swagger)</div>
                </div>
            </div>

            <div id="testSection" class="test-section">
                <h2>Test API Call</h2>
                <div>
                    <label>Request Body (JSON)</label>
                    <textarea id="payload">{}</textarea>
                </div>
                <button onclick="callAPI()">Send Request</button>
                <div id="response"></div>
            </div>
        </div>

        <script>
            let currentEndpoint = null;

            function selectEndpoint(endpoint) {
                currentEndpoint = endpoint;
                document.getElementById('testSection').classList.add('show');

                const examples = {
                    health: '{}',
                    analyze: '{"text": "Users can login", "format": "free_text"}',
                    testgen: '{"requirements": "System validates password"}',
                    unified: '{"text": "User registration", "format": "free_text", "analyze": true, "generate": true}',
                    docs: ''
                };

                if (endpoint === 'docs') {
                    window.open('/docs', '_blank');
                    return;
                }

                document.getElementById('payload').value = examples[endpoint];
            }

            async function callAPI() {
                const payload = document.getElementById('payload').value;
                const responseDiv = document.getElementById('response');

                if (!currentEndpoint) {
                    responseDiv.innerHTML = '<div class="response" style="color: red;">Select an endpoint first</div>';
                    return;
                }

                try {
                    const endpoints = {
                        health: '/api/unified/health',
                        analyze: '/api/v3/generate',
                        testgen: '/api/v2/test-generation/generate-test-cases',
                        unified: '/api/unified/generate'
                    };

                    const response = await fetch(endpoints[currentEndpoint], {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: payload
                    });

                    const data = await response.json();
                    responseDiv.innerHTML = `
                        <div class="response">
                            <strong>Status: ${response.status} ${response.statusText}</strong>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        </div>
                    `;
                } catch (error) {
                    responseDiv.innerHTML = `<div class="response" style="color: red;"><strong>Error:</strong> ${error.message}</div>`;
                }
            }
        </script>
    </body>
    </html>
    """
