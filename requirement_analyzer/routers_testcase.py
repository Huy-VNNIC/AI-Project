"""
Test Case Generation Routes
Tích hợp vào requirement_analyzer.api
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
import json
from datetime import datetime
from requirement_analyzer.file_util import RequirementFileParser

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
                background: linear-gradient(135deg, #0f766e 0%, #06b6d4 50%, #0369a1 100%);
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
                color: #0369a1;
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
                color: #0369a1;
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
                border-color: #0369a1;
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
                background: #0369a1;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s;
            }
            button:hover {
                background: #0d7377;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .results {
                display: none;
                margin-top: 20px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 8px;
                border-left: 4px solid #0369a1;
            }
            .results.show {
                display: block;
            }
            .results h3 {
                color: #0369a1;
                margin-bottom: 15px;
            }
            .test-case {
                background: white;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 6px;
                border-left: 4px solid #0369a1;
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
                color: #0369a1;
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


@router.get("/testcase/upload", response_class=HTMLResponse)
async def testcase_upload_page():
    """File upload page for requirements"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload Requirements</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: linear-gradient(135deg, #0f766e 0%, #06b6d4 50%, #0369a1 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
                min-height: 100vh;
                padding: 20px;
            }
            .container { max-width: 1000px; margin: 0 auto; }
            .header {
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .header h1 { color: #0369a1; font-size: 32px; margin-bottom: 10px; }
            .panel {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 20px;
            }
            .upload-zone {
                border: 3px dashed #0369a1;
                border-radius: 12px;
                padding: 40px;
                text-align: center;
                background: #f9f9f9;
                cursor: pointer;
                transition: all 0.3s;
            }
            .upload-zone:hover {
                background: #e3f2fd;
                border-color: #0d7377;
            }
            .upload-zone p { color: #666; margin: 10px 0; }
            input[type="file"] { display: none; }
            button {
                padding: 12px 24px;
                background: #0369a1;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                margin-top: 20px;
                transition: all 0.3s;
            }
            button:hover { background: #0d7377; }
            .results {
                display: none;
                margin-top: 20px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 8px;
            }
            .results.show { display: block; }
            .loading { text-align: center; color: #0369a1; }
            .requirement-item {
                background: white;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 6px;
                border-left: 4px solid #0369a1;
            }
            .requirement-item h4 { color: #333; margin-bottom: 8px; }
            .test-case-list {
                margin-top: 15px;
                max-height: 300px;
                overflow-y: auto;
                background: #f3f3f3;
                padding: 10px;
                border-radius: 6px;
            }
            .test-case { font-size: 12px; color: #666; padding: 5px; border-bottom: 1px solid #ddd; }
            .stat-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-top: 15px; }
            .stat { background: #e3f2fd; padding: 15px; border-radius: 6px; }
            .stat h3 { color: #0369a1; font-size: 24px; }
            .stat p { color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📄 Upload Requirements File</h1>
                <p>Upload requirements file and generate detailed test cases from each requirement</p>
            </div>

            <div class="panel">
                <h2>📥 Upload Requirements File</h2>
                <div class="upload-zone" onclick="document.getElementById('fileInput').click()">
                    <p style="font-size: 32px;">📁</p>
                    <p><strong>Click to upload</strong> or drag & drop</p>
                    <p style="font-size: 12px;">Supported: <strong>TXT, CSV, MD, DOCX</strong></p>
                </div>
                <input type="file" id="fileInput" accept=".txt,.csv,.md,.markdown,.docx" onchange="handleFileUpload(event)">
                
                <div style="margin-top: 15px;">
                    <label>Max Test Cases per Requirement:</label>
                    <input type="number" id="maxTests" value="10" min="1" max="50" style="width: 100px; padding: 8px;">
                </div>

                <button onclick="analyzeFile()">Analyze & Generate Test Cases</button>
            </div>

            <div id="results" class="results">
                <h2>Analysis Results</h2>
                <div id="resultsContent"></div>
            </div>
        </div>

        <script>
            let uploadedFile = null;

            function handleFileUpload(event) {
                uploadedFile = event.target.files[0];
                console.log('File selected:', uploadedFile.name);
            }

            async function analyzeFile() {
                if (!uploadedFile) {
                    alert('Please select a file');
                    return;
                }

                const formData = new FormData();
                formData.append('file', uploadedFile);
                formData.append('max_tests', document.getElementById('maxTests').value);

                document.getElementById('results').classList.add('show');
                document.getElementById('resultsContent').innerHTML = '<div class="loading"><p>🔄 Analyzing requirements...</p></div>';

                try {
                    const response = await fetch('/api/v3/test-generation/analyze-file-detailed', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.detail || 'Failed to analyze file');
                    }

                    displayDetailedResults(data);
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('resultsContent').innerHTML = 
                        '<p style="color: red;">❌ Error: ' + error.message + '</p>';
                }
            }

            function displayDetailedResults(data) {
                // Store file for export functions
                window.currentFile = uploadedFile;
                window.detailedData = data;
                
                let totalTestCases = 0;
                let avgConfidence = 0;
                let confCount = 0;

                data.detailed.forEach(item => {
                    if (item.test_cases_count) {
                        totalTestCases += item.test_cases_count;
                    }
                    if (item.nlp_confidence) {
                        avgConfidence += item.nlp_confidence;
                        confCount++;
                    }
                });

                // Calculate statistics
                if (confCount > 0) {
                    avgConfidence = avgConfidence / confCount;
                }

                let html = `
                    <div class="stat-row" style="margin-bottom: 30px;">
                        <div class="stat">
                            <h3>${data.detailed.length}</h3>
                            <p>Requirements Analyzed</p>
                        </div>
                        <div class="stat">
                            <h3>${totalTestCases}</h3>
                            <p>Test Cases Generated</p>
                        </div>
                        <div class="stat">
                            <h3>${(avgConfidence * 100).toFixed(1)}%</h3>
                            <p>Avg NLP Confidence</p>
                        </div>
                    </div>
                `;

                // Display each requirement with detailed analysis
                data.detailed.forEach((item, idx) => {
                    if (item.error) {
                        html += `
                            <div class="requirement-item" style="border-color: #f44336;">
                                <h4>Requirement ${item.index}</h4>
                                <p style="color: #666;">${item.requirement}</p>
                                <p style="color: #f44336; font-size: 12px;">Error: ${item.error}</p>
                            </div>
                        `;
                        return;
                    }

                    html += `
                        <div class="requirement-item">
                            <h4>Requirement ${item.index}</h4>
                            <p style="color: #333; font-weight: 500; margin-bottom: 8px;">
                                "${item.requirement}"
                            </p>
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin: 10px 0; font-size: 12px;">
                                <div style="background: #e3f2fd; padding: 8px; border-radius: 4px;">
                                    <strong style="color: #0369a1;">Words:</strong> ${item.word_count}
                                </div>
                                <div style="background: #e3f2fd; padding: 8px; border-radius: 4px;">
                                    <strong style="color: #0369a1;">Chars:</strong> ${item.character_count}
                                </div>
                                <div style="background: #e3f2fd; padding: 8px; border-radius: 4px;">
                                    <strong style="color: #0369a1;">Confidence:</strong> ${(item.nlp_confidence * 100).toFixed(1)}%
                                </div>
                                <div style="background: #e3f2fd; padding: 8px; border-radius: 4px;">
                                    <strong style="color: #0369a1;">Test Cases:</strong> ${item.test_cases_count}
                                </div>
                            </div>

                            <div class="test-case-list">
                                <strong>Generated Test Cases (${item.test_cases.length}):</strong>
                                ${item.test_cases.map((tc, i) => `
                                    <div class="test-case" data-tc-id="${tc.id}" style="padding: 12px; margin: 8px 0; background: white; border-radius: 4px; border-left: 4px solid #0369a1; cursor: pointer; transition: all 0.3s;" 
                                         onmouseover="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)'" 
                                         onmouseout="this.style.boxShadow='none'"
                                         onclick="showTestCaseDetailsV2('${tc.id}')">
                                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1fr; gap: 8px; font-size: 11px;">
                                            <div><strong>ID:</strong> <span style="color: #0369a1; font-weight: bold;">${tc.id}</span></div>
                                            <div><strong>Type:</strong> ${tc.type || tc.scenario_type}</div>
                                            <div><strong>Priority:</strong> <span style="color: ${tc.priority === 'CRITICAL' ? '#d32f2f' : tc.priority === 'HIGH' ? '#f57c00' : '#1976d2'};">${tc.priority}</span></div>
                                            <div><strong>Steps:</strong> ${tc.steps_count || tc.steps?.length || 0}</div>
                                            <div><strong>Confidence:</strong> ${(tc.confidence * 100).toFixed(0)}%</div>
                                        </div>
                                        <div style="margin-top: 6px; color: #333; font-weight: 500;" title="${tc.title}">${tc.title}</div>
                                        <div style="margin-top: 4px; color: #999; font-size: 11px;">
                                            Effort: ${tc.estimated_effort_hours?.toFixed(1) || '1.0'}h | Confidence: ${(tc.confidence * 100).toFixed(0)}%
                                        </div>
                                        <div style="margin-top: 6px; font-size: 11px; color: #0369a1; text-decoration: underline;">
                                            Click to view full details
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                });

                html += `
                    <div style="margin-top: 30px;">
                        <h3 style="margin-bottom: 15px; color: #0369a1;">Export Options</h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <button onclick="exportPytest()" style="background: #FF9800; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; color: white;">
                                Export Pytest
                            </button>
                            <button onclick="exportGherkin()" style="background: #9C27B0; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; color: white;">
                                Export Gherkin
                            </button>
                            <button onclick="exportRTM()" style="background: #00BCD4; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; color: white;">
                                Export RTM (CSV)
                            </button>
                            <button onclick="exportJSON()" style="background: #4CAF50; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; color: white;">
                                Export JSON
                            </button>
                            <button onclick="exportHtmlReport()" style="background: #2196F3; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; color: white;">
                                Export HTML Report
                            </button>
                            <button onclick="exportPdfReport()" style="background: #E91E63; padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; color: white;">
                                Export PDF Report
                            </button>
                        </div>
                    </div>
                `;

                document.getElementById('resultsContent').innerHTML = html;
                
                // Store test case data globally for modal display
                window.testCasesData = {};
                data.detailed.forEach((req, idx) => {
                    if (req.test_cases) {
                        req.test_cases.forEach(tc => {
                            window.testCasesData[tc.id] = {
                                ...tc,
                                requirement: req.requirement,
                                requirement_index: req.index
                            };
                        });
                    }
                });
                
                window.detailedData = data;
            }

            function downloadDetailedJSON() {
                const json = JSON.stringify(window.detailedData, null, 2);
                const blob = new Blob([json], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'requirements_analysis_detailed.json';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }

            function downloadDetailedCSV() {
                let csv = 'Req Index,Requirement,Word Count,Char Count,NLP Confidence,Test Cases Count,Avg Effort Hours\\n';
                
                window.detailedData.detailed.forEach(item => {
                    if (!item.error) {
                        csv += `"${item.index}","${item.requirement.replace(/"/g, '\\"')}","${item.word_count}","${item.character_count}","${(item.nlp_confidence*100).toFixed(1)}%","${item.test_cases_count}","${item.avg_effort.toFixed(2)}"\\n`;
                    }
                });

                const blob = new Blob([csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'requirements_analysis.csv';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }

            // Show detailed test case information in modal (Fixed version)
            function showTestCaseDetailsV2(testCaseId) {
                const modal = document.getElementById('testCaseModal');
                if (!modal) {
                    console.error('Modal not found');
                    return;
                }

                // Get test case data from global storage
                const testCase = window.testCasesData[testCaseId];
                if (!testCase) {
                    console.error('Test case not found:', testCaseId);
                    return;
                }

                // Parse test case data safely
                let preconditions = testCase.preconditions || [];
                let testData = testCase.test_data || {};
                let steps = testCase.steps || [];
                let validation = testCase.validation || [];
                let expectedResult = testCase.expected_result || '';

                // Build HTML
                let html = `
                    <div class="modal-content">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0369a1; padding-bottom: 12px; margin-bottom: 16px;">
                            <div style="flex: 1;">
                                <h2 style="margin: 0; color: #333;">${testCase.title || 'Test Case'}</h2>
                                <p style="margin: 4px 0; color: #666; font-size: 13px;">ID: <strong>${testCaseId}</strong></p>
                                <p style="margin: 4px 0; color: #999; font-size: 12px;">From: ${testCase.requirement}</p>
                            </div>
                            <button onclick="closeTestCaseModal()" style="background: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 16px; white-space: nowrap;">Close</button>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; margin-bottom: 20px;">
                            <div style="background: #e3f2fd; padding: 12px; border-radius: 4px;">
                                <strong style="color: #0369a1;">Type:</strong><br>
                                <span style="font-size: 14px; font-weight: bold;">${testCase.type || 'unknown'}</span>
                            </div>
                            <div style="background: #fff3e0; padding: 12px; border-radius: 4px;">
                                <strong style="color: #f57c00;">Priority:</strong><br>
                                <span style="font-size: 14px; font-weight: bold; color: ${testCase.priority === 'CRITICAL' ? '#d32f2f' : testCase.priority === 'HIGH' ? '#f57c00' : '#1976d2'};">${testCase.priority || 'MEDIUM'}</span>
                            </div>
                            <div style="background: #f3e5f5; padding: 12px; border-radius: 4px;">
                                <strong style="color: #7b1fa2;">Confidence:</strong><br>
                                <span style="font-size: 14px; font-weight: bold;">${((testCase.confidence || 0) * 100).toFixed(1)}%</span>
                            </div>
                            <div style="background: #e8f5e9; padding: 12px; border-radius: 4px;">
                                <strong style="color: #388e3c;">Effort:</strong><br>
                                <span style="font-size: 14px; font-weight: bold;">${(testCase.estimated_effort_hours || 1.0).toFixed(1)}h</span>
                            </div>
                        </div>

                        <!-- Preconditions -->
                        <div style="margin-bottom: 20px; border: 1px solid #ddd; border-radius: 6px; padding: 12px; background: #f9f9f9;">
                            <h3 style="margin: 0 0 10px 0; color: #333; font-size: 16px;">Preconditions</h3>
                            <ul style="margin: 0; padding-left: 20px; color: #555;">
                                ${preconditions && preconditions.length > 0 ? 
                                    preconditions.map(p => `<li style="margin: 4px 0; font-size: 13px;">${p}</li>`).join('') :
                                    '<li style="color: #999;">None specified</li>'
                                }
                            </ul>
                        </div>

                        <!-- Test Data -->
                        <div style="margin-bottom: 20px; border: 1px solid #ddd; border-radius: 6px; padding: 12px; background: #f9f9f9;">
                            <h3 style="margin: 0 0 10px 0; color: #333; font-size: 16px;">Test Data</h3>
                            ${Object.keys(testData).length > 0 ? `
                                <table style="width: 100%; font-size: 12px; border-collapse: collapse;">
                                    <tr style="background: #e3f2fd; border-bottom: 1px solid #ddd;">
                                        <th style="padding: 8px; text-align: left; font-weight: bold; color: #0369a1;">Key</th>
                                        <th style="padding: 8px; text-align: left; font-weight: bold; color: #0369a1;">Value</th>
                                    </tr>
                                    ${Object.entries(testData).map(([key, value]) => `
                                        <tr style="border-bottom: 1px solid #eee;">
                                            <td style="padding: 8px; color: #333;"><strong>${key}</strong></td>
                                            <td style="padding: 8px; color: #666;"><code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">${typeof value === 'string' ? value : JSON.stringify(value)}</code></td>
                                        </tr>
                                    `).join('')}
                                </table>
                            ` : '<p style="color: #999; font-size: 13px;">No test data specified</p>'}
                        </div>

                        <!-- Steps -->
                        <div style="margin-bottom: 20px; border: 1px solid #ddd; border-radius: 6px; padding: 12px; background: #f9f9f9;">
                            <h3 style="margin: 0 0 10px 0; color: #333; font-size: 16px;">Test Steps</h3>
                            ${steps && steps.length > 0 ? `
                                <ol style="margin: 0; padding-left: 20px; color: #555;">
                                    ${steps.map((step, idx) => `
                                        <li style="margin: 8px 0; font-size: 13px;">
                                            <strong>Action:</strong> ${typeof step === 'string' ? step : step.action || 'N/A'}<br>
                                            ${step.expected ? `<strong>Expected:</strong> ${step.expected}` : ''}
                                        </li>
                                    `).join('')}
                                </ol>
                            ` : '<p style="color: #999; font-size: 13px;">No steps specified</p>'}
                        </div>

                        <!-- Expected Result -->
                        <div style="margin-bottom: 20px; border: 1px solid #ddd; border-radius: 6px; padding: 12px; background: #e8f5e9;">
                            <h3 style="margin: 0 0 10px 0; color: #388e3c; font-size: 16px;">Expected Result</h3>
                            <p style="margin: 0; color: #333; font-size: 13px; line-height: 1.6; white-space: pre-wrap;">${expectedResult || 'Not specified'}</p>
                        </div>

                        <!-- Validation Criteria -->
                        <div style="border: 1px solid #ddd; border-radius: 6px; padding: 12px; background: #f9f9f9;">
                            <h3 style="margin: 0 0 10px 0; color: #333; font-size: 16px;">Validation Criteria</h3>
                            <ul style="margin: 0; padding-left: 20px; color: #555;">
                                ${validation && validation.length > 0 ? 
                                    validation.map(v => `<li style="margin: 4px 0; font-size: 13px;">✓ ${v}</li>`).join('') :
                                    '<li style="color: #999;">No validation criteria specified</li>'
                                }
                            </ul>
                        </div>
                    </div>
                `;

                document.getElementById('modalBody').innerHTML = html;
                modal.style.display = 'flex';
            }

            function closeTestCaseModal() {
                document.getElementById('testCaseModal').style.display = 'none';
            }

            // Close modal when clicking outside
            window.onclick = function(event) {
                const modal = document.getElementById('testCaseModal');
                if (modal && event.target === modal) {
                    modal.style.display = 'none';
                }
            }

            // ===== EXPORT FUNCTIONS =====

            function getUploadedFile() {
                const fileInput = document.querySelector('input[type="file"]');
                return fileInput?.files[0];
            }

            async function exportWithFormat(format) {
                const file = getUploadedFile();
                if (!file) {
                    alert('Please upload a file first');
                    return;
                }

                const maxTests = document.getElementById('maxTests')?.value || 8;
                const formData = new FormData();
                formData.append('file', file);
                formData.append('max_tests', maxTests);

                const endpoints = {
                    'pytest': '/api/v3/test-generation/export-pytest',
                    'gherkin': '/api/v3/test-generation/export-gherkin',
                    'rtm': '/api/v3/test-generation/export-rtm',
                    'json': '/api/v3/test-generation/export-json'
                };

                const fileNames = {
                    'pytest': 'test_hotel_booking_generated.py',
                    'gherkin': 'hotel_booking_generated.feature',
                    'rtm': 'requirements_traceability_matrix_generated.csv',
                    'json': 'test_cases_detailed_generated.json'
                };

                try {
                    const response = await fetch(endpoints[format], {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.message || 'Export failed');
                    }

                    // Download file
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = fileNames[format];
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(url);

                    alert(`✓ ${format.toUpperCase()} exported successfully!`);
                } catch (error) {
                    alert(`✗ Export failed: ${error.message}`);
                    console.error(error);
                }
            }

            function exportPytest() {
                exportWithFormat('pytest');
            }

            function exportGherkin() {
                exportWithFormat('gherkin');
            }

            function exportRTM() {
                exportWithFormat('rtm');
            }

            function exportJSON() {
                exportWithFormat('json');
            }

            function exportHtmlReport() {
                if (!window.currentFile) {
                    alert('⚠️ Please analyze a file first');
                    return;
                }
                exportReportWithFormat('html');
            }

            function exportPdfReport() {
                if (!window.currentFile) {
                    alert('⚠️ Please analyze a file first');
                    return;
                }
                exportReportWithFormat('pdf');
            }

            async function exportReportWithFormat(format) {
                try {
                    if (!window.currentFile) {
                        alert('Please analyze file first');
                        return;
                    }
                    
                    const formData = new FormData();
                    formData.append('file', window.currentFile);
                    
                    const maxTests = parseInt(document.getElementById('maxTests').value) || 8;
                    
                    let endpoint;
                    let filename;
                    
                    if (format === 'html') {
                        endpoint = `/api/v3/test-generation/export-html-report?max_tests=${maxTests}`;
                        filename = `test_report_${new Date().toISOString().slice(0, 10)}.html`;
                    } else if (format === 'pdf') {
                        endpoint = `/api/v3/test-generation/export-pdf-report?max_tests=${maxTests}`;
                        filename = `test_report_${new Date().toISOString().slice(0, 10)}.pdf`;
                    }
                    
                    console.log('Exporting to:', endpoint);
                    
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });
                    
                    console.log('Response status:', response.status);
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error('Error response:', errorText);
                        throw new Error(`Export failed: ${response.status} ${response.statusText} - ${errorText.substring(0, 100)}`);
                    }
                    
                    const blob = await response.blob();
                    if (blob.size === 0) {
                        throw new Error('Empty response received');
                    }
                    
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    
                    alert(`✓ ${format.toUpperCase()} report exported successfully!`);
                } catch (error) {
                    alert(`✗ Export failed: ${error.message}`);
                    console.error(error);
                }
            }

            // Legacy compatibility
            function downloadDetailedJSON() {
                exportJSON();
            }

            function downloadDetailedCSV() {
                exportRTM();
            }
        </script>

        <!-- Test Case Details Modal -->
        <div id="testCaseModal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); flex-direction: column; justify-content: center; align-items: center;">
            <div style="width: 90%; max-width: 1000px; max-height: 90vh; background-color: white; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); overflow-y: auto; padding: 20px;">
                <div id="modalBody"></div>
            </div>
        </div>
    </body>
    </html>
    """


@router.post("/api/v2/test-generation/analyze-file")
async def analyze_requirement_file(file: UploadFile = File(...), max_tests: int = 10):
    """Analyze uploaded requirement file and generate test cases"""
    try:
        from requirement_analyzer.task_gen.test_case_generator_v2 import AITestCaseGeneratorV2
        
        content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        if file_type not in ['txt', 'csv']:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Parse file
        parser = RequirementFileParser()
        requirements = parser.parse_file(content.decode('utf-8'), file_type)
        
        if not requirements:
            return JSONResponse(
                {
                    "status": "error",
                    "message": "No requirements found in file"
                },
                status_code=400
            )
        
        # Analyze each requirement
        generator = AITestCaseGeneratorV2()
        analysis = []
        total_tests = 0
        confidences = []
        
        for req in requirements:
            if not req.strip():
                continue
            
            try:
                # Generate test cases for this requirement
                result = generator.generate([req], max_test_cases=max_tests, confidence_threshold=0.4)
                
                test_cases = result.get('test_cases', [])
                avg_conf = result.get('summary', {}).get('avg_confidence', 0)
                
                analysis.append({
                    'requirement': req[:150],
                    'nlp_confidence': avg_conf,
                    'test_cases': [
                        {
                            'id': tc.get('id'),
                            'title': tc.get('title'),
                            'scenario_type': tc.get('scenario_type'),
                            'priority': tc.get('priority'),
                            'confidence': tc.get('confidence', {}).get('overall_score', 0)
                        }
                        for tc in test_cases
                    ]
                })
                total_tests += len(test_cases)
                confidences.append(avg_conf)
            except Exception as e:
                print(f"Error analyzing requirement: {e}")
                continue
        
        if not analysis:
            return JSONResponse(
                {
                    "status": "error",
                    "message": "Could not analyze any requirements"
                },
                status_code=400
            )
        
        return {
            "status": "success",
            "total_requirements": len(analysis),
            "total_test_cases": total_tests,
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "analysis": analysis
        }
    
    except Exception as e:
        return JSONResponse(
            {
                "status": "error",
                "message": str(e)
            },
            status_code=500
        )


@router.post("/api/v2/test-generation/analyze-file-detailed")
async def analyze_file_detailed(file: UploadFile = File(...), max_tests: int = 10):
    """Analyze file with detailed breakdown per requirement"""
    try:
        from requirement_analyzer.task_gen.test_case_generator_v2 import AITestCaseGeneratorV2
        import json
        
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        # Support: txt, csv, md, markdown, docx
        supported_types = ['txt', 'csv', 'md', 'markdown', 'docx']
        if file_type not in supported_types:
            raise ValueError(f"Unsupported file type: .{file_type}. Supported: TXT, CSV, MD, DOCX")
        
        # Parse file
        parser = RequirementFileParser()
        try:
            if file_type == 'docx':
                # DOCX files need binary content
                requirements = parser.parse_file(None, file_type, binary_content=file_content)
            else:
                # TXT, CSV, MD files can use string content
                requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        except ValueError as e:
            return JSONResponse(
                {"status": "error", "message": str(e)},
                status_code=400
            )
        
        if not requirements:
            return JSONResponse(
                {"status": "error", "message": "No requirements found in file"},
                status_code=400
            )
        
        # Detailed analysis
        generator = AITestCaseGeneratorV2()
        detailed_analysis = []
        skipped_analysis = []
        
        for idx, req in enumerate(requirements, 1):
            if not req.strip() or len(req.split()) < 3:
                skipped_analysis.append({
                    'index': idx,
                    'requirement': req,
                    'reason': 'Too short (less than 3 words)'
                })
                continue
            
            try:
                result = generator.generate([req], max_test_cases=max_tests, confidence_threshold=0.4)
                test_cases = result.get('test_cases', [])
                nlp_confidence = result.get('summary', {}).get('avg_confidence', 0)
                
                # Skip requirements with 0% confidence (couldn't generate meaningful test cases)
                if not test_cases or nlp_confidence == 0:
                    skipped_analysis.append({
                        'index': idx,
                        'requirement': req,
                        'reason': 'Low NLP confidence - unable to generate meaningful test cases',
                        'nlp_confidence': nlp_confidence
                    })
                    continue
                
                # Extract NLP parsing details
                req_words = req.split()
                
                detailed_analysis.append({
                    'index': idx,
                    'requirement': req,
                    'word_count': len(req_words),
                    'character_count': len(req),
                    'nlp_confidence': nlp_confidence,
                    'test_cases_count': len(test_cases),
                    'avg_effort': result.get('summary', {}).get('avg_effort_hours', 0),
                    'test_cases': [
                        {
                            'id': tc.get('id'),
                            'title': tc.get('title'),
                            'scenario_type': tc.get('scenario_type'),
                            'priority': tc.get('priority'),
                            'estimated_effort_hours': tc.get('estimated_effort_hours', 0),
                            'confidence': tc.get('confidence', {}).get('overall_score', 0),
                            'steps_count': len(tc.get('steps', []))
                        }
                        for tc in test_cases
                    ]
                })
            except Exception as e:
                skipped_analysis.append({
                    'index': idx,
                    'requirement': req,
                    'reason': f'Error during processing: {str(e)}'
                })
                continue
        
        return {
            "status": "success",
            "filename": file.filename,
            "file_type": file_type.upper(),
            "total_requirements_in_file": len(requirements),
            "total_requirements_analyzed": len(detailed_analysis),
            "total_requirements_skipped": len(skipped_analysis),
            "total_test_cases_generated": sum(r['test_cases_count'] for r in detailed_analysis),
            "avg_nlp_confidence": sum(r['nlp_confidence'] for r in detailed_analysis) / len(detailed_analysis) if detailed_analysis else 0,
            "detailed": detailed_analysis,
            "skipped_requirements": skipped_analysis if skipped_analysis else None
        }
    
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


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
            h1 { color: #0369a1; margin-bottom: 20px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; font-weight: 600; }
            textarea, input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-family: monospace; }
            button { background: #0369a1; color: white; padding: 12px 30px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
            button:hover { background: #0d7377; }
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
                background: linear-gradient(135deg, #0369a1 0%, #764ba2 100%);
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
            .card h2 { color: #0369a1; margin-bottom: 10px; }
            .card p { color: #666; font-size: 14px; margin-bottom: 20px; }
            .card button {
                display: inline-block;
                padding: 10px 20px;
                background: #0369a1;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            }
            .card button:hover { background: #0d7377; }
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
            h1 { color: #0369a1; margin-bottom: 30px; }
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
            .stat-number { font-size: 32px; font-weight: 700; color: #0369a1; margin-bottom: 10px; }
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


@router.post("/api/v3/test-generation/analyze-file-detailed")
async def analyze_file_detailed_v3(file: UploadFile = File(...), max_tests: int = 8):
    """
    PRODUCTION-GRADE Test Case Analysis - v3
    Generates REAL, ACTIONABLE test cases using smart requirement understanding
    
    Key improvements over v2:
    - Concrete test data (not generic)  
    - Real input/output pairs
    - Boundary value analysis with actual tests
    - State machine test generation
    - Requirement quality validation
    - Smart deduplication
    """
    try:
        from requirement_analyzer.task_gen.test_case_generator_v3 import AITestCaseGeneratorV3
        
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        # Support: txt, csv, md, markdown, docx
        supported_types = ['txt', 'csv', 'md', 'markdown', 'docx']
        if file_type not in supported_types:
            raise ValueError(f"Unsupported file type: .{file_type}. Supported: TXT, CSV, MD, DOCX")
        
        # Parse file
        parser = RequirementFileParser()
        try:
            if file_type == 'docx':
                requirements = parser.parse_file(None, file_type, binary_content=file_content)
            else:
                requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        except ValueError as e:
            return JSONResponse(
                {"status": "error", "message": str(e)},
                status_code=400
            )
        
        if not requirements:
            return JSONResponse(
                {"status": "error", "message": "No requirements found in file"},
                status_code=400
            )
        
        # Generate using production-grade v3
        generator = AITestCaseGeneratorV3()
        v3_results = generator.generate(requirements, max_test_cases_per_req=max_tests)
        
        # Format response
        detailed_analysis = []
        skipped_analysis = []
        total_test_cases = 0
        total_confidence = 0
        
        for req_result in v3_results['results']:
            req_id = req_result['requirement_id']
            req_text = req_result['requirement_text']
            test_cases = req_result['test_cases']
            
            # Separate actionable from ambiguous
            if not req_result['is_actionable']:
                skipped_analysis.append({
                    'index': len(detailed_analysis) + len(skipped_analysis) + 1,
                    'requirement': req_text,
                    'requirement_id': req_id,
                    'reason': 'Requirement is ambiguous or unclear',
                    'quality_issues': req_result.get('quality_issues', []),
                    'note': 'Please clarify this requirement before generating tests'
                })
                continue
            
            # Process actionable requirements
            formatted_tests = []
            req_confidence = 0
            
            for tc in test_cases:
                if tc.get('type') != 'requirement_quality_check':
                    formatted_tests.append({
                        'id': tc.get('id'),
                        'title': tc.get('title'),
                        'type': tc.get('type'),
                        'priority': tc.get('priority'),
                        'confidence': round(tc.get('confidence', 0.85) * 100) / 100,
                        'preconditions': tc.get('preconditions', []),
                        'test_data': tc.get('test_data', {}),
                        'steps_count': len(tc.get('steps', [])),
                        'expected_result': tc.get('expected_result', ''),
                        'validation':tc.get('validation', [])
                    })
                    if 'confidence' in tc:
                        req_confidence += tc['confidence']
            
            if formatted_tests:
                avg_conf = req_confidence / len(formatted_tests) if formatted_tests else 0
                detailed_analysis.append({
                    'index': len(detailed_analysis) + 1,
                    'requirement_id': req_id,
                    'requirement': req_text,
                    'word_count': len(req_text.split()),
                    'character_count': len(req_text),
                    'nlp_confidence': avg_conf,
                    'test_cases_count': len(formatted_tests),
                    'test_cases': formatted_tests
                })
                total_test_cases += len(formatted_tests)
                total_confidence += avg_conf
        
        # Calculate summary
        avg_confidence = total_confidence / len(detailed_analysis) if detailed_analysis else 0
        
        return {
            "status": "success",
            "generator_version": "v3_production",
            "filename": file.filename,
            "file_type": file_type.upper(),
            "total_requirements_in_file": len(requirements),
            "total_requirements_analyzed": len(detailed_analysis),
            "total_requirements_skipped": len(skipped_analysis),
            "total_test_cases_generated": total_test_cases,
            "avg_nlp_confidence": round(avg_confidence * 100) / 100,
            "detailed": detailed_analysis,
            "skipped_requirements": skipped_analysis if skipped_analysis else None,
            "quality_metrics": {
                "ambiguous_requirements": v3_results['summary']['ambiguous_requirements'],
                "actionable_requirements": v3_results['summary']['actionable_requirements'],
                "test_cases_by_type": v3_results['summary']['test_cases_by_type'],
                "avg_test_quality_score": v3_results['summary']['avg_test_quality_score']
            }
        }
    
    except Exception as e:
        import traceback
        return JSONResponse(
            {"status": "error", "message": str(e), "traceback": traceback.format_exc()},
            status_code=500
        )


# ===== PYTEST EXPORT ENDPOINTS =====

@router.post("/api/v3/test-generation/export-pytest")
async def export_pytest_code(file: UploadFile = File(...), max_tests: int = 8):
    """
    Export test cases as executable pytest code
    Returns Python file with all test cases ready to run
    """
    try:
        from requirement_analyzer.task_gen.test_case_generator_v3 import AITestCaseGeneratorV3
        from requirement_analyzer.task_gen.pytest_export_generator import PytestExportGenerator
        from fastapi.responses import FileResponse
        import os
        import tempfile
        
        # Parse file
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        supported_types = ['txt', 'csv', 'md', 'markdown', 'docx']
        if file_type not in supported_types:
            raise ValueError(f"Unsupported file type: .{file_type}")
        
        parser = RequirementFileParser()
        if file_type == 'docx':
            requirements = parser.parse_file(None, file_type, binary_content=file_content)
        else:
            requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        
        if not requirements:
            return JSONResponse(
                {"status": "error", "message": "No requirements found"},
                status_code=400
            )
        
        # Generate test cases
        generator = AITestCaseGeneratorV3()
        test_data = generator.generate(requirements, max_test_cases_per_req=max_tests)
        
        # Export to pytest
        exporter = PytestExportGenerator(test_data)
        pytest_code = exporter.generate_pytest_file()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='_pytest.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(pytest_code)
            temp_file = f.name
        
        # Return file
        return FileResponse(
            path=temp_file,
            filename=f"test_hotel_booking_generated.py",
            media_type="text/plain"
        )
    
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


@router.post("/api/v3/test-generation/export-gherkin")
async def export_gherkin_code(file: UploadFile = File(...), max_tests: int = 8):
    """
    Export test cases as Gherkin/BDD feature files
    Returns feature file for Cucumber/BDD frameworks
    """
    try:
        from requirement_analyzer.task_gen.test_case_generator_v3 import AITestCaseGeneratorV3
        from requirement_analyzer.task_gen.pytest_export_generator import PytestExportGenerator
        from fastapi.responses import FileResponse
        import tempfile
        
        # Parse file
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        parser = RequirementFileParser()
        if file_type == 'docx':
            requirements = parser.parse_file(None, file_type, binary_content=file_content)
        else:
            requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        
        if not requirements:
            return JSONResponse(
                {"status": "error", "message": "No requirements found"},
                status_code=400
            )
        
        # Generate test cases
        generator = AITestCaseGeneratorV3()
        test_data = generator.generate(requirements, max_test_cases_per_req=max_tests)
        
        # Export to Gherkin
        exporter = PytestExportGenerator(test_data)
        gherkin_code = exporter.export_gherkin_file()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.feature',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(gherkin_code)
            temp_file = f.name
        
        # Return file
        return FileResponse(
            path=temp_file,
            filename=f"hotel_booking_generated.feature",
            media_type="text/plain"
        )
    
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


@router.post("/api/v3/test-generation/export-rtm")
async def export_rtm_matrix(file: UploadFile = File(...), max_tests: int = 8):
    """
    Export Requirements Traceability Matrix (RTM)
    Returns CSV file showing requirement-to-test mapping
    """
    try:
        from requirement_analyzer.task_gen.test_case_generator_v3 import AITestCaseGeneratorV3
        from requirement_analyzer.task_gen.pytest_export_generator import PytestExportGenerator
        from fastapi.responses import FileResponse
        import tempfile
        
        # Parse file
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        parser = RequirementFileParser()
        if file_type == 'docx':
            requirements = parser.parse_file(None, file_type, binary_content=file_content)
        else:
            requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        
        if not requirements:
            return JSONResponse(
                {"status": "error", "message": "No requirements found"},
                status_code=400
            )
        
        # Generate test cases
        generator = AITestCaseGeneratorV3()
        test_data = generator.generate(requirements, max_test_cases_per_req=max_tests)
        
        # Export to RTM
        exporter = PytestExportGenerator(test_data)
        rtm_csv = exporter.export_rtm_csv()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.csv',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(rtm_csv)
            temp_file = f.name
        
        # Return file
        return FileResponse(
            path=temp_file,
            filename=f"requirements_traceability_matrix_generated.csv",
            media_type="text/csv"
        )
    
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


@router.post("/api/v3/test-generation/export-json")
async def export_json_detailed(file: UploadFile = File(...), max_tests: int = 8):
    """
    Export all test data as detailed JSON
    Returns complete JSON with all test case details
    """
    try:
        from requirement_analyzer.task_gen.test_case_generator_v3 import AITestCaseGeneratorV3
        from requirement_analyzer.task_gen.pytest_export_generator import PytestExportGenerator
        from fastapi.responses import FileResponse
        import tempfile
        
        # Parse file
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        parser = RequirementFileParser()
        if file_type == 'docx':
            requirements = parser.parse_file(None, file_type, binary_content=file_content)
        else:
            requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        
        if not requirements:
            return JSONResponse(
                {"status": "error", "message": "No requirements found"},
                status_code=400
            )
        
        # Generate test cases
        generator = AITestCaseGeneratorV3()
        test_data = generator.generate(requirements, max_test_cases_per_req=max_tests)
        
        # Export to JSON
        exporter = PytestExportGenerator(test_data)
        json_data = exporter.export_json_detailed()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(json_data)
            temp_file = f.name
        
        # Return file
        return FileResponse(
            path=temp_file,
            filename=f"test_cases_detailed_generated.json",
            media_type="application/json"
        )
    
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


@router.post("/api/v3/test-generation/get-statistics")
async def get_export_statistics(file: UploadFile = File(...), max_tests: int = 8):
    """
    Get statistics about generated test cases
    Useful for planning and CI/CD integration
    """
    try:
        from requirement_analyzer.task_gen.test_case_generator_v3 import AITestCaseGeneratorV3
        from requirement_analyzer.task_gen.pytest_export_generator import PytestExportGenerator
        
        # Parse file
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        parser = RequirementFileParser()
        if file_type == 'docx':
            requirements = parser.parse_file(None, file_type, binary_content=file_content)
        else:
            requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        
        if not requirements:
            return JSONResponse(
                {"status": "error", "message": "No requirements found"},
                status_code=400
            )
        
        # Generate test cases
        generator = AITestCaseGeneratorV3()
        test_data = generator.generate(requirements, max_test_cases_per_req=max_tests)
        
        # Get statistics
        exporter = PytestExportGenerator(test_data)
        stats = exporter.get_statistics()
        
        return {
            "status": "success",
            "statistics": stats,
            "export_formats_available": [
                "pytest",
                "gherkin",
                "rtm",
                "json"
            ]
        }
    
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


@router.post("/api/v3/test-generation/export-html-report")
async def export_html_report(file: UploadFile = File(...), max_tests: int = 8):
    """
    Export test cases as interactive HTML report with charts and visualizations
    """
    try:
        from requirement_analyzer.task_gen.test_case_generator_v3 import AITestCaseGeneratorV3
        from requirement_analyzer.task_gen.report_generator import ReportGenerator
        from fastapi.responses import FileResponse
        import tempfile
        import os
        
        # Validate file
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        # Parse file
        file_content = await file.read()
        if not file_content:
            raise ValueError("File is empty")
            
        file_type = file.filename.split('.')[-1].lower()
        
        parser = RequirementFileParser()
        if file_type == 'docx':
            requirements = parser.parse_file(None, file_type, binary_content=file_content)
        else:
            requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        
        if not requirements:
            raise ValueError("No requirements found in file")
        
        # Generate test cases
        generator = AITestCaseGeneratorV3()
        test_data = generator.generate(requirements, max_test_cases_per_req=max_tests)
        
        # Generate HTML report
        report_gen = ReportGenerator(test_data)
        html_content = report_gen.generate_html_report()
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = os.path.join(temp_dir, f"test_report_{timestamp}.html")
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return FileResponse(
            temp_file,
            media_type="text/html",
            filename=f"test_report_{timestamp}.html",
            headers={"Content-Disposition": f"attachment; filename=test_report_{timestamp}.html"}
        )
    
    except ValueError as e:
        return JSONResponse(
            {"status": "error", "detail": str(e)},
            status_code=400
        )
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"Export HTML error: {error_msg}\n{traceback.format_exc()}")
        return JSONResponse(
            {"status": "error", "detail": error_msg},
            status_code=500
        )


@router.post("/api/v3/test-generation/export-pdf-report")
async def export_pdf_report(file: UploadFile = File(...), max_tests: int = 8):
    """
    Export test cases as formatted PDF report with charts
    Professional format suitable for stakeholder review
    """
    try:
        from requirement_analyzer.task_gen.test_case_generator_v3 import AITestCaseGeneratorV3
        from requirement_analyzer.task_gen.report_generator import ReportGenerator
        from fastapi.responses import FileResponse
        
        # Parse file
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        parser = RequirementFileParser()
        if file_type == 'docx':
            requirements = parser.parse_file(None, file_type, binary_content=file_content)
        else:
            requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        
        if not requirements:
            return JSONResponse(
                {"status": "error", "message": "No requirements found"},
                status_code=400
            )
        
        # Generate test cases
        generator = AITestCaseGeneratorV3()
        test_data = generator.generate(requirements, max_test_cases_per_req=max_tests)
        
        # Generate PDF report
        report_gen = ReportGenerator(test_data)
        pdf_content = report_gen.generate_pdf_report()
        
        if isinstance(pdf_content, bytes) and pdf_content.startswith(b'%PDF'):
            # Valid PDF
            import tempfile
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
                f.write(pdf_content)
                temp_file = f.name
            
            return FileResponse(
                temp_file,
                media_type="application/pdf",
                filename=f"test_report_{generator.timestamp.replace(' ', '_').replace(':', '-')}.pdf"
            )
        else:
            # reportlab not installed, return message
            return JSONResponse(
                {"status": "warning", "message": "PDF export requires: pip install reportlab"},
                status_code=400
            )
    
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


@router.post("/api/v3/test-generation/export-report-stats")
async def export_report_statistics(file: UploadFile = File(...), max_tests: int = 8):
    """
    Export detailed statistics in JSON format for analytics/dashboards
    Includes quality scores, recommendations, and detailed metrics
    """
    try:
        from requirement_analyzer.task_gen.test_case_generator_v3 import AITestCaseGeneratorV3
        from requirement_analyzer.task_gen.report_generator import ReportGenerator
        import json
        
        # Parse file
        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        parser = RequirementFileParser()
        if file_type == 'docx':
            requirements = parser.parse_file(None, file_type, binary_content=file_content)
        else:
            requirements = parser.parse_file(file_content.decode('utf-8'), file_type)
        
        if not requirements:
            return JSONResponse(
                {"status": "error", "message": "No requirements found"},
                status_code=400
            )
        
        # Generate test cases
        generator = AITestCaseGeneratorV3()
        test_data = generator.generate(requirements, max_test_cases_per_req=max_tests)
        
        # Generate statistics
        report_gen = ReportGenerator(test_data)
        stats_json = report_gen.export_statistics_json()
        stats = json.loads(stats_json)
        
        return {
            "status": "success",
            "statistics": stats
        }
    
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )
