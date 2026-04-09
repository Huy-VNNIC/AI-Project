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

function renderSummary(summary) {
  document.getElementById("sumCount").textContent = summary.task_count || 0;
  document.getElementById("sumAvg").textContent = `${summary.average_score || 0}/6`;
  document.getElementById("sumLevel").textContent = summary.overall_label || "No data";

  dimensionSummary.innerHTML = dimensions.map(([key, name]) => {
    const info = summary.criteria_pass_rates?.[key] || { passed: 0, total: 0, percent: 0 };
    const cls = quality(info.passed, info.total || 1)[1];
    return `<div class="dimension-box"><div class="d-flex justify-content-between align-items-center mb-2"><h6 class="mb-0">${name}</h6><span class="pill ${cls}">${info.percent}%</span></div><p class="mb-0 text-muted">${info.passed}/${info.total} tasks passed.</p></div>`;
  }).join("");

  emptyState.style.display = "none";
  summaryState.style.display = "block";
}

function renderCards(results) {
  resultsList.innerHTML = results.map((result, index) => {
    const [text, cls] = quality(result.score || 0, dimensions.length);
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
    const refined = result.refined
      ? `<div class="mt-3"><div class="text-muted small mb-2">Refined story</div><div class="task-text">${result.refined}</div></div>`
      : "";
    const acceptanceCriteria = result.acceptance_criteria && result.acceptance_criteria.length
      ? `<div class="mt-4"><h6 class="fw-bold mb-3">Acceptance Criteria</h6><ul class="mb-0 ps-3">${result.acceptance_criteria.map((item) => `<li>${item}</li>`).join("")}</ul></div>`
      : "";

    return `<div class="card task-card"><div class="card-body p-4"><div class="d-flex justify-content-between align-items-start gap-3 flex-wrap"><div><div class="text-muted small mb-1">Task ${index + 1}</div><h5 class="mb-2">${cardTitle}</h5><div class="mb-2">INVEST score: ${result.score || 0}/6</div><span class="pill ${cls}">${text}</span></div></div><div class="mt-3"><div class="text-muted small mb-2">Original input</div><div class="task-text">${result.original || ""}</div></div>${sourceTask}${converted}${refined}${acceptanceCriteria}<div class="mt-4"><h6 class="fw-bold mb-3">Criterion breakdown</h6><div class="dimension-grid">${checks}</div></div><div class="mt-4"><h6 class="fw-bold mb-3">Improvement notes</h6>${suggestions}</div></div></div>`;
  }).join("");
}

async function analyze() {
  const splitMode = document.getElementById("splitMode").value;
  const minLength = Number(document.getElementById("minLength").value || 15);
  const tasks = splitTasks(input.value, splitMode, minLength);

  if (!tasks.length) {
    resultsList.innerHTML = "";
    summaryState.style.display = "none";
    emptyState.style.display = "block";
    return;
  }

  setLoading(true);

  try {
    const response = await fetch("/api/task-invest/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: input.value,
        split_mode: splitMode,
        min_length: minLength,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    renderSummary(data.summary || {});
    renderCards(data.results || []);
  } catch (error) {
    console.error(error);
    resultsList.innerHTML = '<div class="alert alert-danger">Unable to analyze INVEST right now. Please try again.</div>';
    summaryState.style.display = "none";
    emptyState.style.display = "block";
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  analyze();
});

document.getElementById("sampleBtn").addEventListener("click", () => {
  input.value = sampleText;
  analyze();
});

document.getElementById("clearBtn").addEventListener("click", () => {
  input.value = "";
  resultsList.innerHTML = "";
  summaryState.style.display = "none";
  emptyState.style.display = "block";
});

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
