// Global variables
let currentEstimationChart = null;
let allTasks = [];
let taskCounter = 0;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupTabSwitching();
    setupFileUpload();
    initializeTaskManager();
});

function setupEventListeners() {
    console.log('Setting up event listeners');
    
    // Text estimation form
    const textForm = document.getElementById('textForm');
    const estimateBtn = document.getElementById('estimateBtn');
    
    console.log('Text form found:', !!textForm);
    console.log('Estimate button found:', !!estimateBtn);
    
    if (textForm) {
        textForm.addEventListener('submit', function(e) {
            console.log('Text form submitted');
            e.preventDefault();
            handleTextEstimation(e);
        });
    }
    
    if (estimateBtn) {
        estimateBtn.addEventListener('click', function(e) {
            console.log('Estimate button clicked');
            e.preventDefault();
            handleTextEstimation(e);
        });
    }

    // Manual estimation form
    const manualForm = document.getElementById('manualForm');
    if (manualForm) {
        manualForm.addEventListener('submit', handleManualEstimation);
    }

    // File upload form
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }
}

async function handleTextEstimation(event) {
    console.log('handleTextEstimation called');
    event.preventDefault();
    
    const requirementText = document.getElementById('requirementsText')?.value;
    const method = document.getElementById('methodSelect')?.value || 'weighted_average';

    console.log('Text input:', requirementText);
    console.log('Method:', method);

    if (!requirementText || !requirementText.trim()) {
        showError('Please enter project requirements');
        return;
    }

    showLoading('Analyzing requirements and calculating estimation...');

    try {
        const requestData = {
            text: requirementText.trim(),
            method: method
        };
        
        console.log('Sending request:', requestData);

        const response = await fetch('/estimate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        console.log('Response status:', response.status);
        const result = await response.json();
        console.log('Response data:', result);
        
        if (response.ok) {
            displayResults(result);
        } else {
            showError(result.detail || 'Estimation failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error occurred');
    } finally {
        hideLoading();
    }
}

async function handleFileUpload(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('requirementsFile'); // Fixed ID to match HTML
    const file = fileInput?.files[0];
    const method = document.getElementById('uploadMethodSelect')?.value || 'weighted_average';

    if (!file) {
        showError('Please select a file');
        return;
    }

    showLoading('Uploading and analyzing file...');

    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('method', method);

        const response = await fetch('/upload-requirements', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (response.ok) {
            displayResults(result);
        } else {
            showError(result.detail || 'File upload failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error occurred');
    } finally {
        hideLoading();
    }
}

async function handleManualEstimation(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const method = document.getElementById('manualMethodSelect')?.value || 'weighted_average';

    showLoading('Calculating estimation...');

    try {
        const params = {};
        formData.forEach((value, key) => {
            if (value) {
                params[key] = parseFloat(value) || value;
            }
        });

        const response = await fetch('/estimate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                parameters: params,
                method: method
            })
        });

        const result = await response.json();
        
        if (response.ok) {
            displayResults(result);
        } else {
            showError(result.detail || 'Manual estimation failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error occurred');
    } finally {
        hideLoading();
    }
}

function displayResults(data) {
    console.log('displayResults called with:', data);
    console.log('Data structure:', JSON.stringify(data, null, 2));
    
    const resultsCard = document.getElementById('resultsCard');
    console.log('Results card element:', resultsCard);
    
    if (!resultsCard || !data) {
        console.error('Results card not found or no data', {
            resultsCard: !!resultsCard,
            data: !!data
        });
        return;
    }

    // Show results card
    resultsCard.classList.remove('d-none');
    resultsCard.scrollIntoView({ behavior: 'smooth' });

    // Extract estimation data (handle both direct and nested structures)
    const estimation = data.estimation || data;
    console.log('Estimation object:', estimation);
    console.log('total_effort value:', estimation.total_effort);
    
    // Update total effort
    const totalEffort = document.getElementById('totalEffort');
    if (totalEffort) {
        if (estimation.total_effort !== undefined) {
            console.log('Updating total effort:', estimation.total_effort);
            totalEffort.textContent = estimation.total_effort.toFixed(2);
            console.log('Total effort element after update:', totalEffort.textContent);
        } else {
            console.error('total_effort is undefined in estimation:', estimation);
            totalEffort.textContent = '-';
        }
    } else {
        console.error('totalEffort element not found');
    }

    // Update duration
    const duration = document.getElementById('duration');
    if (duration) {
        if (estimation.duration !== undefined) {
            duration.textContent = estimation.duration.toFixed(1);
            console.log('Duration updated to:', duration.textContent);
        } else {
            duration.textContent = '-';
        }
    }

    // Update team size  
    const teamSize = document.getElementById('teamSize');
    if (teamSize) {
        if (estimation.team_size !== undefined) {
            teamSize.textContent = Math.ceil(estimation.team_size);
            console.log('Team size updated to:', teamSize.textContent);
        } else {
            teamSize.textContent = '-';
        }
    }

    // Update confidence level
    const confidenceLevel = document.getElementById('confidenceLevel');
    const confidence = estimation.confidence_level || data.confidence?.confidence_level || 'Unknown';
    if (confidenceLevel) {
        confidenceLevel.textContent = confidence;
        confidenceLevel.className = `badge bg-${getConfidenceBadgeColor(confidence)}`;
        console.log('Confidence level updated to:', confidenceLevel.textContent);
    }

    // Update individual model estimates
    const modelEstimates = estimation.model_estimates || data.model_estimates;
    console.log('Model estimates:', modelEstimates);
    console.log('Model estimates type:', typeof modelEstimates);
    console.log('Model estimates keys:', modelEstimates ? Object.keys(modelEstimates) : 'none');
    
    if (modelEstimates && Object.keys(modelEstimates).length > 0) {
        const estimates = modelEstimates;
        
        // Update specific model cards if they exist
        const cocomoValue = document.getElementById('cocomoValue');
        const fpValue = document.getElementById('fpValue');
        const ucpValue = document.getElementById('ucpValue');
        const locValue = document.getElementById('locValue');
        
        if (cocomoValue && estimates.cocomo) {
            cocomoValue.textContent = estimates.cocomo.effort.toFixed(2);
        }
        if (fpValue && estimates.function_points) {
            fpValue.textContent = estimates.function_points.effort.toFixed(2);
        }
        if (ucpValue && estimates.use_case_points) {
            ucpValue.textContent = estimates.use_case_points.effort.toFixed(2);
        }
        if (locValue && (estimates.loc_linear || estimates.loc_random_forest)) {
            const locEstimate = estimates.loc_linear || estimates.loc_random_forest;
            locValue.textContent = locEstimate.effort.toFixed(2);
        }

        // Update chart - ALWAYS call this to show comparison
        console.log('Calling updateChart with estimates');
        updateChart(estimates);
        
        // Update model details section
        updateModelDetailsTable(estimates);
    } else {
        console.error('❌ No model_estimates found in response!');
        console.log('Full data object:', data);
    }

    // Update project details
    const projectSize = data.ml_features?.size || data.analysis?.size;
    if (projectSize) {
        const projectSizeElement = document.getElementById('projectSize');
        if (projectSizeElement) {
            projectSizeElement.textContent = projectSize.toFixed(1) + ' KLOC';
        }
    }
    
    // Update analysis details if available
    if (data.ml_features || data.analysis) {
        updateAnalysisDetails(data.ml_features || data.analysis);
    }
}

function updateModelDetailsTable(estimates) {
    const detailsContent = document.getElementById('modelDetailsContent');
    if (!detailsContent) return;
    
    let tableHTML = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-primary">
                    <tr>
                        <th>Model</th>
                        <th>Effort (PM)</th>
                        <th>Duration (Months)</th>
                        <th>Team Size</th>
                        <th>Confidence (%)</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    Object.entries(estimates).forEach(([key, value]) => {
        if (value && value.effort !== undefined) {
            // Use descriptive name
            let name = value.name || key;
            
            // Better names for ML models
            if (key.startsWith('ml_')) {
                const modelType = key.replace('ml_', '').replace(/_/g, ' ');
                name = `ML: ${modelType}`;
            }
            
            tableHTML += `
                <tr>
                    <td><strong>${name}</strong></td>
                    <td>${value.effort.toFixed(2)}</td>
                    <td>${value.duration ? value.duration.toFixed(1) : '-'}</td>
                    <td>${value.team_size ? Math.ceil(value.team_size) : '-'}</td>
                    <td>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar ${getProgressBarClass(value.confidence || 0)}" 
                                 role="progressbar" 
                                 style="width: ${value.confidence || 0}%"
                                 aria-valuenow="${value.confidence || 0}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                                ${value.confidence || 0}%
                            </div>
                        </div>
                    </td>
                </tr>
            `;
        }
    });
    
    tableHTML += `
                </tbody>
            </table>
        </div>
    `;
    
    detailsContent.innerHTML = tableHTML;
}

function getProgressBarClass(confidence) {
    if (confidence >= 80) return 'bg-success';
    if (confidence >= 60) return 'bg-warning';
    return 'bg-danger';
}

function updateAnalysisDetails(analysis) {
    const analysisContent = document.getElementById('analysisDetailsContent');
    if (!analysisContent) return;
    
    let detailsHTML = '<div class="row">';
    
    if (analysis.size) {
        detailsHTML += `
            <div class="col-md-4 mb-3">
                <div class="card bg-light">
                    <div class="card-body">
                        <h6 class="card-title"><i class="bi bi-file-code"></i> Project Size</h6>
                        <p class="card-text h4">${analysis.size.toFixed(2)} KLOC</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    if (analysis.complexity) {
        detailsHTML += `
            <div class="col-md-4 mb-3">
                <div class="card bg-light">
                    <div class="card-body">
                        <h6 class="card-title"><i class="bi bi-gear"></i> Complexity</h6>
                        <p class="card-text h4">${analysis.complexity}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    if (analysis.requirements_count !== undefined) {
        detailsHTML += `
            <div class="col-md-4 mb-3">
                <div class="card bg-light">
                    <div class="card-body">
                        <h6 class="card-title"><i class="bi bi-list-check"></i> Requirements</h6>
                        <p class="card-text h4">${analysis.requirements_count}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    detailsHTML += '</div>';
    
    analysisContent.innerHTML = detailsHTML;
}

function updateChart(estimates) {
    console.log('=== updateChart called ===');
    console.log('Estimates received:', estimates);
    console.log('Chart.js available?', typeof Chart !== 'undefined');
    
    const chartCanvas = document.getElementById('modelsChart');
    console.log('Canvas element found:', chartCanvas);
    
    if (!chartCanvas) {
        console.error('❌ modelsChart canvas not found in DOM!');
        console.log('Available canvas elements:', document.querySelectorAll('canvas'));
        return;
    }

    const ctx = chartCanvas.getContext('2d');
    console.log('Canvas context:', ctx);
    
    // Destroy existing chart
    if (currentEstimationChart) {
        console.log('Destroying existing chart');
        currentEstimationChart.destroy();
    }

    const modelNames = [];
    const effortValues = [];
    const confidenceValues = [];
    const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
        'rgba(83, 102, 255, 0.8)',
        'rgba(255, 99, 255, 0.8)'
    ];

    console.log('Processing estimates...');
    Object.entries(estimates).forEach(([key, value], index) => {
        console.log(`Processing ${key}:`, value);
        if (value && value.effort !== undefined) {
            // Use descriptive name, fall back to key
            let name = value.name || key;
            
            // Better names for ML models
            if (key.startsWith('ml_')) {
                const modelType = key.replace('ml_', '').replace(/_/g, ' ');
                name = `ML: ${modelType}`;
            }
            
            console.log(`✓ Adding ${name}: effort=${value.effort}`);
            modelNames.push(name);
            effortValues.push(value.effort);
            confidenceValues.push(value.confidence || 0);
        } else {
            console.log(`✗ Skipping ${key}: invalid data`);
        }
    });

    console.log('Final chart data:', { modelNames, effortValues, confidenceValues });
    
    if (modelNames.length === 0) {
        console.error('❌ No valid model data to display!');
        return;
    }

    console.log('Final chart data:', { modelNames, effortValues, confidenceValues });
    
    if (modelNames.length === 0) {
        console.error('❌ No valid model data to display!');
        return;
    }

    // Get scale preference (default to logarithmic)
    const isLogarithmic = true; // Default to logarithmic scale

    console.log('Creating Chart.js instance...');
    try {
        currentEstimationChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: modelNames,
                datasets: [
                    {
                        label: 'Effort (Person-months)',
                        data: effortValues,
                        backgroundColor: colors.slice(0, modelNames.length),
                        borderColor: colors.slice(0, modelNames.length).map(color => color.replace('0.8', '1')),
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        type: isLogarithmic ? 'logarithmic' : 'linear',
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Effort (Person-months)',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            callback: function(value, index, values) {
                                return value.toFixed(2);
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Models',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Effort: ${context.parsed.y.toFixed(2)} person-months`;
                            },
                            afterLabel: function(context) {
                                const index = context.dataIndex;
                                const confidence = confidenceValues[index];
                                return confidence ? `Confidence: ${confidence}%` : '';
                            }
                        }
                    }
                }
            }
        });

        console.log('✅ Chart created successfully!');
        console.log('Chart instance:', currentEstimationChart);
        
        // Setup scale toggle buttons
        setupScaleToggle();
    } catch (error) {
        console.error('❌ Error creating chart:', error);
        console.error('Error stack:', error.stack);
    }
}

