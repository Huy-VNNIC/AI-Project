"""
Test Case Generation Routes
Tích hợp vào requirement_analyzer.api
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pathlib import Path as _Path
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

                    const response = await fetch('/api/v3/test-generation/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            requirements: requirements,
                            max_tests: 15,
                            confidence_threshold: 0.5
                        })
                    });

                    if (!response.ok) {
                        const errText = await response.text();
                        throw new Error('API error: ' + errText);
                    }

                    const data = await response.json();
                    displayTestCases(data);
                    
                } catch (error) {
                    alert('Error: ' + error.message);
                } finally {
                    document.querySelector('button').textContent = 'Generate Test Cases';
                }
            }

            function escapeHtml(str) {
                if (!str) return '';
                return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
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

                const summary = data.summary || {};
                let html = `<h3>Generated ${data.test_cases.length} Test Cases</h3>`;
                html += `<p style="color:#666;font-size:12px;margin-bottom:15px;">Avg Quality: ${Math.round((summary.avg_quality_score||0)*100)}% | Time: ${summary.generation_time_ms||0}ms | System: ${escapeHtml(summary.system||'AI')}</p>`;

                data.test_cases.forEach((tc) => {
                    const type = tc.type || tc.scenario_type || 'Functional';
                    const quality = Math.round((tc.ml_quality_score || tc.quality_score || 0.7) * 100);
                    const priority = tc.priority || 'Medium';
                    const effort = tc.estimated_effort_hours || 0.5;
                    const domain = tc.domain || '';

                    // Steps rendering
                    let stepsHtml = '';
                    if (Array.isArray(tc.steps)) {
                        stepsHtml = '<ol style="margin:8px 0 8px 20px;font-size:12px;color:#444;">';
                        tc.steps.forEach(step => {
                            if (typeof step === 'object' && step.action) {
                                stepsHtml += '<li style="margin-bottom:4px;"><strong>' + escapeHtml(step.action) + '</strong>';
                                if (step.expected_result) stepsHtml += '<br><span style="color:#0369a1;">→ ' + escapeHtml(step.expected_result) + '</span>';
                                stepsHtml += '</li>';
                            } else {
                                stepsHtml += '<li>' + escapeHtml(String(step)) + '</li>';
                            }
                        });
                        stepsHtml += '</ol>';
                    }

                    // Preconditions
                    let preHtml = '';
                    if (Array.isArray(tc.preconditions) && tc.preconditions.length > 0) {
                        preHtml = tc.preconditions.map(p => escapeHtml(p)).join('; ');
                    } else if (typeof tc.preconditions === 'string') {
                        preHtml = escapeHtml(tc.preconditions);
                    } else {
                        preHtml = 'None';
                    }

                    const typeColors = {
                        'happy_path': '#059669', 'negative': '#dc2626', 'security': '#7c3aed',
                        'boundary': '#d97706', 'performance': '#2563eb', 'edge_case': '#ea580c',
                        'data_integrity': '#0891b2', 'integration': '#4f46e5'
                    };
                    const typeColor = typeColors[type] || '#0369a1';

                    html += `
                        <div class="test-case" style="border-left-color:${typeColor};">
                            <h4>${escapeHtml(tc.test_id || tc.id || '')}: ${escapeHtml(tc.title || 'Test Case')}</h4>
                            <p><span class="test-type" style="background:${typeColor}20;color:${typeColor};">${escapeHtml(type)}</span>
                               <span style="margin-left:8px;font-size:11px;color:#666;">Priority: <strong>${escapeHtml(priority)}</strong> | Quality: <strong>${quality}%</strong> | Effort: <strong>${effort}h</strong>${domain ? ' | Domain: <strong>'+escapeHtml(domain)+'</strong>' : ''}</span></p>
                            <p style="font-size:12px;color:#555;margin-top:6px;"><strong>Description:</strong> ${escapeHtml(tc.description)}</p>
                            <p style="font-size:12px;color:#555;"><strong>Preconditions:</strong> ${preHtml}</p>
                            ${stepsHtml}
                            <p style="font-size:12px;color:#0369a1;margin-top:6px;"><strong>Expected:</strong> ${escapeHtml(tc.expected_result)}</p>
                            ${tc.why_generated ? '<p style="font-size:11px;color:#888;margin-top:4px;">💡 ' + escapeHtml(tc.why_generated) + '</p>' : ''}
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
    """File upload page → serves the modern Analysis Results Dashboard."""
    # Serve the new Linear/Notion-inspired dashboard (has built-in upload zone).
    dash_file = _Path(__file__).parent.parent / "templates" / "analysis_dashboard.html"
    if dash_file.exists():
        return FileResponse(dash_file, media_type="text/html")
    # Fallback to legacy upload page if template missing
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload Requirements — AI Test Generator</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
        <style>
            :root {
                --parchment: #f5f4ed;
                --ivory: #faf9f5;
                --white: #ffffff;
                --warm-sand: #e8e6dc;
                --near-black: #141413;
                --dark-surface: #30302e;
                --terracotta: #c96442;
                --coral: #d97757;
                --charcoal-warm: #4d4c48;
                --olive-gray: #5e5d59;
                --stone-gray: #87867f;
                --dark-warm: #3d3d3a;
                --warm-silver: #b0aea5;
                --border-cream: #f0eee6;
                --border-warm: #e8e6dc;
                --ring-warm: #d1cfc5;
                --ring-deep: #c2c0b6;
                --error-crimson: #b53333;
                --focus-blue: #3898ec;
                --font-serif: 'Playfair Display', Georgia, serif;
                --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
                --font-mono: 'JetBrains Mono', monospace;
            }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: var(--parchment);
                font-family: var(--font-sans);
                min-height: 100vh;
                color: var(--near-black);
                line-height: 1.6;
            }

            /* Navigation */
            .nav {
                position: sticky; top: 0; z-index: 100;
                background: var(--ivory);
                border-bottom: 1px solid var(--border-cream);
                padding: 16px 0;
            }
            .nav-inner {
                max-width: 1200px; margin: 0 auto; padding: 0 32px;
                display: flex; align-items: center; justify-content: space-between;
            }
            .nav-brand {
                font-family: var(--font-serif); font-weight: 500; font-size: 20px;
                color: var(--near-black); text-decoration: none;
            }
            .nav-links { display: flex; gap: 24px; align-items: center; }
            .nav-links a {
                font-size: 15px; color: var(--olive-gray); text-decoration: none;
                font-weight: 500; transition: color 0.2s;
            }
            .nav-links a:hover { color: var(--near-black); }
            .nav-links a.active { color: var(--terracotta); }

            /* Container */
            .container { max-width: 1200px; margin: 0 auto; padding: 0 32px; }

            /* Hero / Header */
            .header-section {
                padding: 64px 0 48px;
                border-bottom: 1px solid var(--border-cream);
            }
            .header-section h1 {
                font-family: var(--font-serif); font-weight: 500; font-size: 52px;
                line-height: 1.15; color: var(--near-black); margin-bottom: 16px;
            }
            .header-section .subtitle {
                font-size: 20px; color: var(--olive-gray); line-height: 1.6;
                max-width: 640px;
            }

            /* Upload Panel */
            .upload-section { padding: 48px 0; }
            .upload-grid {
                display: grid; grid-template-columns: 1fr 1fr; gap: 32px;
            }
            .panel {
                background: var(--ivory);
                border: 1px solid var(--border-cream);
                border-radius: 16px;
                padding: 32px;
                box-shadow: rgba(0,0,0,0.05) 0px 4px 24px;
            }
            .panel h2 {
                font-family: var(--font-serif); font-weight: 500; font-size: 25px;
                line-height: 1.2; color: var(--near-black); margin-bottom: 20px;
            }
            .upload-zone {
                border: 2px dashed var(--ring-warm);
                border-radius: 16px;
                padding: 48px 32px;
                text-align: center;
                background: var(--parchment);
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .upload-zone:hover {
                background: var(--ivory);
                border-color: var(--terracotta);
            }
            .upload-zone.file-selected {
                border-color: var(--terracotta);
                border-style: solid;
                background: var(--ivory);
            }
            .upload-icon {
                width: 56px; height: 56px; margin: 0 auto 16px;
                background: var(--warm-sand); border-radius: 12px;
                display: flex; align-items: center; justify-content: center;
                font-size: 24px;
            }
            .upload-zone h3 {
                font-family: var(--font-sans); font-weight: 600; font-size: 16px;
                color: var(--near-black); margin-bottom: 8px;
            }
            .upload-zone p { font-size: 14px; color: var(--stone-gray); margin: 4px 0; }
            .upload-zone .filetypes {
                display: inline-flex; gap: 6px; margin-top: 12px;
            }
            .upload-zone .filetypes span {
                background: var(--warm-sand); color: var(--charcoal-warm);
                font-size: 11px; font-weight: 600; padding: 4px 10px;
                border-radius: 6px; letter-spacing: 0.5px;
            }
            .file-info {
                margin-top: 16px; padding: 12px 16px;
                background: var(--parchment); border-radius: 8px;
                font-size: 14px; color: var(--olive-gray);
                display: none; align-items: center; gap: 8px;
            }
            .file-info.show { display: flex; }
            .file-info .fname { font-weight: 600; color: var(--near-black); }

            input[type="file"] { display: none; }

            /* Controls */
            .controls {
                margin-top: 24px;
                display: flex; flex-direction: column; gap: 16px;
            }
            .form-group label {
                display: block; font-size: 14px; font-weight: 500;
                color: var(--charcoal-warm); margin-bottom: 6px;
            }
            .form-group input, .form-group select {
                width: 100%; padding: 10px 14px;
                border: 1px solid var(--border-warm); border-radius: 12px;
                font-family: var(--font-sans); font-size: 15px;
                color: var(--near-black); background: var(--white);
                transition: border-color 0.2s;
            }
            .form-group input:focus, .form-group select:focus {
                outline: none; border-color: var(--focus-blue);
                box-shadow: 0 0 0 3px rgba(56,152,236,0.12);
            }

            /* Buttons */
            .btn {
                display: inline-flex; align-items: center; justify-content: center;
                gap: 8px; padding: 12px 24px; border: none; border-radius: 12px;
                font-family: var(--font-sans); font-size: 16px; font-weight: 600;
                cursor: pointer; transition: all 0.2s; text-decoration: none;
            }
            .btn-primary {
                background: var(--terracotta); color: var(--ivory);
                box-shadow: var(--terracotta) 0 0 0 0, var(--terracotta) 0 0 0 1px;
            }
            .btn-primary:hover {
                background: #b8593a; transform: translateY(-1px);
                box-shadow: rgba(0,0,0,0.08) 0 4px 16px;
            }
            .btn-primary:disabled {
                background: var(--ring-warm); color: var(--stone-gray);
                cursor: not-allowed; transform: none; box-shadow: none;
            }
            .btn-secondary {
                background: var(--warm-sand); color: var(--charcoal-warm);
                box-shadow: var(--warm-sand) 0 0 0 0, var(--ring-warm) 0 0 0 1px;
            }
            .btn-secondary:hover { background: var(--ring-warm); }
            .btn-dark {
                background: var(--dark-surface); color: var(--ivory);
                box-shadow: var(--dark-surface) 0 0 0 0, var(--dark-surface) 0 0 0 1px;
            }
            .btn-dark:hover { background: var(--near-black); }
            .btn-sm { padding: 8px 16px; font-size: 14px; border-radius: 8px; }
            .btn-full { width: 100%; }

            /* Info panel */
            .info-panel { padding: 0; }
            .info-card {
                padding: 20px; border-bottom: 1px solid var(--border-cream);
            }
            .info-card:last-child { border-bottom: none; }
            .info-card h3 {
                font-family: var(--font-serif); font-weight: 500; font-size: 18px;
                color: var(--near-black); margin-bottom: 8px;
            }
            .info-card p { font-size: 14px; color: var(--olive-gray); line-height: 1.6; }
            .info-card .tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
            .tag {
                font-size: 12px; font-weight: 500; padding: 4px 10px;
                border-radius: 6px; background: var(--parchment); color: var(--olive-gray);
                border: 1px solid var(--border-cream);
            }

            /* Results */
            .results-section {
                display: none; padding: 48px 0 64px;
            }
            .results-section.show { display: block; }
            .results-section h2 {
                font-family: var(--font-serif); font-weight: 500; font-size: 36px;
                line-height: 1.2; color: var(--near-black); margin-bottom: 32px;
            }

            /* Stats bar */
            .stats-bar {
                display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
                margin-bottom: 40px;
            }
            .stat-card {
                background: var(--ivory); border: 1px solid var(--border-cream);
                border-radius: 12px; padding: 20px; text-align: center;
            }
            .stat-card .value {
                font-family: var(--font-serif); font-size: 32px; font-weight: 500;
                color: var(--terracotta); line-height: 1.2;
            }
            .stat-card .label {
                font-size: 13px; color: var(--stone-gray); margin-top: 6px;
                font-weight: 500;
            }

            /* Requirement cards */
            .req-card {
                background: var(--ivory); border: 1px solid var(--border-cream);
                border-radius: 16px; margin-bottom: 24px; overflow: hidden;
                box-shadow: rgba(0,0,0,0.03) 0 2px 12px;
            }
            .req-header {
                padding: 24px 28px; background: var(--parchment);
                border-bottom: 1px solid var(--border-cream);
                display: flex; justify-content: space-between; align-items: flex-start;
            }
            .req-header .req-index {
                font-family: var(--font-mono); font-size: 12px; font-weight: 500;
                color: var(--terracotta); background: rgba(201,100,66,0.08);
                padding: 4px 10px; border-radius: 6px;
            }
            .req-header .req-text {
                font-family: var(--font-serif); font-size: 18px; font-weight: 500;
                color: var(--near-black); line-height: 1.4; flex: 1; margin: 0 16px;
            }
            .req-meta {
                display: flex; gap: 12px; padding: 16px 28px;
                border-bottom: 1px solid var(--border-cream);
            }
            .meta-chip {
                display: inline-flex; align-items: center; gap: 4px;
                font-size: 12px; color: var(--olive-gray);
                background: var(--parchment); padding: 6px 12px; border-radius: 8px;
                font-weight: 500;
            }
            .meta-chip strong { color: var(--near-black); }

            /* Test case items */
            .tc-list { padding: 16px 28px 24px; }
            .tc-item {
                background: var(--white); border: 1px solid var(--border-cream);
                border-radius: 12px; padding: 16px 20px; margin-bottom: 12px;
                cursor: pointer; transition: all 0.2s;
            }
            .tc-item:hover {
                border-color: var(--ring-warm);
                box-shadow: rgba(0,0,0,0.05) 0 4px 24px;
                transform: translateY(-1px);
            }
            .tc-item-top {
                display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 8px;
            }
            .tc-id {
                font-family: var(--font-mono); font-size: 12px;
                color: var(--terracotta); font-weight: 500;
            }
            .tc-type-badge {
                font-size: 11px; font-weight: 600; padding: 3px 10px;
                border-radius: 6px; text-transform: uppercase; letter-spacing: 0.5px;
            }
            .tc-title {
                font-size: 15px; font-weight: 500; color: var(--near-black);
                line-height: 1.4; margin-bottom: 8px;
            }
            .tc-bottom {
                display: flex; gap: 16px; font-size: 12px; color: var(--stone-gray);
            }
            .tc-bottom strong { color: var(--olive-gray); }

            /* Export section */
            .export-section {
                margin-top: 48px; padding-top: 48px;
                border-top: 1px solid var(--border-cream);
            }
            .export-section h3 {
                font-family: var(--font-serif); font-weight: 500; font-size: 25px;
                color: var(--near-black); margin-bottom: 20px;
            }
            .export-grid {
                display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;
            }
            .export-btn {
                display: flex; align-items: center; gap: 10px;
                padding: 14px 20px; background: var(--ivory);
                border: 1px solid var(--border-cream); border-radius: 12px;
                font-family: var(--font-sans); font-size: 14px; font-weight: 600;
                color: var(--charcoal-warm); cursor: pointer; transition: all 0.2s;
            }
            .export-btn:hover {
                background: var(--warm-sand); border-color: var(--ring-warm);
                transform: translateY(-1px);
            }
            .export-btn .icon {
                width: 36px; height: 36px; border-radius: 8px;
                display: flex; align-items: center; justify-content: center;
                font-size: 16px; flex-shrink: 0;
            }

            /* Modal — Claude style */
            .modal-overlay {
                display: none; position: fixed; z-index: 999;
                left: 0; top: 0; width: 100%; height: 100%;
                background: rgba(20,20,19,0.6); backdrop-filter: blur(4px);
                justify-content: center; align-items: center;
            }
            .modal-overlay.show { display: flex; }
            .modal-box {
                width: 92%; max-width: 900px; max-height: 88vh;
                background: var(--ivory); border-radius: 20px;
                box-shadow: rgba(0,0,0,0.2) 0 24px 64px;
                overflow-y: auto;
            }
            .modal-header {
                position: sticky; top: 0; z-index: 10;
                background: var(--ivory);
                padding: 28px 32px 20px;
                border-bottom: 1px solid var(--border-cream);
            }
            .modal-header h2 {
                font-family: var(--font-serif); font-weight: 500; font-size: 25px;
                color: var(--near-black); line-height: 1.3; margin-bottom: 4px;
            }
            .modal-header .modal-sub {
                font-size: 13px; color: var(--stone-gray);
            }
            .modal-close {
                position: absolute; right: 24px; top: 24px;
                width: 36px; height: 36px; border-radius: 8px;
                background: var(--warm-sand); border: none; cursor: pointer;
                font-size: 18px; color: var(--charcoal-warm);
                display: flex; align-items: center; justify-content: center;
                transition: background 0.2s;
            }
            .modal-close:hover { background: var(--ring-warm); }
            .modal-body { padding: 28px 32px 32px; }
            .modal-meta-grid {
                display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
                margin-bottom: 28px;
            }
            .modal-meta-card {
                background: var(--parchment); border-radius: 10px; padding: 14px;
                text-align: center;
            }
            .modal-meta-card .mmc-label {
                font-size: 11px; font-weight: 600; color: var(--stone-gray);
                text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;
            }
            .modal-meta-card .mmc-value {
                font-family: var(--font-serif); font-size: 20px; font-weight: 500;
                color: var(--near-black);
            }
            .modal-section {
                margin-bottom: 24px;
            }
            .modal-section-title {
                font-family: var(--font-serif); font-weight: 500; font-size: 18px;
                color: var(--near-black); margin-bottom: 12px;
                padding-bottom: 8px; border-bottom: 1px solid var(--border-cream);
            }
            .modal-section ul {
                list-style: none; padding: 0;
            }
            .modal-section ul li {
                font-size: 14px; color: var(--olive-gray); line-height: 1.6;
                padding: 6px 0; padding-left: 20px; position: relative;
            }
            .modal-section ul li::before {
                content: ''; position: absolute; left: 0; top: 14px;
                width: 6px; height: 6px; border-radius: 50%;
                background: var(--terracotta);
            }
            .step-item {
                padding: 14px 18px; background: var(--parchment);
                border-radius: 10px; margin-bottom: 10px;
            }
            .step-num {
                font-family: var(--font-mono); font-size: 11px; color: var(--terracotta);
                font-weight: 600; margin-bottom: 4px;
            }
            .step-action { font-size: 14px; font-weight: 500; color: var(--near-black); }
            .step-expected {
                font-size: 13px; color: var(--olive-gray); margin-top: 4px;
                padding-left: 16px; border-left: 2px solid var(--terracotta);
            }
            .test-data-table {
                width: 100%; border-collapse: collapse; font-size: 13px;
            }
            .test-data-table th {
                text-align: left; padding: 10px 14px; font-weight: 600;
                background: var(--parchment); color: var(--charcoal-warm);
                border-bottom: 1px solid var(--border-warm);
            }
            .test-data-table td {
                padding: 10px 14px; color: var(--olive-gray);
                border-bottom: 1px solid var(--border-cream);
            }
            .test-data-table td code {
                font-family: var(--font-mono); font-size: 12px;
                background: var(--parchment); padding: 2px 8px; border-radius: 4px;
            }
            .expected-result-box {
                background: rgba(201,100,66,0.06); border: 1px solid rgba(201,100,66,0.15);
                border-radius: 12px; padding: 18px 20px;
                font-size: 14px; color: var(--near-black); line-height: 1.7;
            }

            /* Loading */
            .loading-container {
                text-align: center; padding: 64px 32px;
            }
            .spinner {
                width: 40px; height: 40px; border: 3px solid var(--border-warm);
                border-top-color: var(--terracotta); border-radius: 50%;
                animation: spin 0.8s linear infinite; margin: 0 auto 16px;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
            .loading-text {
                font-size: 15px; color: var(--olive-gray); font-weight: 500;
            }

            /* Error */
            .error-box {
                padding: 20px; background: rgba(181,51,51,0.06);
                border: 1px solid rgba(181,51,51,0.15); border-radius: 12px;
                color: var(--error-crimson); font-size: 14px;
            }

            /* Responsive */
            @media (max-width: 991px) {
                .upload-grid { grid-template-columns: 1fr; }
                .stats-bar { grid-template-columns: repeat(2, 1fr); }
                .export-grid { grid-template-columns: repeat(2, 1fr); }
                .modal-meta-grid { grid-template-columns: repeat(2, 1fr); }
            }
            @media (max-width: 640px) {
                .header-section h1 { font-size: 36px; }
                .container { padding: 0 16px; }
                .stats-bar { grid-template-columns: 1fr 1fr; }
                .export-grid { grid-template-columns: 1fr; }
                .nav-links { gap: 12px; }
            }
        </style>
    </head>
    <body>
        <!-- Navigation -->
        <nav class="nav">
            <div class="nav-inner">
                <a href="/testcase" class="nav-brand">AI Test Generator</a>
                <div class="nav-links">
                    <a href="/testcase">Text Input</a>
                    <a href="/testcase/upload" class="active">File Upload</a>
                    <a href="/testcase/dashboard">Dashboard</a>
                </div>
            </div>
        </nav>

        <!-- Header -->
        <div class="header-section">
            <div class="container">
                <h1>Upload Requirements</h1>
                <p class="subtitle">Upload your requirements document and let the AI analyze each requirement with NLP-powered parsing, generating comprehensive test cases with intelligent coverage.</p>
            </div>
        </div>

        <!-- Upload Area -->
        <div class="upload-section">
            <div class="container">
                <div class="upload-grid">
                    <!-- Left: Upload + Controls -->
                    <div class="panel">
                        <h2>Upload Document</h2>
                        <div class="upload-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
                            <div class="upload-icon">📄</div>
                            <h3>Click to select file</h3>
                            <p>or drag and drop your requirements document</p>
                            <div class="filetypes">
                                <span>TXT</span><span>CSV</span><span>MD</span><span>DOCX</span>
                            </div>
                        </div>
                        <input type="file" id="fileInput" accept=".txt,.csv,.md,.markdown,.docx" onchange="handleFileUpload(event)">

                        <div class="file-info" id="fileInfo">
                            <span>📎</span>
                            <span class="fname" id="fileName"></span>
                            <span id="fileSize" style="color:var(--stone-gray);font-size:12px;"></span>
                        </div>

                        <div class="controls">
                            <div class="form-group">
                                <label>Max Test Cases per Requirement</label>
                                <input type="number" id="maxTests" value="10" min="1" max="50">
                            </div>
                            <button class="btn btn-primary btn-full" id="analyzeBtn" onclick="analyzeFile()" disabled>
                                Analyze &amp; Generate Test Cases
                            </button>
                        </div>
                    </div>

                    <!-- Right: Info -->
                    <div class="panel info-panel">
                        <div class="info-card">
                            <h3>NLP-Powered Analysis</h3>
                            <p>Each requirement is parsed using spaCy dependency parsing to extract subjects, verbs, objects, conditions, and numeric constraints — enabling context-aware test generation.</p>
                            <div class="tag-row">
                                <span class="tag">spaCy NLP</span>
                                <span class="tag">SVO Extraction</span>
                                <span class="tag">Dependency Parse</span>
                            </div>
                        </div>
                        <div class="info-card">
                            <h3>Intelligent Test Types</h3>
                            <p>The AI strategically selects test types based on the parsed semantics — security tests for auth requirements, boundary tests for numeric constraints, and more.</p>
                            <div class="tag-row">
                                <span class="tag">Happy Path</span>
                                <span class="tag">Negative</span>
                                <span class="tag">Security</span>
                                <span class="tag">Boundary</span>
                                <span class="tag">Edge Case</span>
                                <span class="tag">Data Integrity</span>
                            </div>
                        </div>
                        <div class="info-card">
                            <h3>Export Formats</h3>
                            <p>Export generated test cases to Pytest, Gherkin/BDD, RTM (CSV), JSON, HTML Report, or PDF Report.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Results -->
        <div class="results-section" id="resultsSection">
            <div class="container">
                <h2>Analysis Results</h2>
                <div id="resultsContent"></div>
            </div>
        </div>

        <!-- Modal -->
        <div class="modal-overlay" id="testCaseModal">
            <div class="modal-box">
                <div class="modal-header">
                    <h2 id="modalTitle">Test Case Details</h2>
                    <p class="modal-sub" id="modalSub"></p>
                    <button class="modal-close" onclick="closeTestCaseModal()">✕</button>
                </div>
                <div class="modal-body" id="modalBody"></div>
            </div>
        </div>

        <script>
            let uploadedFile = null;

            function escapeHtml(str) {
                if (!str) return '';
                return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
            }

            // Drag-and-drop support
            const dropZone = document.getElementById('dropZone');
            ['dragenter','dragover'].forEach(evt => {
                dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.add('file-selected'); });
            });
            ['dragleave','drop'].forEach(evt => {
                dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.remove('file-selected'); });
            });
            dropZone.addEventListener('drop', e => {
                const file = e.dataTransfer.files[0];
                if (file) { setFile(file); }
            });

            function handleFileUpload(event) {
                setFile(event.target.files[0]);
            }

            function setFile(file) {
                uploadedFile = file;
                window.currentFile = file;
                document.getElementById('fileName').textContent = file.name;
                document.getElementById('fileSize').textContent = (file.size/1024).toFixed(1) + ' KB';
                document.getElementById('fileInfo').classList.add('show');
                document.getElementById('dropZone').classList.add('file-selected');
                document.getElementById('analyzeBtn').disabled = false;
            }

            async function analyzeFile() {
                if (!uploadedFile) return;

                const resultsSection = document.getElementById('resultsSection');
                resultsSection.classList.add('show');
                const rc = document.getElementById('resultsContent');
                rc.innerHTML = '<div class="loading-container"><div class="spinner"></div><p class="loading-text">Analyzing requirements with NLP pipeline...</p><p style="font-size:13px;color:var(--stone-gray);margin-top:8px;">File: ' + escapeHtml(uploadedFile.name) + '</p></div>';
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

                const formData = new FormData();
                formData.append('file', uploadedFile);
                formData.append('max_tests', document.getElementById('maxTests').value);

                try {
                    const response = await fetch('/api/v3/test-generation/analyze-file-detailed', {
                        method: 'POST', body: formData
                    });
                    const data = await response.json();
                    if (!response.ok) throw new Error(data.detail || 'Failed to analyze file');
                    displayDetailedResults(data);
                } catch (error) {
                    rc.innerHTML = '<div class="error-box">Error: ' + escapeHtml(error.message) + '</div>';
                }
            }

            function displayDetailedResults(data) {
                window.detailedData = data;
                let totalTestCases = 0, avgConfidence = 0, confCount = 0, totalEffort = 0;

                data.detailed.forEach(item => {
                    if (item.test_cases_count) totalTestCases += item.test_cases_count;
                    if (item.nlp_confidence) { avgConfidence += item.nlp_confidence; confCount++; }
                    if (item.avg_effort) totalEffort += item.avg_effort * (item.test_cases_count || 0);
                });
                if (confCount > 0) avgConfidence /= confCount;

                let html = '';

                // Stats bar
                html += '<div class="stats-bar">';
                html += '<div class="stat-card"><div class="value">' + data.detailed.length + '</div><div class="label">Requirements Analyzed</div></div>';
                html += '<div class="stat-card"><div class="value">' + totalTestCases + '</div><div class="label">Test Cases Generated</div></div>';
                html += '<div class="stat-card"><div class="value">' + (avgConfidence * 100).toFixed(1) + '%</div><div class="label">Avg NLP Confidence</div></div>';
                html += '<div class="stat-card"><div class="value">' + totalEffort.toFixed(1) + 'h</div><div class="label">Total Estimated Effort</div></div>';
                html += '</div>';

                // Type color map
                const typeColors = {
                    'happy_path': {bg:'#f0fdf4',fg:'#166534',border:'#bbf7d0'},
                    'negative': {bg:'#fef2f2',fg:'#991b1b',border:'#fecaca'},
                    'security': {bg:'#faf5ff',fg:'#6b21a8',border:'#e9d5ff'},
                    'boundary': {bg:'#fffbeb',fg:'#92400e',border:'#fde68a'},
                    'performance': {bg:'#eff6ff',fg:'#1e40af',border:'#bfdbfe'},
                    'edge_case': {bg:'#fff7ed',fg:'#9a3412',border:'#fed7aa'},
                    'data_integrity': {bg:'#ecfeff',fg:'#155e75',border:'#a5f3fc'},
                    'integration': {bg:'#eef2ff',fg:'#3730a3',border:'#c7d2fe'}
                };

                // Requirement cards
                data.detailed.forEach((item, idx) => {
                    if (item.error) {
                        html += '<div class="req-card"><div class="req-header"><span class="req-index">REQ-' + item.index + '</span><span class="req-text" style="color:var(--error-crimson);">' + escapeHtml(item.requirement) + '</span></div><div style="padding:16px 28px;"><div class="error-box">' + escapeHtml(item.error) + '</div></div></div>';
                        return;
                    }

                    html += '<div class="req-card">';
                    html += '<div class="req-header"><span class="req-index">REQ-' + item.index + '</span><span class="req-text">' + escapeHtml(item.requirement) + '</span></div>';
                    html += '<div class="req-meta">';
                    html += '<span class="meta-chip">Words: <strong>' + item.word_count + '</strong></span>';
                    html += '<span class="meta-chip">Chars: <strong>' + item.character_count + '</strong></span>';
                    html += '<span class="meta-chip">NLP Confidence: <strong>' + (item.nlp_confidence * 100).toFixed(1) + '%</strong></span>';
                    html += '<span class="meta-chip">Test Cases: <strong>' + item.test_cases_count + '</strong></span>';
                    html += '</div>';

                    html += '<div class="tc-list">';
                    (item.test_cases || []).forEach(tc => {
                        const type = tc.type || tc.scenario_type || 'functional';
                        const colors = typeColors[type] || {bg:'var(--parchment)',fg:'var(--charcoal-warm)',border:'var(--border-warm)'};
                        const priority = tc.priority || 'Medium';
                        const priorityColor = priority === 'Critical' || priority === 'CRITICAL' ? 'var(--error-crimson)' : priority === 'High' || priority === 'HIGH' ? 'var(--terracotta)' : 'var(--olive-gray)';

                        html += '<div class="tc-item" onclick="showTestCaseDetailsV2(\\'' + (tc.id || '') + '\\')">';
                        html += '<div class="tc-item-top"><span class="tc-id">' + escapeHtml(tc.id) + '</span>';
                        html += '<span class="tc-type-badge" style="background:' + colors.bg + ';color:' + colors.fg + ';border:1px solid ' + colors.border + ';">' + escapeHtml(type) + '</span></div>';
                        html += '<div class="tc-title">' + escapeHtml(tc.title) + '</div>';
                        html += '<div class="tc-bottom">';
                        html += '<span>Priority: <strong style="color:' + priorityColor + ';">' + escapeHtml(priority) + '</strong></span>';
                        html += '<span>Steps: <strong>' + (tc.steps_count || tc.steps?.length || 0) + '</strong></span>';
                        html += '<span>Confidence: <strong>' + ((tc.confidence || 0) * 100).toFixed(0) + '%</strong></span>';
                        html += '<span>Effort: <strong>' + (tc.estimated_effort_hours || 1.0).toFixed(1) + 'h</strong></span>';
                        html += '</div></div>';
                    });
                    html += '</div></div>';
                });

                // Export section
                html += '<div class="export-section"><h3>Export Results</h3><div class="export-grid">';
                const exports = [
                    {fn:'exportPytest',icon:'🐍',label:'Pytest',desc:'Python test file',color:'#f59e0b'},
                    {fn:'exportGherkin',icon:'🥒',label:'Gherkin / BDD',desc:'Feature file',color:'#8b5cf6'},
                    {fn:'exportRTM',icon:'📊',label:'RTM (CSV)',desc:'Traceability matrix',color:'#06b6d4'},
                    {fn:'exportJSON',icon:'📋',label:'JSON',desc:'Structured data',color:'#22c55e'},
                    {fn:'exportHtmlReport',icon:'🌐',label:'HTML Report',desc:'Full report',color:'#3b82f6'},
                    {fn:'exportPdfReport',icon:'📑',label:'PDF Report',desc:'Printable report',color:'#ec4899'}
                ];
                exports.forEach(e => {
                    html += '<button class="export-btn" onclick="' + e.fn + '()">';
                    html += '<span class="icon" style="background:' + e.color + '15;color:' + e.color + ';">' + e.icon + '</span>';
                    html += '<span><strong>' + e.label + '</strong><br><span style="font-size:12px;font-weight:400;color:var(--stone-gray);">' + e.desc + '</span></span>';
                    html += '</button>';
                });
                html += '</div></div>';

                document.getElementById('resultsContent').innerHTML = html;

                // Store test case data for modal
                window.testCasesData = {};
                data.detailed.forEach(req => {
                    if (req.test_cases) {
                        req.test_cases.forEach(tc => {
                            window.testCasesData[tc.id] = { ...tc, requirement: req.requirement, requirement_index: req.index };
                        });
                    }
                });
            }

            function showTestCaseDetailsV2(testCaseId) {
                const tc = window.testCasesData[testCaseId];
                if (!tc) return;

                document.getElementById('modalTitle').textContent = tc.title || 'Test Case';
                document.getElementById('modalSub').textContent = 'ID: ' + testCaseId + '  •  From: ' + (tc.requirement || '').substring(0, 100);

                const typeColors = {
                    'happy_path':'#166534','negative':'#991b1b','security':'#6b21a8',
                    'boundary':'#92400e','performance':'#1e40af','edge_case':'#9a3412',
                    'data_integrity':'#155e75','integration':'#3730a3'
                };
                const type = tc.type || tc.scenario_type || 'functional';
                const tColor = typeColors[type] || 'var(--terracotta)';

                let body = '';

                // Meta grid
                body += '<div class="modal-meta-grid">';
                body += '<div class="modal-meta-card"><div class="mmc-label">Type</div><div class="mmc-value" style="color:' + tColor + ';font-size:16px;">' + escapeHtml(type) + '</div></div>';
                body += '<div class="modal-meta-card"><div class="mmc-label">Priority</div><div class="mmc-value">' + escapeHtml(tc.priority || 'Medium') + '</div></div>';
                body += '<div class="modal-meta-card"><div class="mmc-label">Confidence</div><div class="mmc-value">' + ((tc.confidence || 0) * 100).toFixed(1) + '%</div></div>';
                body += '<div class="modal-meta-card"><div class="mmc-label">Effort</div><div class="mmc-value">' + (tc.estimated_effort_hours || 1.0).toFixed(1) + 'h</div></div>';
                body += '</div>';

                // Preconditions
                const preconds = tc.preconditions || [];
                if (preconds.length > 0) {
                    body += '<div class="modal-section"><div class="modal-section-title">Preconditions</div><ul>';
                    preconds.forEach(p => { body += '<li>' + escapeHtml(typeof p === 'string' ? p : JSON.stringify(p)) + '</li>'; });
                    body += '</ul></div>';
                }

                // Test Data
                const testData = tc.test_data || {};
                if (Object.keys(testData).length > 0) {
                    body += '<div class="modal-section"><div class="modal-section-title">Test Data</div>';
                    body += '<table class="test-data-table"><tr><th>Key</th><th>Value</th></tr>';
                    Object.entries(testData).forEach(([k, v]) => {
                        body += '<tr><td><strong>' + escapeHtml(k) + '</strong></td><td><code>' + escapeHtml(typeof v === 'string' ? v : JSON.stringify(v)) + '</code></td></tr>';
                    });
                    body += '</table></div>';
                }

                // Steps
                const steps = tc.steps || [];
                if (steps.length > 0) {
                    body += '<div class="modal-section"><div class="modal-section-title">Test Steps</div>';
                    steps.forEach((step, i) => {
                        body += '<div class="step-item">';
                        body += '<div class="step-num">Step ' + (i + 1) + '</div>';
                        body += '<div class="step-action">' + escapeHtml(typeof step === 'string' ? step : (step.action || 'N/A')) + '</div>';
                        const exp = typeof step === 'object' ? (step.expected_result || step.expected || '') : '';
                        if (exp) body += '<div class="step-expected">' + escapeHtml(exp) + '</div>';
                        body += '</div>';
                    });
                    body += '</div>';
                }

                // Expected Result
                body += '<div class="modal-section"><div class="modal-section-title">Expected Result</div>';
                body += '<div class="expected-result-box">' + escapeHtml(tc.expected_result || 'Not specified') + '</div></div>';

                // Validation
                const validation = tc.validation || [];
                if (validation.length > 0) {
                    body += '<div class="modal-section"><div class="modal-section-title">Validation Criteria</div><ul>';
                    validation.forEach(v => { body += '<li>' + escapeHtml(v) + '</li>'; });
                    body += '</ul></div>';
                }

                document.getElementById('modalBody').innerHTML = body;
                document.getElementById('testCaseModal').classList.add('show');
            }

            function closeTestCaseModal() {
                document.getElementById('testCaseModal').classList.remove('show');
            }
            window.onclick = function(e) {
                if (e.target === document.getElementById('testCaseModal')) closeTestCaseModal();
            };

            // ===== EXPORT FUNCTIONS =====
            function getUploadedFile() { return uploadedFile; }

            async function exportWithFormat(format) {
                const file = getUploadedFile();
                if (!file) { alert('Please upload and analyze a file first'); return; }
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
                    'pytest': 'test_generated.py',
                    'gherkin': 'generated.feature',
                    'rtm': 'traceability_matrix.csv',
                    'json': 'test_cases.json'
                };
                try {
                    const response = await fetch(endpoints[format], { method: 'POST', body: formData });
                    if (!response.ok) { const err = await response.json(); throw new Error(err.message || 'Export failed'); }
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a'); a.href = url; a.download = fileNames[format];
                    document.body.appendChild(a); a.click(); document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                } catch (error) { alert('Export failed: ' + error.message); }
            }
            function exportPytest() { exportWithFormat('pytest'); }
            function exportGherkin() { exportWithFormat('gherkin'); }
            function exportRTM() { exportWithFormat('rtm'); }
            function exportJSON() { exportWithFormat('json'); }

            async function exportReportWithFormat(format) {
                if (!uploadedFile) { alert('Please analyze a file first'); return; }
                const formData = new FormData();
                formData.append('file', uploadedFile);
                const maxTests = parseInt(document.getElementById('maxTests').value) || 8;
                const ext = format === 'html' ? 'html' : 'pdf';
                const endpoint = '/api/v3/test-generation/export-' + ext + '-report?max_tests=' + maxTests;
                const filename = 'test_report_' + new Date().toISOString().slice(0, 10) + '.' + ext;
                try {
                    const response = await fetch(endpoint, { method: 'POST', body: formData });
                    if (!response.ok) throw new Error('Export failed: ' + response.status);
                    const blob = await response.blob();
                    if (blob.size === 0) throw new Error('Empty response');
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a'); a.href = url; a.download = filename;
                    document.body.appendChild(a); a.click(); document.body.removeChild(a);
                } catch (error) { alert('Export failed: ' + error.message); }
            }
            function exportHtmlReport() { exportReportWithFormat('html'); }
            function exportPdfReport() { exportReportWithFormat('pdf'); }
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
    NLP-Powered Test Case Analysis using spaCy dependency parsing.
    Uses AITestGenerator (smart_ai_generator_v2) for real context-aware generation.
    """
    try:
        from requirement_analyzer.task_gen.smart_ai_generator_v2 import AITestGenerator

        file_content = await file.read()
        file_type = file.filename.split('.')[-1].lower()

        supported_types = ['txt', 'csv', 'md', 'markdown', 'docx']
        if file_type not in supported_types:
            raise ValueError(f"Unsupported file type: .{file_type}. Supported: TXT, CSV, MD, DOCX")

        # Parse file into requirement strings
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

        # Generate using real NLP generator (spaCy-based)
        generator = AITestGenerator()
        detailed_analysis = []
        total_test_cases = 0
        total_confidence = 0.0
        type_distribution = {}

        for req_idx, req_text in enumerate(requirements, 1):
            req_text = req_text.strip()
            if not req_text:
                continue

            # Generate for this single requirement
            result = generator.generate([req_text], max_tests=max_tests)
            test_cases = result.get("test_cases", [])

            if not test_cases:
                continue

            # Format test cases for frontend
            formatted_tests = []
            req_confidence = 0.0
            for tc in test_cases:
                conf = tc.get("ai_confidence", tc.get("ml_quality_score", 0.8))
                tc_type = tc.get("test_type", tc.get("type", "unknown"))
                formatted_tests.append({
                    'id': tc.get('id', tc.get('test_id')),
                    'title': tc.get('title', ''),
                    'type': tc_type,
                    'priority': tc.get('priority', 'Medium'),
                    'confidence': round(conf, 2),
                    'preconditions': tc.get('preconditions', []),
                    'test_data': tc.get('test_data', {}),
                    'steps_count': len(tc.get('steps', [])),
                    'steps': tc.get('steps', []),
                    'expected_result': tc.get('expected_result', ''),
                    'validation': tc.get('postconditions', []),
                    'description': tc.get('description', ''),
                    'why_generated': tc.get('why_generated', ''),
                    'domain': tc.get('domain', 'general'),
                    'risk_level': tc.get('risk_level', 'medium'),
                })
                req_confidence += conf
                type_distribution[tc_type] = type_distribution.get(tc_type, 0) + 1

            avg_conf = req_confidence / len(formatted_tests) if formatted_tests else 0
            # Always use sequential per-file ID so rows in the dashboard
            # don't collide on the generator's internal "REQ-XXX-001" tags.
            req_id = f"REQ-{req_idx:03d}"
            # Re-tag every test case with this stable requirement_id and a
            # unique TC id (TC-001-01, TC-001-02 …) so the UI never collides.
            for tc_pos, tc in enumerate(formatted_tests, 1):
                tc['requirement_id'] = req_id
                tc['id'] = f"TC-{req_idx:03d}-{tc_pos:02d}"

            detailed_analysis.append({
                'index': len(detailed_analysis) + 1,
                'requirement_id': req_id,
                'requirement': req_text,
                'word_count': len(req_text.split()),
                'character_count': len(req_text),
                'nlp_confidence': round(avg_conf, 2),
                'test_cases_count': len(formatted_tests),
                'test_cases': formatted_tests,
            })
            total_test_cases += len(formatted_tests)
            total_confidence += avg_conf

        avg_confidence = total_confidence / len(detailed_analysis) if detailed_analysis else 0

        return {
            "status": "success",
            "generator_version": "v4_nlp_spacy",
            "filename": file.filename,
            "file_type": file_type.upper(),
            "total_requirements_in_file": len(requirements),
            "total_requirements_analyzed": len(detailed_analysis),
            "total_requirements_skipped": 0,
            "total_test_cases_generated": total_test_cases,
            "avg_nlp_confidence": round(avg_confidence, 2),
            "detailed": detailed_analysis,
            "quality_metrics": {
                "test_cases_by_type": type_distribution,
                "avg_test_quality_score": round(avg_confidence, 3),
                "nlp_engine": "spaCy (en_core_web_sm)",
                "analysis_pipeline": "dependency_parse → SVO_extraction → semantic_strategy → context_aware_builder",
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
                filename=f"test_report_{report_gen.timestamp.replace(' ', '_').replace(':', '-')}.pdf"
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
