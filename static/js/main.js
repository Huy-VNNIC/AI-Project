// Main JavaScript for Software Effort Estimation Tool

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Setup event listeners
    setupEventListeners();
    
    // Show/hide sections based on method selection
    handleMethodChange();
}

function setupEventListeners() {
    // Method selection change
    const methodSelect = document.getElementById('method');
    if (methodSelect) {
        methodSelect.addEventListener('change', handleMethodChange);
    }

    // Text estimation form
    const textForm = document.getElementById('textEstimationForm');
    if (textForm) {
        textForm.addEventListener('submit', handleTextEstimation);
    }

    // File upload form
    const fileForm = document.getElementById('fileUploadForm');
    if (fileForm) {
        fileForm.addEventListener('submit', handleFileUpload);
    }

    // Manual parameters form
    const manualForm = document.getElementById('manualParametersForm');
    if (manualForm) {
        manualForm.addEventListener('submit', handleManualEstimation);
    }
}

function handleMethodChange() {
    const method = document.getElementById('method')?.value;
    
    // Hide all method-specific sections
    document.querySelectorAll('.method-section').forEach(section => {
        section.style.display = 'none';
    });

    // Show the selected method section
    if (method) {
        const section = document.getElementById(method + 'Section');
        if (section) {
            section.style.display = 'block';
        }
    }
}