function setupScaleToggle() {
    const logButton = document.getElementById('logScale');
    const linearButton = document.getElementById('linearScale');
    
    if (!logButton || !linearButton) return;
    
    logButton.addEventListener('click', function() {
        if (currentEstimationChart) {
            currentEstimationChart.options.scales.y.type = 'logarithmic';
            currentEstimationChart.update();
            logButton.classList.add('active');
            linearButton.classList.remove('active');
        }
    });
    
    linearButton.addEventListener('click', function() {
        if (currentEstimationChart) {
            currentEstimationChart.options.scales.y.type = 'linear';
            currentEstimationChart.update();
            linearButton.classList.add('active');
            logButton.classList.remove('active');
        }
    });
}

function getConfidenceBadgeColor(confidence) {
    if (typeof confidence === 'string') {
        switch (confidence.toLowerCase()) {
            case 'high': return 'success';
            case 'medium': return 'warning';
            case 'low': return 'danger';
            default: return 'secondary';
        }
    }
    
    if (typeof confidence === 'number') {
        if (confidence >= 80) return 'success';
        if (confidence >= 60) return 'warning';
        return 'danger';
    }
    
    return 'secondary';
}

function showLoading(message = 'Processing...') {
    const loadingElement = document.getElementById('loadingSpinner');
    const loadingText = document.getElementById('loadingText');
    
    if (loadingElement) {
        loadingElement.classList.remove('d-none');
    }
    if (loadingText) {
        loadingText.textContent = message;
    }
}

