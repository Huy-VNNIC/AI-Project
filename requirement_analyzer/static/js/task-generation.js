// Task Generation UI Logic
let generatedTasks = [];
let currentFilter = 'all';
let currentTaskForModal = null;

// Example datasets
const examples = {
    ecommerce: `The system shall allow users to browse products by category.
The application must support user registration with email verification.
Users should be able to add products to a shopping cart.
The system shall calculate total price including taxes and shipping.
The platform must integrate with payment gateways for secure checkout.
Users should be able to track their order status in real-time.
The system shall send confirmation emails for orders.
The application must support product reviews and ratings.`,

    auth: `The system shall implement user authentication with email and password.
The application must support OAuth2 login with Google and Facebook.
Users should be able to reset their password via email link.
The system shall enforce strong password requirements.
The platform must implement two-factor authentication.
Sessions should expire after 30 minutes of inactivity.
The system shall log all authentication attempts for security audit.
The application must support role-based access control.`,

    healthcare: `The system shall maintain secure patient medical records.
The application must comply with HIPAA privacy regulations.
Healthcare providers should be able to schedule patient appointments.
The system shall send appointment reminders via SMS and email.
The platform must support telemedicine video consultations.
Patients should be able to view their lab results online.
The system shall integrate with pharmacy systems for prescription management.
The application must encrypt all patient data at rest and in transit.`
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    checkGeneratorMode();
});

function setupEventListeners() {
    // Form submission
    const form = document.getElementById('taskGenerationForm');
    if (form) {
        form.addEventListener('submit', handleTaskGeneration);
    }

    // Filter buttons
    const filterButtons = document.querySelectorAll('input[name="filterType"]');
    filterButtons.forEach(button => {
        button.addEventListener('change', handleFilterChange);
    });

    // File upload
    const uploadBtn = document.getElementById('uploadGenerateBtn');
    if (uploadBtn) {
        uploadBtn.addEventListener('click', handleFileUpload);
    }
}

async function checkGeneratorMode() {
    try {
        const response = await fetch('/api/task-generation/status');
        const data = await response.json();
        
        // Update mode badge
        const badge = document.querySelector('.navbar .badge');
        if (badge && data.mode) {
            badge.textContent = data.mode.charAt(0).toUpperCase() + data.mode.slice(1) + ' Mode';
            badge.className = 'badge ms-2 mt-2 ' + (data.mode === 'model' ? 'bg-success' : 'bg-warning');
        }
    } catch (error) {
        console.warn('Could not check generator mode:', error);
    }
}

async function handleTaskGeneration(event) {
    event.preventDefault();
    
    const requirementsText = document.getElementById('requirementsText').value.trim();
    
    if (!requirementsText) {
        showToast('Please enter requirements text', 'error');
        return;
    }

    const maxTasks = parseInt(document.getElementById('maxTasks').value) || 50;
    const threshold = parseFloat(document.getElementById('threshold').value) || 0.5;

    // Show loading state
    showLoading(true);

    try {
        const startTime = performance.now();

        const response = await fetch('/api/task-generation/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: requirementsText,
                max_tasks: maxTasks,
                requirement_threshold: threshold
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }

        const data = await response.json();
        const endTime = performance.now();
        const processingTime = ((endTime - startTime) / 1000).toFixed(2);

        // Store and display results
        generatedTasks = data.tasks || [];
        displayResults(generatedTasks, processingTime, data);

        showToast(`Successfully generated ${generatedTasks.length} tasks!`, 'success');

    } catch (error) {
        console.error('Generation error:', error);
        showToast('Error: ' + error.message, 'error');
        showLoading(false);
    }
}

async function handleFileUpload() {
    const fileInput = document.getElementById('fileUpload');
    const file = fileInput.files[0];

    if (!file) {
        showToast('Please select a file', 'error');
        return;
    }

    // Show loading
    showLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('max_tasks', document.getElementById('maxTasks')?.value || '50');

    try {
        const startTime = performance.now();

        const response = await fetch('/api/task-generation/generate-from-file', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'File processing failed');
        }

        const data = await response.json();
        const endTime = performance.now();
        const processingTime = ((endTime - startTime) / 1000).toFixed(2);

        generatedTasks = data.tasks || [];
        displayResults(generatedTasks, processingTime, data);

        showToast(`Successfully processed ${file.name}!`, 'success');

    } catch (error) {
        console.error('Upload error:', error);
        showToast('Error: ' + error.message, 'error');
        showLoading(false);
    }
}