async function handleTextEstimation(event) {
    event.preventDefault();
    
    const form = event.target;
    const text = document.getElementById('requirementText').value;
    const method = document.getElementById('method').value || 'weighted_average';

    if (!text.trim()) {
        showError('Please enter requirement text');
        return;
    }

    showLoading('Analyzing requirements and estimating effort...');

    try {
        const response = await fetch('/estimate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                method: method
            })
        });

        const result = await response.json();
        
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
    
    const form = event.target;
    const fileInput = document.getElementById('requirementFile');
    const file = fileInput.files[0];
    const method = document.getElementById('method').value || 'weighted_average';

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
    const method = document.getElementById('method').value || 'weighted_average';

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
    const resultsContainer = document.getElementById('results');
    const resultsSection = document.getElementById('resultsSection');
    
    if (!resultsContainer || !data) {
        console.error('Results container not found or no data');
        return;
    }

    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    // Create results HTML
    let html = `
        <div class="alert alert-success animate__animated animate__fadeIn">
            <h4><i class="bi bi-check-circle"></i> Estimation Complete!</h4>
        </div>
    `;

    // Main estimation result
    if (data.estimated_effort !== undefined) {
        html += `
            <div class="card mb-4 animate__animated animate__slideInUp">
                <div class="card-header bg-primary text-white">
                    <h5><i class="bi bi-calculator"></i> Final Estimation</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h2 class="text-primary">${data.estimated_effort.toFixed(2)} person-months</h2>
                            <p class="text-muted">Integrated estimation using ${data.method || 'weighted average'} method</p>
                        </div>
                        <div class="col-md-6">
                            ${data.confidence_level ? `
                                <div class="mb-2">
                                    <strong>Confidence Level:</strong> 
                                    <span class="badge bg-${getConfidenceBadgeColor(data.confidence_level)}">${data.confidence_level}</span>
                                </div>
                            ` : ''}
                            ${data.project_size ? `
                                <div class="mb-2">
                                    <strong>Estimated Size:</strong> ${data.project_size.toFixed(1)} KLOC
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Individual estimates breakdown
    if (data.individual_estimates) {
        html += `
            <div class="card mb-4 animate__animated animate__slideInUp" style="animation-delay: 0.2s">
                <div class="card-header">
                    <h5><i class="bi bi-bar-chart"></i> Individual Model Estimates</h5>
                </div>
                <div class="card-body">
                    <div class="row">
        `;
        
        const estimates = data.individual_estimates;
        Object.keys(estimates).forEach(model => {
            const value = estimates[model];
            if (value !== null && value !== undefined) {
                html += `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card border-left-primary">
                            <div class="card-body">
                                <h6 class="card-title">${formatModelName(model)}</h6>
                                <h4 class="text-primary">${value.toFixed(2)}</h4>
                                <small class="text-muted">person-months</small>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
    }

    // Project parameters detected
    if (data.extracted_parameters) {
        html += `
            <div class="card mb-4 animate__animated animate__slideInUp" style="animation-delay: 0.4s">
                <div class="card-header">
                    <h5><i class="bi bi-list-check"></i> Extracted Parameters</h5>
                </div>
                <div class="card-body">
                    <div class="row">
        `;
        
        Object.keys(data.extracted_parameters).forEach(param => {
            const value = data.extracted_parameters[param];
            if (value !== null && value !== undefined) {
                html += `
                    <div class="col-md-6 col-lg-4 mb-2">
                        <strong>${formatParameterName(param)}:</strong> 
                        <span class="badge bg-secondary">${value}</span>
                    </div>
                `;
            }
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
    }

    // Recommendations
    if (data.recommendations) {
        html += `
            <div class="card mb-4 animate__animated animate__slideInUp" style="animation-delay: 0.6s">
                <div class="card-header bg-info text-white">
                    <h5><i class="bi bi-lightbulb"></i> Recommendations</h5>
                </div>
                <div class="card-body">
                    <ul class="list-unstyled">
        `;
        
        data.recommendations.forEach(rec => {
            html += `<li class="mb-2"><i class="bi bi-arrow-right text-info"></i> ${rec}</li>`;
        });
        
        html += `
                    </ul>
                </div>
            </div>
        `;
    }

    resultsContainer.innerHTML = html;

    // Create chart if individual estimates exist
    if (data.individual_estimates) {
        createEstimationChart(data.individual_estimates);
    }
}

function createEstimationChart(estimates) {
    const chartContainer = document.getElementById('chartContainer');
    if (!chartContainer) return;

    chartContainer.innerHTML = '<canvas id="estimationChart" width="400" height="200"></canvas>';
    
    const ctx = document.getElementById('estimationChart').getContext('2d');
    
    const labels = Object.keys(estimates).map(formatModelName);
    const values = Object.values(estimates);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Effort (person-months)',
                data: values,
                backgroundColor: [
                    '#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#20c997'
                ],
                borderColor: [
                    '#0056b3', '#1e7e34', '#d39e00', '#bd2130', '#59359a', '#1a9f86'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Person-Months'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Effort Estimation by Model'
                },
                legend: {
                    display: false
                }
            }
        }
    });
}

function showLoading(message = 'Processing...') {
    const loadingDiv = document.getElementById('loading');
    const loadingMessage = document.getElementById('loadingMessage');
    
    if (loadingDiv) {
        loadingDiv.style.display = 'block';
    }
    
    if (loadingMessage) {
        loadingMessage.textContent = message;
    }

    // Disable all forms
    document.querySelectorAll('form').forEach(form => {
        form.style.pointerEvents = 'none';
        form.style.opacity = '0.6';
    });
}

function hideLoading() {
    const loadingDiv = document.getElementById('loading');
    
    if (loadingDiv) {
        loadingDiv.style.display = 'none';
    }

    // Re-enable all forms
    document.querySelectorAll('form').forEach(form => {
        form.style.pointerEvents = 'auto';
        form.style.opacity = '1';
    });
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    
    if (errorDiv) {
        errorDiv.innerHTML = `
            <div class="alert alert-danger alert-dismissible animate__animated animate__shakeX">
                <i class="bi bi-exclamation-triangle"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        errorDiv.scrollIntoView({ behavior: 'smooth' });
    } else {
        alert(message);
    }
}

function getConfidenceBadgeColor(confidence) {
    switch(confidence?.toLowerCase()) {
        case 'high': return 'success';
        case 'medium': return 'warning';
        case 'low': return 'danger';
        default: return 'secondary';
    }
}

function formatModelName(model) {
    const names = {
        'cocomo': 'COCOMO II',
        'function_points': 'Function Points',
        'use_case_points': 'Use Case Points',
        'loc_linear': 'LOC Linear',
        'loc_random_forest': 'LOC Random Forest',
        'ml_ensemble': 'ML Ensemble'
    };
    return names[model] || model.replace(/_/g, ' ').toUpperCase();
}

function formatParameterName(param) {
    const names = {
        'project_size': 'Project Size (KLOC)',
        'complexity': 'Complexity',
        'team_size': 'Team Size',
        'experience': 'Experience Level',
        'reliability': 'Reliability Requirements'
    };
    return names[param] || param.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Utility function to format numbers
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return 'N/A';
    return parseFloat(num).toFixed(decimals);
}
