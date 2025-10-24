// main.js - Handles UI logic and API calls for the Software Effort Estimation Tool

document.addEventListener('DOMContentLoaded', function () {
    // Tab: Text Input
    const textForm = document.getElementById('textForm');
    const requirementsText = document.getElementById('requirementsText');
    const methodSelect = document.getElementById('methodSelect');

    // Tab: Upload Document
    const uploadForm = document.getElementById('uploadForm');
    const requirementsFile = document.getElementById('requirementsFile');
    const uploadMethodSelect = document.getElementById('uploadMethodSelect');

    // Tab: Task List
    const addTaskBtn = document.getElementById('addTaskBtn');
    const taskList = document.getElementById('taskList');
    const estimateTasksBtn = document.getElementById('estimateTasksBtn');
    const tasksMethodSelect = document.getElementById('tasksMethodSelect');

    // Results
    const resultsCard = document.getElementById('resultsCard');
    const totalEffort = document.getElementById('totalEffort');
    const duration = document.getElementById('duration');
    const teamSize = document.getElementById('teamSize');
    const confidenceLevel = document.getElementById('confidenceLevel');
    const modelDetailsContent = document.getElementById('modelDetailsContent');
    const analysisDetailsContent = document.getElementById('analysisDetailsContent');
    const logScaleBtn = document.getElementById('logScale');
    const linearScaleBtn = document.getElementById('linearScale');
    let modelsChart = null;
    let currentChartData = null;
    let currentScaleType = 'logarithmic';

    // Helper: Show results
    function showResults(data) {
        console.log("Received data:", data); // Debug: Log the data we receive
        resultsCard.classList.remove('d-none');
        
        // Fix model_estimates data structure first if it exists
        if (data && data.estimation && data.estimation.model_estimates) {
            // Process model_estimates to fix [object Object] display issues
            const fixedModels = {};
            
            Object.entries(data.estimation.model_estimates).forEach(([key, value]) => {
                // Skip old metadata fields if present
                if (key.endsWith('_name') || key.endsWith('_confidence') || 
                    key.endsWith('_type') || key.endsWith('_description')) {
                    return;
                }
                
                // If value is an object (new format) - convert to consistent format
                if (value && typeof value === 'object') {
                    fixedModels[key] = {
                        effort: value.effort || value.estimate || 0,
                        confidence: value.confidence || 70,
                        type: value.type || "Other", 
                        name: value.name || key,
                        description: value.description || ""
                    };
                } else {
                    // If value is a number (old format) - convert to object
                    fixedModels[key] = {
                        effort: value,
                        confidence: 70,
                        type: "Unknown",
                        name: key,
                        description: ""
                    };
                }
            });
            
            // Replace with fixed models
            data.estimation.model_estimates = fixedModels;
        }
        
        // Ngăn chặn các hành động có thể gây tải lại trang
        try {
            if (window.stop) {
                window.stop();
            }
            
            // Ngăn chặn các redirect không mong muốn
            history.pushState(null, null, window.location.href);
            window.onpopstate = function() {
                history.go(1);
            };
        } catch (e) {
            console.warn('Could not prevent page navigation:', e);
        }
        
        try {
            // Store the data for chart scale toggling
            currentChartData = data;
        
        // Summary - Xử lý định dạng mới từ API
        if (data.estimation?.integrated_estimate) {
            totalEffort.textContent = data.estimation.integrated_estimate + ' person-months';
        } else if (data.estimation?.total_effort) {
            totalEffort.textContent = data.estimation.total_effort + ' person-months';
        } else {
            totalEffort.textContent = '-';
        }
        
        duration.textContent = data.estimation?.duration ? data.estimation.duration + ' months' : '-';
        teamSize.textContent = data.estimation?.team_size ? data.estimation.team_size : '-';
        
        if (typeof data.estimation?.confidence_level === 'number') {
            confidenceLevel.textContent = data.estimation.confidence_level + '%';
        } else {
            confidenceLevel.textContent = data.estimation?.confidence_level || '-';
        }
        
        // Model details
        let modelHtml = '';
        if (data.estimation?.model_estimates) {
            // Chuẩn hóa model_estimates để xử lý cả định dạng mới và cũ
            const normalizedModels = {};
            
            console.log("Processing model estimates:", JSON.stringify(data.estimation.model_estimates));
            
            Object.entries(data.estimation.model_estimates).forEach(([key, value]) => {
                // Skip metadata fields
                if (key.endsWith('_name') || key.endsWith('_confidence') || 
                    key.endsWith('_type') || key.endsWith('_description')) {
                    return;
                }
                
                let modelName = key;
                let modelEffort = 0;
                let modelConfidence = null;
                let modelType = "";
                let modelDesc = "";
                
                // New format: value is an object with effort, confidence, name, type, description
                if (value && typeof value === 'object') {
                    if (value.name) modelName = value.name;
                    
                    if (value.effort !== undefined) {
                        modelEffort = value.effort;
                    } else if (value.estimate !== undefined) {
                        modelEffort = value.estimate;
                    } else if (value.effort_pm !== undefined) {
                        modelEffort = value.effort_pm;
                    }
                    
                    if (value.confidence) modelConfidence = value.confidence;
                    if (value.type) modelType = value.type;
                    if (value.description) modelDesc = value.description;
                } 
                // Old format: value is a direct number
                else if (typeof value === 'number') {
                    modelEffort = value;
                }
                
                // If we still don't have a type, guess from the key name
                if (!modelType) {
                    if (key.toLowerCase().includes('cocomo')) modelType = "COCOMO";
                    else if (key.toLowerCase().includes('function_points')) modelType = "Function Points";
                    else if (key.toLowerCase().includes('use_case')) modelType = "Use Case";
                    else if (key.toLowerCase().includes('loc')) modelType = "LOC";
                    else if (key.toLowerCase().includes('ml_')) modelType = "ML";
                    else modelType = "Other";
                }
                
                normalizedModels[key] = {
                    name: modelName,
                    effort: modelEffort,
                    confidence: modelConfidence,
                    type: modelType,
                    description: modelDesc
                };
                
                console.log("Normalized model:", key, normalizedModels[key]);
            });
            
            // Sort models by type (traditional first, then ML models)
            const sortedModels = Object.entries(normalizedModels).sort((a, b) => {
                const isAML = a[0].startsWith('ml_');
                const isBML = b[0].startsWith('ml_');
                return isAML === isBML ? 0 : isAML ? 1 : -1;
            });
            
            // Traditional models section
            const traditionalModels = sortedModels.filter(([key]) => !key.startsWith('ml_'));
            if (traditionalModels.length > 0) {
                modelHtml += '<div class="model-type-header">Traditional Models</div>';
                
                // Create table for traditional models
                modelHtml += `<table class="results-table">
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Effort (PM)</th>
                            <th>Confidence</th>
                            <th>Type</th>
                        </tr>
                    </thead>
                    <tbody>`;
                
                for (const [model, details] of traditionalModels) {
                    // Force the values to be primitive types, not objects
                    const modelName = typeof details.name === 'string' ? details.name : model;
                    
                    // Handle effort value - make sure it's a number or string, not an object
                    let effortValue = '-';
                    if (details.effort !== undefined) {
                        if (typeof details.effort === 'object') {
                            // If effort is an object, try to get a useful property or use 0
                            effortValue = JSON.stringify(details.effort);
                        } else {
                            effortValue = details.effort;
                        }
                    }
                    
                    // Handle confidence - make sure it's a string with %
                    let confidenceValue = '-';
                    if (details.confidence !== undefined) {
                        if (typeof details.confidence === 'object') {
                            confidenceValue = '-';
                        } else {
                            confidenceValue = `${details.confidence}%`;
                        }
                    }
                    
                    // Handle type - make sure it's a string
                    let typeValue = 'Other';
                    if (details.type !== undefined && typeof details.type === 'string') {
                        typeValue = details.type;
                    } else if (model.toLowerCase().includes('cocomo')) {
                        typeValue = "COCOMO";
                    } else if (model.toLowerCase().includes('function_points')) {
                        typeValue = "Function Points";
                    } else if (model.toLowerCase().includes('use_case')) {
                        typeValue = "Use Case";
                    } else if (model.toLowerCase().includes('loc')) {
                        typeValue = "LOC";
                    }
                    
                    modelHtml += `<tr>
                        <td><strong>${modelName}</strong></td>
                        <td class="text-end">${effortValue}</td>
                        <td class="text-center">${confidenceValue}</td>
                        <td><span class="model-badge" style="background-color: ${getModelColor(model)}; color: white;">${typeValue}</span></td>
                    </tr>`;
                }
                modelHtml += '</tbody></table>';
            }
            
            // ML models section
            const mlModels = sortedModels.filter(([key]) => key.startsWith('ml_'));
            if (mlModels.length > 0) {
                modelHtml += '<div class="model-type-header">Machine Learning Models</div>';
                
                // Create table for ML models
                modelHtml += `<table class="results-table">
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Effort (PM)</th>
                            <th>Confidence</th>
                            <th>Type</th>
                        </tr>
                    </thead>
                    <tbody>`;
                
                for (const [model, details] of mlModels) {
                    // Force the values to be primitive types, not objects
                    const modelName = typeof details.name === 'string' ? details.name : model;
                    
                    // Handle effort value - make sure it's a number or string, not an object
                    let effortValue = '-';
                    if (details.effort !== undefined) {
                        if (typeof details.effort === 'object') {
                            // If effort is an object, try to get a useful property or use 0
                            effortValue = JSON.stringify(details.effort);
                        } else {
                            effortValue = details.effort;
                        }
                    }
                    
                    // Handle confidence - make sure it's a string with % and has a reasonable value (0-100%)
                    let confidenceValue = '-';
                    if (details.confidence !== undefined) {
                        if (typeof details.confidence === 'object') {
                            confidenceValue = '-';
                        } else {
                            // Make sure confidence is a number between 0-100
                            let confNum = parseFloat(details.confidence);
                            if (!isNaN(confNum)) {
                                // For ML models, sometimes there's a scaling issue - fix it if needed
                                if (confNum > 100 && model.startsWith('ml_')) {
                                    confNum = confNum / 100;
                                }
                                // If confidence is still greater than 100, cap it at 100%
                                confNum = Math.min(confNum, 100);
                                confidenceValue = `${Math.round(confNum)}%`;
                            } else {
                                confidenceValue = '-';
                            }
                        }
                    }
                    
                    modelHtml += `<tr>
                        <td><strong>${modelName}</strong></td>
                        <td class="text-end">${effortValue}</td>
                        <td class="text-center">${confidenceValue}</td>
                        <td><span class="model-badge" style="background-color: #dc3545; color: white;">ML</span></td>
                    </tr>`;
                }
                modelHtml += '</tbody></table>';
            }
            
            // Add model descriptions in smaller format
            modelHtml += '<div class="mt-4">';
            modelHtml += '<div class="model-type-header">Model Descriptions</div>';
            modelHtml += '<div class="small">';
            for (const [model, details] of sortedModels) {
                // Skip metadata fields
                if (model.includes('_name') || model.includes('_confidence') || 
                    model.includes('_type') || model.includes('_description')) {
                    continue;
                }
                
                // Our normalization already handled descriptions
                const description = details.description || '';
                
                if (description) {
                    const displayName = details.name || model;
                    
                    modelHtml += `<div class="model-description mb-2 p-2 border-start border-3" style="border-color: ${getModelColor(model)} !important;">
                        <strong>${displayName}:</strong> ${description}
                    </div>`;
                }
            }
            modelHtml += '</div></div>';
        }
        modelDetailsContent.innerHTML = modelHtml || '<em>No model details available.</em>';
        
        // Helper function to get color for model
        function getModelColor(modelKey) {
            if (modelKey === 'fallback') return '#20c997'; // Teal color for fallback
            if (modelKey.toLowerCase().includes('cocomo')) return '#0d6efd';
            if (modelKey.toLowerCase().includes('function_points')) return '#198754';
            if (modelKey.toLowerCase().includes('use_case')) return '#6610f2';
            if (modelKey.toLowerCase().includes('loc')) return '#fd7e14';  // Orange color for LOC models
            if (modelKey.toLowerCase().includes('ml_')) return '#dc3545';
            return '#0d6efd';
        }
        
        // Analysis details
        analysisDetailsContent.innerHTML = `<pre class="json">${JSON.stringify(data.analysis, null, 2)}</pre>`;
        
        // Chart
        if (modelsChart) modelsChart.destroy();
        
        if (data.estimation?.model_estimates) {
            const canvas = document.getElementById('modelsChart');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                
                // Clear previous chart
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Create chart with current scale type
                createChart(ctx, data, currentScaleType);
            }
        }
        } catch (error) {
            console.error("Error in showResults:", error);
            modelDetailsContent.innerHTML = `<div class="alert alert-danger">Lỗi hiển thị kết quả: ${error.message}</div>`;
        }
    }

    // Helper: Show loading with improved progress indication
    function showLoading() {
        resultsCard.classList.remove('d-none');
        totalEffort.textContent = duration.textContent = teamSize.textContent = confidenceLevel.textContent = '-';
        
        // Show an animated loading indicator with steps
        modelDetailsContent.innerHTML = `
            <div class="card border-info mb-3">
                <div class="card-header bg-info text-white">
                    <i class="bi bi-gear-wide-connected"></i> Processing Request
                </div>
                <div class="card-body">
                    <div class="progress mb-3">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 100%"></div>
                    </div>
                    
                    <div id="processingSteps">
                        <div class="d-flex align-items-center mb-2">
                            <div class="spinner-border spinner-border-sm text-primary me-2"></div>
                            <span>Analyzing document content...</span>
                        </div>
                        <div class="d-flex align-items-center mb-2 text-muted">
                            <i class="bi bi-clock me-2"></i>
                            <span>Extracting requirements...</span>
                        </div>
                        <div class="d-flex align-items-center mb-2 text-muted">
                            <i class="bi bi-clock me-2"></i>
                            <span>Applying estimation models...</span>
                        </div>
                        <div class="d-flex align-items-center text-muted">
                            <i class="bi bi-clock me-2"></i>
                            <span>Generating final estimate...</span>
                        </div>
                    </div>
                    
                    <p class="text-center mt-3 mb-0">
                        <i class="bi bi-info-circle"></i> This may take up to 30 seconds depending on document size.
                    </p>
                </div>
            </div>
        `;
        
        analysisDetailsContent.innerHTML = '';
        if (modelsChart) modelsChart.destroy();
        
        // Simulate progress through steps (for visual feedback only)
        setTimeout(() => {
            try {
                document.querySelector('#processingSteps div:nth-child(1)').innerHTML = 
                    '<i class="bi bi-check-circle-fill text-success me-2"></i><span>Document content analyzed</span>';
                document.querySelector('#processingSteps div:nth-child(2)').innerHTML = 
                    '<div class="spinner-border spinner-border-sm text-primary me-2"></div><span>Extracting requirements...</span>';
            } catch (e) {
                console.log('Animation step skipped, likely due to early response');
            }
        }, 800);
        
        setTimeout(() => {
            try {
                document.querySelector('#processingSteps div:nth-child(2)').innerHTML = 
                    '<i class="bi bi-check-circle-fill text-success me-2"></i><span>Requirements extracted</span>';
                document.querySelector('#processingSteps div:nth-child(3)').innerHTML = 
                    '<div class="spinner-border spinner-border-sm text-primary me-2"></div><span>Applying estimation models...</span>';
            } catch (e) {
                console.log('Animation step skipped, likely due to early response');
            }
        }, 1600);
        
        setTimeout(() => {
            try {
                document.querySelector('#processingSteps div:nth-child(3)').innerHTML = 
                    '<i class="bi bi-check-circle-fill text-success me-2"></i><span>Models applied</span>';
                document.querySelector('#processingSteps div:nth-child(4)').innerHTML = 
                    '<div class="spinner-border spinner-border-sm text-primary me-2"></div><span>Generating final estimate...</span>';
            } catch (e) {
                console.log('Animation step skipped, likely due to early response');
            }
        }, 2400);
    }

    // Helper: Hide results
    function hideResults() {
        resultsCard.classList.add('d-none');
    }
    
    // Helper: Hide loading animation
    function hideLoading() {
        // This doesn't hide the results card but removes the loading indicators
        document.querySelectorAll('.spinner-border, .progress-bar-animated').forEach(el => {
            el.classList.remove('spinner-border', 'progress-bar-animated', 'progress-bar-striped');
        });
    }

    // Text Input Form Submit
    if (textForm) {
        textForm.addEventListener('submit', function (e) {
            e.preventDefault(); // Ngăn chặn form submit mặc định
            e.stopPropagation(); // Ngăn chặn sự kiện lan truyền
            e.stopImmediatePropagation(); // Ngăn chặn các event handler khác
            
            try {
                const text = requirementsText.value.trim();
                const method = methodSelect.value;
                if (!text) {
                    alert('Please enter requirements text.');
                    return false;
                }
                
                showLoading();
                // Get current host including port
                const currentHost = window.location.origin;
                
                fetch(`${currentHost}/estimate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, method })
                })
                .then(res => {
                    if (!res.ok) {
                        throw new Error(`HTTP error! Status: ${res.status}`);
                    }
                    return res.json();
                })
                .then(data => {
                    showResults(data);
                })
                .catch(error => {
                    console.error("Estimation failed:", error);
                    alert('Estimation failed: ' + error.message);
                });
            } catch (err) {
                console.error("Error submitting form:", err);
                alert('An error occurred while submitting the form. Please try again.');
            }
        });
    }

    // Upload Form Submit
    if (uploadForm) {
        uploadForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const file = requirementsFile.files[0];
            const method = uploadMethodSelect.value;
            
            // Validation now handled in file-upload.js
            if (!file) {
                if (window.showToast) {
                    window.showToast('Please select a file.', 'warning');
                } else {
                    alert('Please select a file.');
                }
                return;
            }
            
            showLoading();
            const formData = new FormData();
            formData.append('file', file);
            formData.append('method', method);
            
            // Add upload info to results card
            modelDetailsContent.innerHTML = `
                <div class="alert alert-info">
                    <h5><i class="bi bi-file-earmark"></i> Processing Document</h5>
                    <p>File: <strong>${fileName}</strong><br>
                    Size: <strong>${formatBytes(file.size)}</strong><br>
                    Type: <strong>${file.type || 'Unknown'}</strong></p>
                </div>
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 100%"></div>
                </div>
            `;
            
            // Get current host including port
            const currentHost = window.location.origin;
            
            fetch(`${currentHost}/upload-requirements`, {
                method: 'POST',
                body: formData
            })
            .then(res => {
                if (!res.ok) {
                    return res.json().then(err => {
                        throw new Error(err.detail || `HTTP error! Status: ${res.status}`);
                    });
                }
                return res.json();
            })
            .then(data => {
                // Add document details to results if available
                if (data.document) {
                    const docInfo = data.document;
                    data.analysis = data.analysis || {};
                    data.analysis.document_info = {
                        filename: docInfo.filename,
                        file_type: docInfo.file_type,
                        size: formatBytes(docInfo.size_bytes),
                        text_length: docInfo.text_length + " characters"
                    };
                }
                
                showResults(data);
            })
            .catch(error => {
                console.error("Upload failed:", error);
                hideLoading();
                
                // Show more detailed error information
                modelDetailsContent.innerHTML = `
                    <div class="alert alert-danger">
                        <h5><i class="bi bi-exclamation-triangle"></i> Upload Failed</h5>
                        <p><strong>Error:</strong> ${error.message}</p>
                        <hr>
                        <p class="mb-0">Suggestions:</p>
                        <ul>
                            <li>Check if the file is not corrupted</li>
                            <li>Try another file format (.txt or .md files work best)</li>
                            <li>Ensure the file contains proper requirement text</li>
                            <li>Refresh the page and try again</li>
                        </ul>
                        <button class="btn btn-outline-danger btn-sm mt-2" onclick="document.getElementById('requirementsFile').click()">
                            <i class="bi bi-arrow-repeat"></i> Try Another File
                        </button>
                    </div>
                `;
                
                // Display the results card to show the error
                resultsCard.classList.remove('d-none');
            });
        });
        
        // Helper function to format bytes to human-readable format
        function formatBytes(bytes, decimals = 2) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        }
    }

    // Task List Logic
    function getTasks() {
        const tasks = [];
        document.querySelectorAll('.task-item').forEach(item => {
            tasks.push({
                title: item.querySelector('.task-title').value,
                description: item.querySelector('.task-description').value,
                priority: item.querySelector('.task-priority').value,
                complexity: item.querySelector('.task-complexity').value
            });
        });
        return tasks;
    }

    function addTask() {
        const template = document.getElementById('taskTemplate');
        if (template) {
            const clone = template.content.cloneNode(true);
            clone.querySelector('.delete-task-btn').addEventListener('click', function () {
                this.closest('.task-item').remove();
            });
            taskList.appendChild(clone);
        }
    }

    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', addTask);
    }

    if (estimateTasksBtn) {
        estimateTasksBtn.addEventListener('click', function () {
            const tasks = getTasks();
            const method = tasksMethodSelect.value;
            if (!tasks.length) return alert('Please add at least one task.');
            showLoading();
            // Get current host including port
            const currentHost = window.location.origin;
            
            fetch(`${currentHost}/estimate-from-tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tasks, method })
            })
            .then(res => {
                if (!res.ok) {
                    throw new Error(`HTTP error! Status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                showResults(data);
            })
            .catch(error => {
                console.error("Task estimation failed:", error);
                alert('Task estimation failed: ' + error.message);
            });
        });
    }

    // Jira/Trello Integration
    const jiraImportBtn = document.getElementById('jiraImportBtn');
    const trelloImportBtn = document.getElementById('trelloImportBtn');

    if (jiraImportBtn) {
        jiraImportBtn.addEventListener('click', function () {
            const modal = bootstrap.Modal.getInstance(document.getElementById('jiraModal'));
            if (modal) modal.hide();
            alert('Jira integration is not fully implemented in this demo.');
        });
    }

    if (trelloImportBtn) {
        trelloImportBtn.addEventListener('click', function () {
            const modal = bootstrap.Modal.getInstance(document.getElementById('trelloModal'));
            if (modal) modal.hide();
            alert('Trello integration is not fully implemented in this demo.');
        });
    }

    // Hide results on tab change
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(btn => {
        btn.addEventListener('click', hideResults);
    });
    
    // Helper: Create chart with specified scale
    function createChart(ctx, data, scaleType) {
        try {
            if (modelsChart) {
                try {
                    modelsChart.destroy();
                } catch (err) {
                    console.warn('Error destroying chart:', err);
                }
            }
            
            if (!data || !data.estimation || !data.estimation.model_estimates) {
                console.warn("Invalid chart data:", data);
                return;
            }

            // Create normalized models here inside the function
            const normalizedModels = {};
            Object.entries(data.estimation.model_estimates).forEach(([key, value]) => {
                if (key.endsWith('_name') || key.endsWith('_confidence') || 
                    key.endsWith('_type') || key.endsWith('_description')) {
                    return;
                }
                
                let modelName = key;
                let modelEffort = 0;
                let modelType = "";
                
                if (value && typeof value === 'object') {
                    if (value.name) modelName = value.name;
                    if (value.effort !== undefined) modelEffort = value.effort;
                    else if (value.estimate !== undefined) modelEffort = value.estimate;
                    else if (value.effort_pm !== undefined) modelEffort = value.effort_pm;
                    if (value.type) modelType = value.type;
                } else if (typeof value === 'number') {
                    modelEffort = value;
                }
                
                if (!modelType) {
                    if (key.toLowerCase().includes('cocomo')) modelType = "COCOMO";
                    else if (key.toLowerCase().includes('function_points')) modelType = "Function Points";
                    else if (key.toLowerCase().includes('use_case')) modelType = "Use Case";
                    else if (key.toLowerCase().includes('loc')) modelType = "LOC";
                    else if (key.toLowerCase().includes('ml_')) modelType = "ML";
                    else modelType = "Other";
                }
                
                normalizedModels[key] = {
                    name: modelName,
                    effort: parseFloat(modelEffort) || 0,
                    type: modelType
                };
            });
            
            const chartModels = [];
            
            // Convert normalized models to chart format
            Object.entries(normalizedModels).forEach(([key, value]) => {
                // Ensure we have a valid effort value
                let effortValue = 0;
                try {
                    if (value.effort !== undefined) {
                        if (typeof value.effort === 'object') {
                            // If it's an object, try to extract estimate or effort property
                            if (value.effort.estimate !== undefined) {
                                effortValue = parseFloat(value.effort.estimate) || 0;
                            } else if (value.effort.effort !== undefined) {
                                effortValue = parseFloat(value.effort.effort) || 0;
                            } else if (value.effort.effort_pm !== undefined) {
                                effortValue = parseFloat(value.effort.effort_pm) || 0;
                            } else {
                                // Just parse the object to string as a fallback
                                console.warn(`Complex effort object for ${key}:`, value.effort);
                                effortValue = 1.0;
                            }
                        } else {
                            // Simple value case
                            effortValue = parseFloat(value.effort) || 0;
                        }
                    } else if (value.estimate !== undefined) {
                        effortValue = parseFloat(value.estimate) || 0;
                    }
                    
                    // Final sanity check
                    if (isNaN(effortValue) || !isFinite(effortValue)) {
                        console.warn(`Invalid effort value for ${key}:`, value.effort);
                        effortValue = 1.0; // Sensible default
                    }
                } catch (error) {
                    console.error(`Error processing effort for ${key}:`, error);
                    effortValue = 1.0; // Fallback on error
                }
                
                // Determine color based on model type
                let color = '#0d6efd'; // Default blue
                if (key === 'fallback') {
                    color = '#20c997'; // Teal for fallback
                } else if (key.toLowerCase().includes('cocomo')) {
                    color = '#0d6efd'; // Blue for COCOMO
                } else if (key.toLowerCase().includes('function_points')) {
                    color = '#198754'; // Green for Function Points
                } else if (key.toLowerCase().includes('use_case')) {
                    color = '#6610f2'; // Purple for Use Case
                } else if (key.toLowerCase().includes('loc')) {
                    color = '#fd7e14'; // Orange for LOC
                } else if (key.toLowerCase().includes('ml_')) {
                    color = '#dc3545'; // Red for ML
                }
                
                chartModels.push({
                    key: key,
                    name: value.name || key,
                    effort: effortValue,
                    color: color
                });
                
                console.log(`Chart model: ${key}, Name: ${value.name}, Effort: ${effortValue}`);
            });
            
            // Sort to ensure fallback is first
            chartModels.sort((a, b) => {
                if (a.key === 'fallback') return -1;
                if (b.key === 'fallback') return 1;
                return 0;
            });
            
            // Chart data
            const chartData = {
                labels: chartModels.map(model => model.name),
                datasets: [{
                    label: 'Effort (person-months)',
                    data: chartModels.map(model => model.effort),
                    backgroundColor: chartModels.map(model => model.color)
                }]
            };
            
            // Chart options
            const options = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Effort: ${context.parsed.y.toFixed(2)} person-months`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        type: scaleType,
                        beginAtZero: scaleType === 'linear',
                        min: scaleType === 'logarithmic' ? 0.1 : 0,
                        title: {
                            display: true,
                            text: scaleType === 'logarithmic' 
                                ? 'Effort (person-months, log scale)' 
                                : 'Effort (person-months)'
                        },
                        ticks: {
                            callback: function(value) {
                                if (scaleType === 'logarithmic') {
                                    return value.toFixed(1);
                                }
                                return value.toFixed(0);
                            }
                        }
                    },
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            };
            
            // Create chart
            modelsChart = new Chart(ctx, {
                type: 'bar',
                data: chartData,
                options: options
            });
        } catch (error) {
            console.error("Error creating chart:", error);
            // Hiển thị thông báo lỗi nếu cần
            ctx.font = '14px Arial';
            ctx.fillStyle = 'red';
            ctx.textAlign = 'center';
            ctx.fillText('Không thể hiển thị biểu đồ: ' + error.message, ctx.canvas.width/2, 50);
        }
    }
    
    // Scale toggle handlers
    if (logScaleBtn && linearScaleBtn) {
        logScaleBtn.addEventListener('click', function() {
            if (currentScaleType !== 'logarithmic' && currentChartData) {
                currentScaleType = 'logarithmic';
                logScaleBtn.classList.add('active');
                linearScaleBtn.classList.remove('active');
                
                const canvas = document.getElementById('modelsChart');
                if (canvas) {
                    const ctx = canvas.getContext('2d');
                    createChart(ctx, currentChartData, currentScaleType);
                }
            }
        });
        
        linearScaleBtn.addEventListener('click', function() {
            if (currentScaleType !== 'linear' && currentChartData) {
                currentScaleType = 'linear';
                linearScaleBtn.classList.add('active');
                logScaleBtn.classList.remove('active');
                
                const canvas = document.getElementById('modelsChart');
                if (canvas) {
                    const ctx = canvas.getContext('2d');
                    createChart(ctx, currentChartData, currentScaleType);
                }
            }
        });
    }
});
