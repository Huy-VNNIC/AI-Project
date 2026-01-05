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
    // Text form submission
    const textForm = document.getElementById('textForm');
    if (textForm) {
        textForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleTextEstimation(e);
        });
    }

    // File upload form submission  
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFileUpload(e);
        });
    }

    console.log('Event listeners setup completed');
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
    console.log('handleTextEstimation called');
    event.preventDefault();
    
    const text = document.getElementById('requirementsText').value;
    const method = document.getElementById('methodSelect').value || 'weighted_average';

    console.log('Form data:', { text: text.length, method });

    if (!text.trim()) {
        showError('Please enter requirement text');
        return;
    }

    showLoading('Analyzing requirements and estimating effort...');

    try {
        const requestData = {
            text: text,
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
    console.log('displayResults called with:', data);
    
    // Wait a bit for DOM to be ready
    setTimeout(() => {
        const resultsCard = document.getElementById('resultsCard');
        const totalEffort = document.getElementById('totalEffort');
        
        console.log('Elements found:', {
            resultsCard: !!resultsCard,
            totalEffort: !!totalEffort,
            resultsCardExists: document.querySelector('#resultsCard') !== null,
            totalEffortExists: document.querySelector('#totalEffort') !== null
        });
        
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

        // Update total effort with more explicit logging
        if (totalEffort && data.total_effort !== undefined) {
            console.log('Updating total effort:', data.total_effort);
            totalEffort.textContent = data.total_effort.toFixed(2);
            console.log('Total effort updated to:', totalEffort.textContent);
        } else {
            console.error('Total effort update failed:', {
                totalEffort: !!totalEffort,
                total_effort_data: data.total_effort
            });
        }
    }, 100);

        // Update duration
        const duration = document.getElementById('duration');
        if (duration && data.duration !== undefined) {
            duration.textContent = data.duration.toFixed(1);
            console.log('Duration updated to:', duration.textContent);
        } else {
            console.error('Duration update failed:', {
                duration: !!duration,
                duration_data: data.duration
            });
        }

        // Update team size  
        const teamSize = document.getElementById('teamSize');
        if (teamSize && data.team_size !== undefined) {
            teamSize.textContent = data.team_size;
            console.log('Team size updated to:', teamSize.textContent);
        } else {
            console.error('Team size update failed:', {
                teamSize: !!teamSize,
                team_size_data: data.team_size
            });
        }

        // Update confidence level
        const confidenceLevel = document.getElementById('confidenceLevel');
        if (confidenceLevel && data.confidence_level) {
            confidenceLevel.textContent = data.confidence_level;
            confidenceLevel.className = `badge bg-${getConfidenceBadgeColor(data.confidence_level)}`;
            console.log('Confidence level updated to:', confidenceLevel.textContent);
        } else {
            console.error('Confidence level update failed:', {
                confidenceLevel: !!confidenceLevel,
                confidence_level_data: data.confidence_level
            });
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
    }, 100);
}
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
            const locAvg = ((estimates.loc_linear?.effort || 0) + (estimates.loc_random_forest?.effort || 0)) / 2;
            locValue.textContent = locAvg.toFixed(2);
        }
    }

    // Update project details
    if (data.project_size) {
        const projectSize = document.getElementById('projectSize');
        if (projectSize) {
            projectSize.textContent = data.project_size.toFixed(1) + ' KLOC';
        }
    }

    // Create detailed breakdown
    const detailedResults = document.getElementById('detailedResults');
    if (detailedResults && data.model_estimates) {
        let detailHtml = '<h6>Detailed Model Breakdown:</h6><div class="row">';
        
        Object.keys(data.model_estimates).forEach(model => {
            const modelData = data.model_estimates[model];
            if (modelData && modelData.effort !== null && modelData.effort !== undefined) {
                detailHtml += `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card border-start border-primary border-3">
                            <div class="card-body">
                                <h6 class="card-title">${modelData.name}</h6>
                                <h4 class="text-primary">${modelData.effort.toFixed(2)} PM</h4>
                                <small class="text-muted">Confidence: ${modelData.confidence}%</small>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        
        detailHtml += '</div>';
        detailedResults.innerHTML = detailHtml;
    }

    // Create chart if canvas exists
    const chartCanvas = document.getElementById('estimationChart');
    if (chartCanvas && data.model_estimates) {
        createEstimationChart(data.model_estimates);
    }
}

function createEstimationChart(modelEstimates) {
    const chartContainer = document.getElementById('chartContainer');
    if (!chartContainer) return;

    chartContainer.innerHTML = '<canvas id="estimationChart" width="400" height="200"></canvas>';
    
    const ctx = document.getElementById('estimationChart').getContext('2d');
    
    const labels = [];
    const values = [];
    
    Object.keys(modelEstimates).forEach(model => {
        const modelData = modelEstimates[model];
        if (modelData && modelData.effort !== null && modelData.effort !== undefined) {
            labels.push(modelData.name || formatModelName(model));
            values.push(modelData.effort);
        }
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Effort (person-months)',
                data: values,
                backgroundColor: [
                    '#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1', '#20c997', 
                    '#fd7e14', '#e83e8c', '#6c757d', '#17a2b8'
                ],
                borderColor: [
                    '#0056b3', '#1e7e34', '#d39e00', '#bd2130', '#59359a', '#1a9f86',
                    '#e8590c', '#d91a72', '#545b62', '#138496'
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