function displayResults(tasks, processingTime, metadata) {
    showLoading(false);

    if (tasks.length === 0) {
        document.getElementById('emptyState').style.display = 'block';
        document.getElementById('resultsContainer').style.display = 'none';
        return;
    }

    // Hide empty state, show results
    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'block';

    // Update summary
    document.getElementById('taskCount').textContent = tasks.length;
    document.getElementById('processingTime').textContent = processingTime;

    // Update stats card
    const statsCard = document.getElementById('statsCard');
    if (statsCard) {
        statsCard.style.display = 'block';
        // Use total_tasks from new response format, fallback to tasks.length
        document.getElementById('statTotal').textContent = metadata.total_tasks || tasks.length;
        document.getElementById('statGenerated').textContent = tasks.length;
        // Calculate filtered: if we have stats with type distribution, sum it up
        const typeCount = metadata.stats && metadata.stats.type_distribution ? 
            Object.values(metadata.stats.type_distribution).reduce((a, b) => a + b, 0) : 0;
        document.getElementById('statFiltered').textContent = typeCount > 0 ? (typeCount - tasks.length) : 0;
    }

    // Render tasks
    renderTasks(tasks);
}

function renderTasks(tasks) {
    const container = document.getElementById('tasksList');
    container.innerHTML = '';

    // Apply filter
    const filteredTasks = currentFilter === 'all' 
        ? tasks 
        : tasks.filter(task => task.type === currentFilter);

    if (filteredTasks.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="bi bi-funnel display-4 text-muted"></i>
                <p class="mt-3 text-muted">No tasks match the current filter</p>
            </div>
        `;
        return;
    }

    filteredTasks.forEach((task, index) => {
        const card = createTaskCard(task, index);
        container.appendChild(card);
    });

    // Add fade-in animation
    setTimeout(() => {
        container.querySelectorAll('.task-card').forEach((card, i) => {
            setTimeout(() => {
                card.classList.add('fade-in');
            }, i * 50);
        });
    }, 10);
}

function createTaskCard(task, index) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.setAttribute('data-task-index', index);

    const priorityClass = `badge-priority-${task.priority.toLowerCase()}`;
    
    card.innerHTML = `
        <div class="task-card-header" onclick="toggleTaskCard(${index})">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="task-title">${escapeHtml(task.title)}</h6>
                    <div class="task-meta">
                        <span class="task-badge badge-type">
                            <i class="bi bi-tag"></i> ${task.type}
                        </span>
                        <span class="task-badge ${priorityClass}">
                            <i class="bi bi-exclamation-circle"></i> ${task.priority}
                        </span>
                        <span class="task-badge badge-domain">
                            <i class="bi bi-building"></i> ${task.domain}
                        </span>
                        <span class="task-badge badge-points">
                            <i class="bi bi-graph-up"></i> ${task.story_points} SP
                        </span>
                    </div>
                </div>
                <i class="bi bi-chevron-down expand-icon"></i>
            </div>
        </div>
        <div class="task-card-body">
            <div class="user-story">
                <strong>As a</strong> ${escapeHtml(task.role)}, 
                <strong>I want to</strong> ${escapeHtml(task.title.toLowerCase())}, 
                <strong>so that</strong> I can ${generateSoThat(task.description)}
            </div>
            
            <div class="task-description">
                ${escapeHtml(task.description)}
            </div>

            ${task.acceptance_criteria && task.acceptance_criteria.length > 0 ? `
                <div class="acceptance-criteria">
                    <h6><i class="bi bi-check2-square"></i> Acceptance Criteria</h6>
                    <ul class="ac-list">
                        ${task.acceptance_criteria.map(ac => `
                            <li class="ac-item">
                                <i class="bi bi-check-circle-fill"></i>
                                <span class="ac-item-text">${escapeHtml(ac)}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}

            <div class="task-actions">
                <button class="btn btn-sm btn-outline-primary" onclick="viewTaskDetail(${index})">
                    <i class="bi bi-eye"></i> View Details
                </button>
                <button class="btn btn-sm btn-outline-success" onclick="copyTask(${index})">
                    <i class="bi bi-clipboard"></i> Copy
                </button>
                <button class="btn btn-sm btn-outline-info" onclick="exportSingleTask(${index})">
                    <i class="bi bi-download"></i> Export
                </button>
            </div>
        </div>
    `;

    return card;
}

function toggleTaskCard(index) {
    const card = document.querySelector(`.task-card[data-task-index="${index}"]`);
    if (card) {
        card.classList.toggle('expanded');
    }
}

function viewTaskDetail(index) {
    const task = generatedTasks[index];
    currentTaskForModal = task;

    document.getElementById('modalTaskTitle').textContent = task.title;
    document.getElementById('modalTaskBody').innerHTML = `
        <div class="row mb-3">
            <div class="col-md-6">
                <strong>Type:</strong> ${task.type}
            </div>
            <div class="col-md-6">
                <strong>Priority:</strong> ${task.priority}
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-md-6">
                <strong>Domain:</strong> ${task.domain}
            </div>
            <div class="col-md-6">
                <strong>Story Points:</strong> ${task.story_points}
            </div>
        </div>
        <div class="row mb-3">
            <div class="col-12">
                <strong>Role:</strong> ${task.role}
            </div>
        </div>
        <div class="mb-3">
            <strong>Description:</strong>
            <p>${escapeHtml(task.description)}</p>
        </div>
        ${task.acceptance_criteria && task.acceptance_criteria.length > 0 ? `
            <div>
                <strong>Acceptance Criteria:</strong>
                <ol>
                    ${task.acceptance_criteria.map(ac => `<li>${escapeHtml(ac)}</li>`).join('')}
                </ol>
            </div>
        ` : ''}
    `;

    const modal = new bootstrap.Modal(document.getElementById('taskDetailModal'));
    modal.show();
}

function copyTask(index) {
    const task = generatedTasks[index];
    const text = formatTaskAsText(task);
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('Task copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Copy failed:', err);
        showToast('Failed to copy task', 'error');
    });
}

function copyTaskToClipboard() {
    if (currentTaskForModal) {
        const text = formatTaskAsText(currentTaskForModal);
        navigator.clipboard.writeText(text).then(() => {
            showToast('Task copied to clipboard!', 'success');
        });
    }
}

function formatTaskAsText(task) {
    let text = `Title: ${task.title}\n`;
    text += `Type: ${task.type}\n`;
    text += `Priority: ${task.priority}\n`;
    text += `Domain: ${task.domain}\n`;
    text += `Story Points: ${task.story_points}\n`;
    text += `Role: ${task.role}\n\n`;
    text += `Description:\n${task.description}\n\n`;
    
    if (task.acceptance_criteria && task.acceptance_criteria.length > 0) {
        text += `Acceptance Criteria:\n`;
        task.acceptance_criteria.forEach((ac, i) => {
            text += `${i + 1}. ${ac}\n`;
        });
    }
    
    return text;
}

function exportTasks(format) {
    if (generatedTasks.length === 0) {
        showToast('No tasks to export', 'error');
        return;
    }

    if (format === 'json') {
        const blob = new Blob([JSON.stringify(generatedTasks, null, 2)], { type: 'application/json' });
        downloadFile(blob, 'tasks.json');
    } else if (format === 'csv') {
        const csv = convertToCSV(generatedTasks);
        const blob = new Blob([csv], { type: 'text/csv' });
        downloadFile(blob, 'tasks.csv');
    }

    showToast(`Exported ${generatedTasks.length} tasks as ${format.toUpperCase()}`, 'success');
}

function exportSingleTask(index) {
    const task = generatedTasks[index];
    const json = JSON.stringify(task, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    downloadFile(blob, `task_${index + 1}.json`);
    showToast('Task exported successfully', 'success');
}

function convertToCSV(tasks) {
    const headers = ['Title', 'Type', 'Priority', 'Domain', 'Story Points', 'Role', 'Description', 'Acceptance Criteria'];
    const rows = tasks.map(task => [
        task.title,
        task.type,
        task.priority,
        task.domain,
        task.story_points,
        task.role,
        task.description,
        (task.acceptance_criteria || []).join(' | ')
    ]);

    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    return csvContent;
}

function downloadFile(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function handleFilterChange(event) {
    currentFilter = event.target.value;
    renderTasks(generatedTasks);
}

function loadExample(type) {
    const text = examples[type];
    if (text) {
        document.getElementById('requirementsText').value = text;
        // Switch to text input tab
        document.getElementById('text-input-tab').click();
        showToast(`Loaded ${type} example`, 'success');
    }
}

function showLoading(show) {
    document.getElementById('loadingState').style.display = show ? 'block' : 'none';
    document.getElementById('emptyState').style.display = !show && generatedTasks.length === 0 ? 'block' : 'none';
    document.getElementById('resultsContainer').style.display = !show && generatedTasks.length > 0 ? 'block' : 'none';
    
    // Disable/enable generate button
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.disabled = show;
        generateBtn.innerHTML = show 
            ? '<span class="spinner-border spinner-border-sm me-2"></span>Generating...' 
            : '<i class="bi bi-magic"></i> Generate Tasks';
    }
}

function showToast(message, type = 'success') {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex align-items-center p-3">
            <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            <div class="me-auto">${message}</div>
            <button type="button" class="btn-close btn-close-white ms-2" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;

    container.appendChild(toast);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function generateSoThat(description) {
    // Extract a benefit from description
    const match = description.match(/to (.+?)(?:\.|$)/i);
    if (match) {
        return match[1];
    }
    return 'achieve the business goal';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
