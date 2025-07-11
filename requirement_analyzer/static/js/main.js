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
    let modelsChart = null;

    // Helper: Show results
    function showResults(data) {
        resultsCard.classList.remove('d-none');
        // Summary
        totalEffort.textContent = data.estimation?.total_effort ? data.estimation.total_effort + ' person-months' : '-';
        duration.textContent = data.estimation?.duration ? data.estimation.duration + ' months' : '-';
        teamSize.textContent = data.estimation?.team_size ? data.estimation.team_size : '-';
        confidenceLevel.textContent = data.estimation?.confidence_level ? data.estimation.confidence_level : '-';
        // Model details
        let modelHtml = '';
        if (data.estimation?.model_estimates) {
            for (const [model, est] of Object.entries(data.estimation.model_estimates)) {
                modelHtml += `<span class="badge bg-info model-badge">${model}: ${est} PM</span>`;
            }
        }
        modelDetailsContent.innerHTML = modelHtml || '<em>No model details available.</em>';
        // Analysis details
        analysisDetailsContent.innerHTML = `<pre class="json">${JSON.stringify(data.analysis, null, 2)}</pre>`;
        // Chart
        if (modelsChart) modelsChart.destroy();
        if (data.estimation?.model_estimates) {
            const ctx = document.getElementById('modelsChart').getContext('2d');
            modelsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.estimation.model_estimates),
                    datasets: [{
                        label: 'Effort (person-months)',
                        data: Object.values(data.estimation.model_estimates),
                        backgroundColor: '#0d6efd',
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } }
                }
            });
        }
    }

    // Helper: Show loading spinner
    function showLoading() {
        resultsCard.classList.remove('d-none');
        totalEffort.textContent = duration.textContent = teamSize.textContent = confidenceLevel.textContent = '-';
        modelDetailsContent.innerHTML = '<div class="spinner-container"><div class="spinner-border text-primary" role="status"></div></div>';
        analysisDetailsContent.innerHTML = '';
        if (modelsChart) modelsChart.destroy();
    }

    // Helper: Hide results
    function hideResults() {
        resultsCard.classList.add('d-none');
    }

    // Text Input Form Submit
    textForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const text = requirementsText.value.trim();
        const method = methodSelect.value;
        if (!text) return alert('Please enter requirements text.');
        showLoading();
        fetch('/estimate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, method })
        })
        .then(res => res.json())
        .then(showResults)
        .catch(() => alert('Estimation failed.'));
    });

    // Upload Form Submit
    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const file = requirementsFile.files[0];
        const method = uploadMethodSelect.value;
        if (!file) return alert('Please select a file.');
        showLoading();
        const formData = new FormData();
        formData.append('file', file);
        formData.append('method', method);
        fetch('/upload-requirements', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(showResults)
        .catch(() => alert('Estimation failed.'));
    });

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
        const clone = template.content.cloneNode(true);
        clone.querySelector('.delete-task-btn').addEventListener('click', function () {
            this.closest('.task-item').remove();
        });
        taskList.appendChild(clone);
    }
    addTaskBtn.addEventListener('click', addTask);
    estimateTasksBtn.addEventListener('click', function () {
        const tasks = getTasks();
        const method = tasksMethodSelect.value;
        if (!tasks.length) return alert('Please add at least one task.');
        showLoading();
        fetch('/estimate-from-tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tasks, method })
        })
        .then(res => res.json())
        .then(showResults)
        .catch(() => alert('Estimation failed.'));
    });

    // Jira/Trello Integration (modal logic only, actual API integration requires backend support)
    document.getElementById('jiraImportBtn').addEventListener('click', function () {
        // For demo: just close modal and show alert
        const modal = bootstrap.Modal.getInstance(document.getElementById('jiraModal'));
        modal.hide();
        alert('Jira integration is not fully implemented in this demo.');
    });
    document.getElementById('trelloImportBtn').addEventListener('click', function () {
        // For demo: just close modal and show alert
        const modal = bootstrap.Modal.getInstance(document.getElementById('trelloModal'));
        modal.hide();
        alert('Trello integration is not fully implemented in this demo.');
    });

    // Hide results on tab change
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(btn => {
        btn.addEventListener('click', hideResults);
    });
});
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
    let modelsChart = null;

    // Helper: Show results
    function showResults(data) {
        resultsCard.classList.remove('d-none');
        // Summary
        totalEffort.textContent = data.estimation?.total_effort ? data.estimation.total_effort + ' person-months' : '-';
        duration.textContent = data.estimation?.duration ? data.estimation.duration + ' months' : '-';
        teamSize.textContent = data.estimation?.team_size ? data.estimation.team_size : '-';
        confidenceLevel.textContent = data.estimation?.confidence_level ? data.estimation.confidence_level : '-';
        // Model details
        let modelHtml = '';
        if (data.estimation?.model_estimates) {
            for (const [model, est] of Object.entries(data.estimation.model_estimates)) {
                modelHtml += `<span class="badge bg-info model-badge">${model}: ${est} PM</span>`;
            }
        }
        modelDetailsContent.innerHTML = modelHtml || '<em>No model details available.</em>';
        // Analysis details
        analysisDetailsContent.innerHTML = `<pre class="json">${JSON.stringify(data.analysis, null, 2)}</pre>`;
        // Chart
        if (modelsChart) modelsChart.destroy();
        if (data.estimation?.model_estimates) {
            const ctx = document.getElementById('modelsChart').getContext('2d');
            modelsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data.estimation.model_estimates),
                    datasets: [{
                        label: 'Effort (person-months)',
                        data: Object.values(data.estimation.model_estimates),
                        backgroundColor: '#0d6efd',
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } }
                }
            });
        }
    }

    // Helper: Show loading spinner
    function showLoading() {
        resultsCard.classList.remove('d-none');
        totalEffort.textContent = duration.textContent = teamSize.textContent = confidenceLevel.textContent = '-';
        modelDetailsContent.innerHTML = '<div class="spinner-container"><div class="spinner-border text-primary" role="status"></div></div>';
        analysisDetailsContent.innerHTML = '';
        if (modelsChart) modelsChart.destroy();
    }

    // Helper: Hide results
    function hideResults() {
        resultsCard.classList.add('d-none');
    }

    // Text Input Form Submit
    textForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const text = requirementsText.value.trim();
        const method = methodSelect.value;
        if (!text) return alert('Please enter requirements text.');
        showLoading();
        fetch('/estimate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, method })
        })
        .then(res => res.json())
        .then(showResults)
        .catch(() => alert('Estimation failed.'));
    });

    // Upload Form Submit
    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const file = requirementsFile.files[0];
        const method = uploadMethodSelect.value;
        if (!file) return alert('Please select a file.');
        showLoading();
        const formData = new FormData();
        formData.append('file', file);
        formData.append('method', method);
        fetch('/upload-requirements', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(showResults)
        .catch(() => alert('Estimation failed.'));
    });

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
        const clone = template.content.cloneNode(true);
        clone.querySelector('.delete-task-btn').addEventListener('click', function () {
            this.closest('.task-item').remove();
        });
        taskList.appendChild(clone);
    }
    addTaskBtn.addEventListener('click', addTask);
    estimateTasksBtn.addEventListener('click', function () {
        const tasks = getTasks();
        const method = tasksMethodSelect.value;
        if (!tasks.length) return alert('Please add at least one task.');
        showLoading();
        fetch('/estimate-from-tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tasks, method })
        })
        .then(res => res.json())
        .then(showResults)
        .catch(() => alert('Estimation failed.'));
    });

    // Jira/Trello Integration (modal logic only, actual API integration requires backend support)
    document.getElementById('jiraImportBtn').addEventListener('click', function () {
        // For demo: just close modal and show alert
        const modal = bootstrap.Modal.getInstance(document.getElementById('jiraModal'));
        modal.hide();
        alert('Jira integration is not fully implemented in this demo.');
    });
    document.getElementById('trelloImportBtn').addEventListener('click', function () {
        // For demo: just close modal and show alert
        const modal = bootstrap.Modal.getInstance(document.getElementById('trelloModal'));
        modal.hide();
        alert('Trello integration is not fully implemented in this demo.');
    });

    // Hide results on tab change
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(btn => {
        btn.addEventListener('click', hideResults);
    });
});
