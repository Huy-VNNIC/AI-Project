"""
Test Case Generation Routes
Tích hợp vào requirement_analyzer.api
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
import json
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            .header h1 { color: #667eea; font-size: 32px; margin-bottom: 10px; }
            .panel {
                background: white;
                border-radius: 12px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 20px;
            }
            .upload-zone {
                border: 3px dashed #667eea;
                border-radius: 12px;
                padding: 40px;
                text-align: center;
                background: #f9f9f9;
                cursor: pointer;
                transition: all 0.3s;
            }
            .upload-zone:hover {
                background: #e3f2fd;
                border-color: #5568d3;
            }
            .upload-zone p { color: #666; margin: 10px 0; }
            input[type="file"] { display: none; }
            button {
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                margin-top: 20px;
                transition: all 0.3s;
            }
            button:hover { background: #5568d3; }
            .results {
                display: none;
                margin-top: 20px;
                padding: 20px;
                background: #f9f9f9;
                border-radius: 8px;
            }
            .results.show { display: block; }
            .loading { text-align: center; color: #667eea; }
            .requirement-item {
                background: white;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
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
            .stat h3 { color: #667eea; font-size: 24px; }
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
                    const response = await fetch('/api/v2/test-generation/analyze-file-detailed', {
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
                                <h4>⚠️ Requirement ${item.index}</h4>
                                <p style="color: #666;">${item.requirement}</p>
                                <p style="color: #f44336; font-size: 12px;">Error: ${item.error}</p>
                            </div>
                        `;
                        return;
                    }

                    html += `
                        <div class="requirement-item">
                            <h4>📋 Requirement ${item.index}</h4>
                            <p style="color: #333; font-weight: 500; margin-bottom: 8px;">
                                "${item.requirement}"
                            </p>
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin: 10px 0; font-size: 12px;">
                                <div style="background: #e3f2fd; padding: 8px; border-radius: 4px;">
                                    <strong style="color: #667eea;">Words:</strong> ${item.word_count}
                                </div>
                                <div style="background: #e3f2fd; padding: 8px; border-radius: 4px;">
                                    <strong style="color: #667eea;">Chars:</strong> ${item.character_count}
                                </div>
                                <div style="background: #e3f2fd; padding: 8px; border-radius: 4px;">
                                    <strong style="color: #667eea;">Confidence:</strong> ${(item.nlp_confidence * 100).toFixed(1)}%
                                </div>
                                <div style="background: #e3f2fd; padding: 8px; border-radius: 4px;">
                                    <strong style="color: #667eea;">Test Cases:</strong> ${item.test_cases_count}
                                </div>
                            </div>

                            <div class="test-case-list">
                                <strong>📊 Generated Test Cases (${item.test_cases.length}):</strong>
                                ${item.test_cases.map((tc, i) => `
                                    <div class="test-case" style="padding: 8px; margin: 4px 0; background: white; border-radius: 3px;">
                                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; font-size: 11px;">
                                            <div><strong>ID:</strong> ${tc.id}</div>
                                            <div><strong>Type:</strong> ${tc.scenario_type}</div>
                                            <div><strong>Priority:</strong> ${tc.priority}</div>
                                            <div><strong>Steps:</strong> ${tc.steps_count}</div>
                                        </div>
                                        <div style="margin-top: 4px; color: #666;" title="${tc.title}">${tc.title.substring(0, 80)}...</div>
                                        <div style="margin-top: 4px; color: #999; font-size: 10px;">
                                            Effort: ${tc.estimated_effort_hours.toFixed(1)}h | Confidence: ${(tc.confidence * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                });

                html += `
                    <div style="margin-top: 30px; display: flex; gap: 10px;">
                        <button onclick="downloadDetailedJSON()" style="background: #4CAF50; flex: 1;">📥 Download Detailed JSON</button>
                        <button onclick="downloadDetailedCSV()" style="background: #2196F3; flex: 1;">📥 Download as CSV</button>
                    </div>
                `;

                document.getElementById('resultsContent').innerHTML = html;
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
        </script>
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
