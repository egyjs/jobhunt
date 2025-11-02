const statusLog = document.getElementById("status-log");
const fetchBtn = document.getElementById("fetch-btn");
const matchBtn = document.getElementById("match-btn");
const applyFilterBtn = document.getElementById("apply-filter");
const jobsTableBody = document.querySelector("#jobs-table tbody");
const sourceInput = document.getElementById("filter-source");
const scoreInput = document.getElementById("filter-score");

function logStatus(message) {
  const timestamp = new Date().toLocaleTimeString();
  statusLog.textContent = `[${timestamp}] ${message}\n` + statusLog.textContent;
}

async function fetchJobs() {
  logStatus("Fetching jobs from providers...");
  try {
    const response = await fetch("/api/jobs/fetch", { method: "POST" });
    const data = await response.json();
    logStatus(`Fetched jobs: ${JSON.stringify(data.counts)}`);
    await loadMatches();
  } catch (error) {
    logStatus(`Fetch failed: ${error}`);
  }
}

async function loadMatches() {
  const params = new URLSearchParams({ limit: "50" });
  const response = await fetch(`/api/jobs/match?${params.toString()}`);
  const data = await response.json();
  renderJobs(data.jobs || []);
  logStatus(`Loaded ${data.jobs?.length || 0} matches`);
}

function renderJobs(jobs) {
  const sourceFilter = sourceInput.value.trim().toLowerCase();
  const minScore = parseFloat(scoreInput.value || '0');
  jobsTableBody.innerHTML = '';
  jobs
    .filter((job) => {
      const scoreOk = !Number.isNaN(minScore) ? (job.match_score || 0) >= minScore : true;
      const sourceOk = sourceFilter ? job.source.toLowerCase().includes(sourceFilter) : true;
      return scoreOk && sourceOk;
    })
    .forEach((job) => {
      const row = document.createElement('tr');
      const cells = [
        [(job.match_score || 0).toFixed(2), 'Score'],
        [`<a href=\"${job.apply_url}\" target=\"_blank\" rel=\"noopener\">${job.title}</a>`, 'Title'],
        [job.company, 'Company'],
        [job.location || '', 'Location'],
        [job.summary || '', 'Summary'],
        [(job.tags || []).join(', '), 'Tags'],
      ];
      cells.forEach(([content, label]) => {
        const cell = document.createElement('td');
        cell.dataset.label = label;
        cell.innerHTML = content;
        row.appendChild(cell);
      });
      const actionCell = document.createElement('td');
      actionCell.dataset.label = 'Actions';
      const applyButton = document.createElement('button');
      applyButton.textContent = 'Apply';
      applyButton.addEventListener('click', () => applyToJob(job.id));
      actionCell.appendChild(applyButton);
      row.appendChild(actionCell);
      jobsTableBody.appendChild(row);
    });
}

async function applyToJob(jobId) {
  logStatus(`Preparing application for job ${jobId}...`);
  try {
    const response = await fetch("/api/jobs/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_id: jobId, auto_submit: false }),
    });
    const data = await response.json();
    if (response.ok) {
      logStatus(`Application ready. Resume: ${data.resume_path}`);
    } else {
      logStatus(`Apply failed: ${data.detail || response.status}`);
    }
  } catch (error) {
    logStatus(`Apply failed: ${error}`);
  }
}

fetchBtn.addEventListener("click", fetchJobs);
matchBtn.addEventListener("click", loadMatches);
applyFilterBtn.addEventListener("click", () => loadMatches());

loadMatches();

if (refreshSeconds && Number.isFinite(refreshSeconds) && refreshSeconds > 0) {
  setInterval(loadMatches, refreshSeconds * 1000);
}
