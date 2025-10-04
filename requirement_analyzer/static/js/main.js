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
            
            Object.entries(data.estimation.model_estimates).forEach(([key, value]) => {
                if (value && typeof value === 'object' && value.estimate !== undefined) {
                    // Định dạng mới: {estimate: x, confidence: y}
                    normalizedModels[key] = {
                        name: key,
                        effort: value.estimate,
                        confidence: value.confidence
                    };
                } else {
                    // Định dạng cũ
                    normalizedModels[key] = {
                        name: key,
                        effort: value,
                        confidence: null
                    };
                }
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
                    // Skip metadata fields
                    if (model.includes('_name') || model.includes('_confidence') || 
                        model.includes('_type') || model.includes('_description')) {
                        continue;
                    }
                    
                    // Get the model name from metadata if available
                    const modelNameFromMetadata = data.estimation.model_estimates[`${model}_name`];
                    const modelName = modelNameFromMetadata || details.name || model;
                    
                    let effort = '-';
                    
                    // Xử lý dữ liệu đầu ra theo cách đơn giản
                    if (details.effort_pm !== undefined) {
                        effort = details.effort_pm;
                    } else if (details.estimate !== undefined) {
                        effort = details.estimate;
                    } else if (details.effort !== undefined) {
                        effort = details.effort;
                    } else if (typeof details === 'number') {
                        effort = details;
                    } else {
                        effort = details;
                    }
                    
                    // Get the confidence from metadata if available
                    const confidenceFromMetadata = data.estimation.model_estimates[`${model}_confidence`];
                    let confidence = '-';
                    if (confidenceFromMetadata !== undefined) {
                        confidence = `${confidenceFromMetadata}%`;
                    } else if (details.confidence !== undefined) {
                        confidence = `${details.confidence}%`;
                    }
                    
                    // Get the model type from metadata if available
                    const typeFromMetadata = data.estimation.model_estimates[`${model}_type`];
                    let modelType = typeFromMetadata || "Other";
                    if (!typeFromMetadata) {
                        if (model === 'fallback') modelType = "Estimate";
                        else if (model.toLowerCase().includes('cocomo')) modelType = "COCOMO";
                        else if (model.toLowerCase().includes('function_points')) modelType = "Function Points";
                        else if (model.toLowerCase().includes('use_case')) modelType = "Use Case";
                        else if (model.toLowerCase().includes('loc')) modelType = "LOC";
                    }
                    
                    modelHtml += `<tr>
                        <td><strong>${modelName}</strong></td>
                        <td class="text-end">${effort}</td>
                        <td class="text-center">${confidence}</td>
                        <td><span class="model-badge" style="background-color: ${getModelColor(model)}; color: white;">${modelType}</span></td>
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
                    // Skip metadata fields
                    if (model.includes('_name') || model.includes('_confidence') || 
                        model.includes('_type') || model.includes('_description')) {
                        continue;
                    }
                    
                    // Get the model name from metadata if available
                    const modelNameFromMetadata = data.estimation.model_estimates[`${model}_name`];
                    const modelName = modelNameFromMetadata || details.name || model;
                    
                    const effort = details.effort || details;
                    
                    // Get the confidence from metadata if available
                    const confidenceFromMetadata = data.estimation.model_estimates[`${model}_confidence`];
                    let confidence = '-';
                    if (confidenceFromMetadata !== undefined) {
                        confidence = `${confidenceFromMetadata}%`;
                    } else if (details.confidence) {
                        confidence = `${(details.confidence * 100).toFixed(0)}%`;
                    }
                    
                    modelHtml += `<tr>
                        <td><strong>${modelName}</strong></td>
                        <td class="text-end">${effort}</td>
                        <td class="text-center">${confidence}</td>
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
                
                // Get description from metadata if available
                const descriptionFromMetadata = data.estimation.model_estimates[`${model}_description`];
                const description = descriptionFromMetadata || details.description;
                
                if (description) {
                    const modelNameFromMetadata = data.estimation.model_estimates[`${model}_name`];
                    const displayName = modelNameFromMetadata || details.name || model;
                    
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
            if (!file) return alert('Please select a file.');
            
            // Check file size - limit to 10MB
            const maxSize = 10 * 1024 * 1024; // 10MB in bytes
            if (file.size > maxSize) {
                return alert('File size exceeds the limit (10MB). Please upload a smaller file.');
            }
            
            // Check file extension
            const fileName = file.name;
            const fileExt = fileName.split('.').pop().toLowerCase();
            const allowedExtensions = ['txt', 'doc', 'docx', 'pdf', 'md'];
            
            if (!allowedExtensions.includes(fileExt)) {
                return alert(`Unsupported file format: .${fileExt}\nAllowed formats: ${allowedExtensions.join(', ')}`);
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
            
            // Log dữ liệu đầu vào để gỡ rối
            try {
                console.log("Chart data input:", JSON.stringify(data?.estimation?.model_estimates));
            } catch (e) {
                console.log("Chart data input cannot be stringified", data?.estimation?.model_estimates);
            }
            
            if (!data || !data.estimation || !data.estimation.model_estimates) {
                console.warn("Invalid chart data:", data);
                return;
            }
            
            // Chuẩn hóa model_estimates để xử lý cả định dạng mới và cũ
            const normalizedModels = [];
            const processedModelKeys = new Set(); // Theo dõi các mô hình đã xử lý
            
            // Chuyển đổi cấu trúc dữ liệu để dễ xử lý hơn
            Object.entries(data.estimation.model_estimates).forEach(([key, value]) => {
                // Bỏ qua các thuộc tính metadata
                if (key.includes('_name') || key.includes('_confidence') || 
                    key.includes('_type') || key.includes('_description')) {
                    return;
                }
                
                processedModelKeys.add(key);
                
                // Tạo tên hiển thị thân thiện hơn
                let displayName = key;
                
                // Lấy các metadata của mô hình nếu có
                const modelName = data.estimation.model_estimates[`${key}_name`] || key;
                const modelType = data.estimation.model_estimates[`${key}_type`] || '';
                
                if (key === 'fallback') {
                    displayName = 'Dự toán';  // Đổi thành tiếng Việt
                } else if (modelName && typeof modelName === 'string') {
                    displayName = modelName;
                } else if (key.toLowerCase().includes('cocomo')) {
                    displayName = 'COCOMO II';
                } else if (key.toLowerCase().includes('function_points')) {
                    displayName = 'Function Points';
                } else if (key.toLowerCase().includes('use_case')) {
                    displayName = 'Use Case Points';
                } else if (key.toLowerCase().includes('loc')) {
                    displayName = 'LOC Model';
                }
                
                // Xác định giá trị nỗ lực
                let effortValue = 0;
                try {
                    if (value && typeof value === 'object') {
                        if (value.estimate !== undefined) {
                            effortValue = parseFloat(value.estimate) || 0;
                        } else if (value.effort !== undefined) {
                            effortValue = parseFloat(value.effort) || 0;
                        } else if (value.effort_pm !== undefined) {
                            effortValue = parseFloat(value.effort_pm) || 0;
                        } else {
                            // Nếu không có giá trị nào hợp lệ, gán mặc định
                            effortValue = 1.0;
                        }
                    } else if (typeof value === 'number') {
                        effortValue = value;
                    } else {
                        // Trường hợp không có giá trị nào
                        effortValue = 1.0;
                    }
                    
                    // Đảm bảo có một giá trị hợp lệ 
                    if (isNaN(effortValue) || !isFinite(effortValue)) {
                        effortValue = 1.0; // Đặt một giá trị mặc định có ý nghĩa
                    }
                    
                    // Log ra giá trị đã xử lý để gỡ rối
                    console.log(`Key: ${key}, Display: ${displayName}, Value:`, value, "Effort:", effortValue);
                } catch (error) {
                    console.error(`Error processing effort value for ${key}:`, error);
                    effortValue = 1.0; // Sử dụng giá trị mặc định có ý nghĩa thay vì 0
                }
                
                // Xác định màu sắc
                let color = '#0d6efd'; // Màu mặc định
                if (key === 'fallback') {
                    color = '#20c997'; // Teal cho fallback
                } else if (key.toLowerCase().includes('cocomo')) {
                    color = '#0d6efd'; // Blue cho COCOMO
                } else if (key.toLowerCase().includes('function_points')) {
                    color = '#198754'; // Green cho Function Points
                } else if (key.toLowerCase().includes('use_case')) {
                    color = '#6610f2'; // Purple cho Use Case
                } else if (key.toLowerCase().includes('loc')) {
                    color = '#fd7e14'; // Orange cho LOC
                } else if (key.toLowerCase().includes('ml_')) {
                    color = '#dc3545'; // Red cho ML
                }
                
                normalizedModels.push({
                    key: key,
                    name: displayName,
                    effort: effortValue,
                    color: color
                });
            });
            
            // Sắp xếp để đảm bảo fallback lên đầu
            normalizedModels.sort((a, b) => {
                if (a.key === 'fallback') return -1;
                if (b.key === 'fallback') return 1;
                return 0;
            });
            
            // Chart data
            const chartData = {
                labels: normalizedModels.map(model => model.name),
                datasets: [{
                    label: 'Effort (person-months)',
                    data: normalizedModels.map(model => model.effort),
                    backgroundColor: normalizedModels.map(model => model.color)
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
                        title: {
                            display: true,
                            text: scaleType === 'logarithmic' 
                                ? 'Effort (person-months, log scale)' 
                                : 'Effort (person-months)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value;
                            }
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
