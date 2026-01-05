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
    
    const requirementText = document.getElementById('requirementText')?.value;
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
    
    const fileInput = document.getElementById('requirementFile');
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

    // Update total effort
    const totalEffort = document.getElementById('totalEffort');
    if (totalEffort && data.total_effort !== undefined) {
        console.log('Updating total effort:', data.total_effort);
        totalEffort.textContent = data.total_effort.toFixed(2);
        console.log('Total effort element after update:', totalEffort.textContent);
    } else {
        console.error('Total effort update failed:', {
            totalEffort: !!totalEffort,
            total_effort_data: data.total_effort
        });
    }

    // Update duration
    const duration = document.getElementById('duration');
    if (duration && data.duration !== undefined) {
        duration.textContent = data.duration.toFixed(1);
        console.log('Duration updated to:', duration.textContent);
    }

    // Update team size  
    const teamSize = document.getElementById('teamSize');
    if (teamSize && data.team_size !== undefined) {
        teamSize.textContent = data.team_size;
        console.log('Team size updated to:', teamSize.textContent);
    }

    // Update confidence level
    const confidenceLevel = document.getElementById('confidenceLevel');
    if (confidenceLevel && data.confidence_level) {
        confidenceLevel.textContent = data.confidence_level;
        confidenceLevel.className = `badge bg-${getConfidenceBadgeColor(data.confidence_level)}`;
        console.log('Confidence level updated to:', confidenceLevel.textContent);
    }

    // Update individual model estimates
    if (data.model_estimates) {
        const estimates = data.model_estimates;
        
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

        // Update chart if it exists
        updateChart(estimates);
    }

    // Update project details
    if (data.project_size) {
        const projectSize = document.getElementById('projectSize');
        if (projectSize) {
            projectSize.textContent = data.project_size.toFixed(1) + ' KLOC';
        }
    }
}

function updateChart(estimates) {
    const chartCanvas = document.getElementById('estimationChart');
    if (!chartCanvas) return;

    const ctx = chartCanvas.getContext('2d');
    
    // Destroy existing chart
    if (currentEstimationChart) {
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

    Object.entries(estimates).forEach(([key, value], index) => {
        if (value && value.effort && value.name) {
            modelNames.push(value.name);
            effortValues.push(value.effort);
            confidenceValues.push(value.confidence || 0);
        }
    });

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
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Effort (Person-months)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            return `Confidence: ${confidenceValues[index]}%`;
                        }
                    }
                }
            }
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
    const fileInput = document.getElementById('requirementFile');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFileBtn = document.getElementById('removeFile');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (fileInfo) fileInfo.classList.remove('d-none');
                if (fileName) fileName.textContent = file.name;
                if (fileSize) {
                    const size = (file.size / 1024).toFixed(1);
                    fileSize.textContent = `${size} KB`;
                }
            }
        });
    }

    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', function() {
            if (fileInput) fileInput.value = '';
            if (fileInfo) fileInfo.classList.add('d-none');
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