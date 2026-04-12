const dimensions = [
  ["independent", "Independent"],
  ["negotiable", "Negotiable"],
  ["valuable", "Valuable"],
  ["estimable", "Estimable"],
  ["small", "Small"],
  ["testable", "Testable"],
];

const input = document.getElementById("taskInput");
const form = document.getElementById("investForm");
const fileInput = document.getElementById("taskFile");
const selectedFileInfo = document.getElementById("selectedFileInfo");
const textInputTab = document.getElementById("text-input-tab");
const fileInputTab = document.getElementById("file-input-tab");
const inputMode = document.getElementById("inputMode");
const emptyState = document.getElementById("emptyState");
const summaryState = document.getElementById("summaryState");
const resultsList = document.getElementById("resultsList");
const dimensionSummary = document.getElementById("dimensionSummary");

const sampleText = [
  "As a customer, I want to save multiple shipping addresses so that I can checkout faster.",
  "As an admin, I want to export monthly revenue reports to CSV so that I can review business performance.",
  "As a patient, I want to receive appointment reminders by email so that I do not miss my visit.",
  "Build login, forgot password, social login, audit log, and admin dashboard in one screen.",
].join("\n");

function setLoading(isLoading) {
  const submitButton = form.querySelector('button[type="submit"]');
  if (!submitButton) return;
  submitButton.disabled = isLoading;
  submitButton.innerHTML = isLoading
    ? '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Analyzing...'
    : '<i class="bi bi-search"></i> Analyze INVEST';
}

function quality(score, total) {
  const ratio = score / total;
  if (ratio >= 0.8) return ["Strong INVEST", "good"];
  if (ratio >= 0.5) return ["Needs Refinement", "mid"];
  return ["Weak INVEST", "bad"];
}

function splitTasks(text, mode, minLength) {
  const chunks = mode === "paragraph" ? text.split(/\n\s*\n+/) : text.split("\n");
  return chunks.map((v) => v.trim()).filter((v) => v.length >= minLength);
}

function isFileMode() {
  return fileInputTab && fileInputTab.classList.contains("active");
}

function updateSelectedFileInfo() {
  if (!fileInput || !selectedFileInfo) return;
  const file = fileInput.files && fileInput.files[0];
  if (!file) {
    selectedFileInfo.style.display = "none";
    selectedFileInfo.textContent = "";
    return;
  }

  selectedFileInfo.style.display = "block";
  selectedFileInfo.textContent = `Selected file: ${file.name} (${Math.ceil(file.size / 1024)} KB)`;
}

function activateTab(tabName) {
  if (tabName === "file" && fileInputTab && bootstrap?.Tab) {
    bootstrap.Tab.getOrCreateInstance(fileInputTab).show();
  } else if (textInputTab && bootstrap?.Tab) {
    bootstrap.Tab.getOrCreateInstance(textInputTab).show();
  }
  if (inputMode) {
    inputMode.value = tabName === "file" ? "file" : "text";
  }
}

function renderSummary(summary) {
  document.getElementById("sumCount").textContent = summary.task_count || 0;
  document.getElementById("sumAvg").textContent = `${summary.average_score || 0}/${summary.score_scale || 6}`;
  document.getElementById("sumLevel").textContent = summary.overall_label || "No data";

  dimensionSummary.innerHTML = dimensions.map(([key, name]) => {
    const info = summary.criteria_pass_rates?.[key] || { passed: 0, total: 0, percent: 0 };
    const cls = quality(info.passed, info.total || 1)[1];
    return `<div class="dimension-box"><div class="d-flex justify-content-between align-items-center mb-2"><h6 class="mb-0">${name}</h6><span class="pill ${cls}">${info.percent}%</span></div><p class="mb-0 text-muted">${info.passed}/${info.total} tasks passed.</p></div>`;
  }).join("");

  emptyState.style.display = "none";
  summaryState.style.display = "block";
}

function renderError(message) {
  resultsList.innerHTML = `<div class="alert alert-danger">${message || "Unable to analyze INVEST right now. Please try again."}</div>`;
  summaryState.style.display = "none";
  emptyState.style.display = "block";
}