function hideLoading() {
    const loadingElement = document.getElementById('loadingSpinner');
    if (loadingElement) {
        loadingElement.classList.add('d-none');
    }
}

function showError(message) {
    // You can implement a toast notification or alert here
    alert(`Error: ${message}`);
}

function setupTabSwitching() {
    // Handle tab switching functionality
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target');
            console.log('Switched to tab:', targetId);
        });
    });
}

function setupFileUpload() {
    const fileInput = document.getElementById('requirementsFile'); // Fixed ID to match HTML
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFile');
    const dropZone = document.getElementById('dropZone');

    console.log('File upload setup - elements found:', {
        fileInput: !!fileInput,
        fileInfo: !!fileInfo,
        fileName: !!fileName,
        fileSize: !!fileSize,
        dropZone: !!dropZone
    });

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            console.log('File selected:', file);
            if (file) {
                displayFileInfo(file);
            }
        });
    }

    // Add drag and drop functionality
    if (dropZone) {
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                fileInput.files = files; // Set the file input
                displayFileInfo(file);
            }
        });

        dropZone.addEventListener('click', function(e) {
            if (e.target === dropZone || e.target.closest('.file-upload-area')) {
                fileInput.click();
            }
        });
    }

    function displayFileInfo(file) {
        if (fileInfo) fileInfo.classList.remove('d-none');
        if (fileName) fileName.textContent = file.name;
        if (fileSize) {
            const size = file.size > 1024 * 1024 
                ? (file.size / (1024 * 1024)).toFixed(1) + ' MB'
                : (file.size / 1024).toFixed(1) + ' KB';
            fileSize.textContent = size;
        }

        // Update file type icon based on extension
        const fileTypeIcon = document.getElementById('fileTypeIcon');
        if (fileTypeIcon) {
            const extension = file.name.split('.').pop().toLowerCase();
            let iconClass = 'bi-file-earmark-text';
            
            switch(extension) {
                case 'pdf':
                    iconClass = 'bi-file-earmark-pdf';
                    break;
                case 'doc':
                case 'docx':
                    iconClass = 'bi-file-earmark-word';
                    break;
                case 'txt':
                    iconClass = 'bi-file-earmark-text';
                    break;
                case 'md':
                    iconClass = 'bi-file-earmark-code';
                    break;
            }
            
            fileTypeIcon.innerHTML = `<i class="bi ${iconClass} fs-1 text-primary"></i>`;
        }

        console.log('File info displayed:', {
            name: file.name,
            size: file.size,
            type: file.type
        });
    }

    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', function() {
            if (fileInput) fileInput.value = '';
            if (fileInfo) fileInfo.classList.add('d-none');
            if (fileName) fileName.textContent = 'No file selected';
            if (fileSize) fileSize.textContent = '0 KB';
            console.log('File removed');
        });
    }
}

function initializeTaskManager() {
    const addTaskBtn = document.getElementById('addTaskBtn');
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', addNewTask);
    }
}

function addNewTask() {
    taskCounter++;
    const taskList = document.getElementById('taskList');
    if (!taskList) return;

    const taskHtml = `
        <div class="card mb-3 task-card" data-task-id="${taskCounter}">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <input type="text" class="form-control mb-2" placeholder="Task name" required>
                        <textarea class="form-control mb-2" rows="2" placeholder="Task description"></textarea>
                    </div>
                    <div class="col-md-4">
                        <select class="form-select mb-2">
                            <option value="simple">Simple</option>
                            <option value="average" selected>Average</option>
                            <option value="complex">Complex</option>
                        </select>
                        <button type="button" class="btn btn-danger btn-sm" onclick="removeTask(${taskCounter})">
                            <i class="bi bi-trash"></i> Remove
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    taskList.insertAdjacentHTML('beforeend', taskHtml);
}

function removeTask(taskId) {
    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskCard) {
        taskCard.remove();
    }
}