function renderCards(results) {
  resultsList.innerHTML = results.map((result, index) => {
    const [fallbackText, fallbackCls] = quality(result.score || 0, dimensions.length);
    let text = fallbackText;
    let cls = fallbackCls;
    if (result.refinement_status === "kept" && result.meets_invest) {
      text = "Already INVEST-ready";
      cls = "good";
    } else if (result.meets_invest) {
      text = "Refined and INVEST-ready";
      cls = "good";
    } else if (result.recommended_action === "refine") {
      text = "Refined, review again";
      cls = "mid";
    }
    const cardTitle = result.title || `Task ${index + 1}`;
    const checks = dimensions.map(([key, name]) => {
      const item = result.criteria?.[key] || { pass: false, reason: "No analysis available." };
      return `<div class="dimension-box"><div class="d-flex justify-content-between align-items-center mb-2"><h6 class="mb-0">${name}</h6><span class="pill ${item.pass ? "good" : "bad"}">${item.pass ? "Pass" : "Review"}</span></div><p>${item.reason}</p></div>`;
    }).join("");

    const suggestions = result.issues && result.issues.length
      ? `<ul class="mb-0 ps-3">${result.issues.map((v) => `<li>${v}</li>`).join("")}</ul>`
      : `<p class="mb-0 text-success">This task already looks strong against INVEST.</p>`;

    const converted = result.generated_from_task
      ? `<div class="mt-3"><div class="text-muted small mb-2">Generated user story</div><div class="task-text">${result.generated_from_task}</div></div>`
      : "";
    const sourceTask = result.source_task
      ? `<div class="mt-3"><div class="text-muted small mb-2">Source composite task</div><div class="task-text">${result.source_task}</div></div>`
      : "";
    const refined = (result.refined_title || result.refined || (result.acceptance_criteria && result.acceptance_criteria.length))
      ? `<div class="mt-3"><div class="text-muted small mb-2">Refined task</div><div class="task-text"><strong>Title:</strong> ${result.refined_title || cardTitle}</div><div class="task-text mt-2"><strong>Description:</strong> ${result.refined_description || result.refined || ""}</div></div>`
      : "";
    const acceptanceCriteria = result.acceptance_criteria && result.acceptance_criteria.length
      ? `<div class="mt-4"><h6 class="fw-bold mb-3">Acceptance Criteria</h6><ul class="mb-0 ps-3">${result.acceptance_criteria.map((item) => `<li>${item}</li>`).join("")}</ul></div>`
      : "";
    const investMeta = result.invest_total
      ? `<div class="text-muted small mt-2">Detailed INVEST total: ${result.invest_total}/30${result.invest_grade ? ` • ${result.invest_grade}` : ""}</div>`
      : "";
    let refinedMeta = "";
    if (result.refinement_status === "kept" && result.meets_invest) {
      refinedMeta = '<div class="text-success small mt-2">This task already met the INVEST threshold, so no refinement was required.</div>';
    } else if (result.meets_invest) {
      refinedMeta = '<div class="text-success small mt-2">This refined task now meets the INVEST threshold.</div>';
    } else {
      refinedMeta = '<div class="text-warning small mt-2">This task was refined, but it still needs improvement to fully meet INVEST.</div>';
    }

    return `<div class="card task-card"><div class="card-body p-4"><div class="d-flex justify-content-between align-items-start gap-3 flex-wrap"><div><div class="text-muted small mb-1">Task ${index + 1}</div><h5 class="mb-2">${cardTitle}</h5><div class="mb-2">INVEST score: ${result.score || 0}/6</div><span class="pill ${cls}">${text}</span>${investMeta}${refinedMeta}</div></div><div class="mt-3"><div class="text-muted small mb-2">Original input</div><div class="task-text">${result.original || ""}</div></div>${sourceTask}${converted}${refined}${acceptanceCriteria}<div class="mt-4"><h6 class="fw-bold mb-3">Criterion breakdown</h6><div class="dimension-grid">${checks}</div></div><div class="mt-4"><h6 class="fw-bold mb-3">Improvement notes</h6>${suggestions}</div></div></div>`;
  }).join("");
}

function prepareSubmit() {
  if (fileInput && fileInput.files && fileInput.files.length) {
    activateTab("file");
  } else {
    activateTab(isFileMode() ? "file" : "text");
  }
  setLoading(true);
}

async function submitAnalyzeForm(event) {
  event.preventDefault();

  // Xác định mode dựa trên file có được chọn không
  const hasFile = fileInput && fileInput.files && fileInput.files.length > 0;
  
  // Set inputMode trước khi tạo FormData
  if (hasFile) {
    inputMode.value = "file";
  } else {
    inputMode.value = isFileMode() ? "file" : "text";
  }

  setLoading(true);

  try {
    const formData = new FormData(form);
    
    // Debug: log formData entries
    console.log("input_mode:", formData.get("input_mode"));
    console.log("file:", formData.get("file"));
    console.log("text length:", (formData.get("text") || "").length);

    const response = await fetch("/api/task-invest/analyze-form", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    if (data.active_tab) {
      activateTab(data.active_tab);
    }

    renderSummary(data.summary || {});
    if (!data.results || !data.results.length) {
      const refinement = data.refinement || {};
      resultsList.innerHTML = `<div class="alert alert-warning">No tasks available to display.${
        refinement.after
          ? ` After refinement: ${refinement.after.meeting_invest || 0} tasks meet INVEST, ${refinement.after.not_meeting_invest || 0} tasks still need work.`
          : ""
      }</div>`;
    } else {
      renderCards(data.results || []);
    }
  } catch (error) {
    console.error(error);
    renderError(error.message);
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", submitAnalyzeForm);

document.getElementById("sampleBtn").addEventListener("click", () => {
  input.value = sampleText;
  activateTab("text");
});

document.getElementById("clearBtn").addEventListener("click", () => {
  input.value = "";
  if (fileInput) {
    fileInput.value = "";
  }
  updateSelectedFileInfo();
  resultsList.innerHTML = "";
  summaryState.style.display = "none";
  emptyState.style.display = "block";
});

if (fileInput) {
  fileInput.addEventListener("change", updateSelectedFileInfo);
}

if (textInputTab) {
  textInputTab.addEventListener("shown.bs.tab", () => {
    if (inputMode) inputMode.value = "text";
    updateSelectedFileInfo();
  });
}

if (fileInputTab) {
  fileInputTab.addEventListener("shown.bs.tab", () => {
    if (inputMode) inputMode.value = "file";
    updateSelectedFileInfo();
  });
}

const initialData = window.initialInvestData;
if (window.initialActiveTab) {
  activateTab(window.initialActiveTab);
}
if (initialData && initialData.status === "error") {
  renderError(initialData.detail);
  setLoading(false);
} else if (initialData && initialData.summary) {
  renderSummary(initialData.summary || {});
  if (!initialData.results || !initialData.results.length) {
    const refinement = initialData.refinement || {};
    resultsList.innerHTML = `<div class="alert alert-warning">No refined tasks available to display.${refinement.after ? ` After refinement: ${refinement.after.meeting_invest || 0} tasks meet INVEST, ${refinement.after.not_meeting_invest || 0} tasks still need work.` : ""}</div>`;
  } else {
    renderCards(initialData.results || []);
  }
  setLoading(false);
}

document.getElementById("copyBtn").addEventListener("click", async function () {
  const text = [...resultsList.querySelectorAll(".task-card")]
    .map((card) => card.innerText.trim())
    .join("\n\n");

  if (!text) return;

  try {
    await navigator.clipboard.writeText(text);
    this.innerHTML = '<i class="bi bi-check2"></i> Copied';
    setTimeout(() => {
      this.innerHTML = '<i class="bi bi-clipboard"></i> Copy Summary';
    }, 1500);
  } catch (error) {
    console.error(error);
  }
});
