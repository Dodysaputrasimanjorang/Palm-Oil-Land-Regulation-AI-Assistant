/* ===================================================
   Hybrid RAG Regulasi Lahan — Frontend Logic
   =================================================== */

const API = "";  // same origin

// ---- DOM refs ----
const questionInput  = document.getElementById("questionInput");
const askBtn         = document.getElementById("askBtn");
const examples       = document.getElementById("examples");
const loading        = document.getElementById("loading");
const result         = document.getElementById("result");
const metrics        = document.getElementById("metrics");
const filterBadges   = document.getElementById("filterBadges");
const answerText     = document.getElementById("answerText");
const sourcesList    = document.getElementById("sourcesList");
const scoreTableBody = document.querySelector("#scoreTable tbody");

const topKSlider     = document.getElementById("topK");
const topKVal        = document.getElementById("topKVal");
const autoFilter     = document.getElementById("autoFilter");

const sidebarToggle  = document.getElementById("sidebarToggle");
const sidebar        = document.getElementById("sidebar");
const ragasSampleSize = document.getElementById("ragasSampleSize");
const runRagasBtn = document.getElementById("runRagasBtn");
const ragasStatus = document.getElementById("ragasStatus");
const ragasResult = document.getElementById("ragasResult");
const ragasMetrics = document.getElementById("ragasMetrics");
const ragasMeta = document.getElementById("ragasMeta");
const ragasTableBody = document.getElementById("ragasTableBody");

// ---- Slider sync ----
topKSlider.addEventListener("input", () => { topKVal.textContent = topKSlider.value; });

// ---- Sidebar toggle (mobile) ----
sidebarToggle.addEventListener("click", () => sidebar.classList.toggle("open"));

// ---- RAGAS evaluation ----
if (runRagasBtn) {
    runRagasBtn.addEventListener("click", runRagasEvaluation);
}

// ---- Load stats ----
async function loadStats() {
    try {
        const res = await fetch(`${API}/api/stats`);
        const data = await res.json();
        document.getElementById("statChunks").textContent = (data.total_chunks || 0).toLocaleString();
        document.getElementById("statDocs").textContent   = data.total_docs || 0;
        document.getElementById("statPasal").textContent  = (data.total_pasal || 0).toLocaleString();
    } catch (e) {
        console.warn("Stats fetch failed", e);
    }
}
loadStats();

// ---- Example buttons ----
document.querySelectorAll(".example-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        questionInput.value = btn.textContent;
        submitQuestion();
    });
});

// ---- Ask button ----
askBtn.addEventListener("click", submitQuestion);
questionInput.addEventListener("keydown", e => {
    if (e.key === "Enter") submitQuestion();
});

// ---- Main query function ----
async function submitQuestion() {
    const q = questionInput.value.trim();
    if (!q) return;

    // Show loading, hide previous result
    examples.classList.add("hidden");
    result.classList.add("hidden");
    loading.classList.remove("hidden");
    askBtn.disabled = true;

    const topK = parseInt(topKSlider.value);
    const af   = autoFilter.checked;

    try {
        const res = await fetch(`${API}/api/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: q, top_k: topK, auto_filter: af })
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || "Server error");
        }

        const data = await res.json();
        renderResult(data);
    } catch (err) {
        const msg = (err && err.message === "Failed to fetch")
            ? "Tidak bisa terhubung ke backend. Pastikan `python server.py` sedang berjalan di port 5000."
            : err.message;
        alert("Error: " + msg);
    } finally {
        loading.classList.add("hidden");
        askBtn.disabled = false;
    }
}

// ---- Render result ----
function renderResult(data) {
    // Metrics
    const refCount = (data.referenced_sources || data.sources).length;
    metrics.innerHTML = `
        <div class="metric-card">
            <span class="metric-icon">⏱</span>
            <div class="metric-label">Waktu Proses</div>
            <div class="metric-value">${data.elapsed}s</div>
        </div>
        <div class="metric-card">
            <span class="metric-icon">§</span>
            <div class="metric-label">Dasar Hukum Dirujuk</div>
            <div class="metric-value">${refCount}</div>
        </div>
        <div class="metric-card">
            <span class="metric-icon">📄</span>
            <div class="metric-label">Total Retrieval</div>
            <div class="metric-value">${data.sources.length}</div>
        </div>
        <div class="metric-card">
            <span class="metric-icon">⚖</span>
            <div class="metric-label">Filter Aktif</div>
            <div class="metric-value">${Object.keys(data.metadata_filters).length}</div>
        </div>
    `;

    // Filter badges
    const filters = data.metadata_filters || {};
    if (Object.keys(filters).length > 0) {
        filterBadges.innerHTML = Object.entries(filters).map(([k, v]) => {
            const val = Array.isArray(v) ? v.join(", ") : v;
            return `<span class="filter-badge">${k}: ${val}</span>`;
        }).join("");
        filterBadges.classList.remove("hidden");
    } else {
        filterBadges.classList.add("hidden");
    }

    // Answer
    answerText.textContent = data.answer;

    // Check if answer indicates no information found
    const answerTextLower = (data.answer || "").toLowerCase();
    const noInfoFound = answerTextLower.startsWith("informasi tidak ditemukan dalam dokumen yang tersedia") && (data.sources || []).length === 0;

    // Sources card & Score details visibility
    const sourcesCard = document.querySelector(".sources-card");
    const scoreDetails = document.querySelector(".score-details");

    if (noInfoFound) {
        sourcesCard.classList.add("hidden");
        scoreDetails.classList.add("hidden");
    } else {
        sourcesCard.classList.remove("hidden");
        scoreDetails.classList.remove("hidden");

        // Sources (Dasar Hukum) — only show sources referenced in the answer
        const refSources = data.referenced_sources || data.sources;
        const refSourcesSorted = sortSourcesByScore(refSources);
        sourcesList.innerHTML = refSourcesSorted.map((src, i) => {
            const retrievalScore = getRetrievalScore(src);
            const bm25Score = getBm25Score(src);
            const semanticScore = getSemanticScore(src);
            const semanticNorm = getScore(src, "semantic_norm");
            const bm25Norm = getScore(src, "bm25_norm");
            const scoreClass = retrievalScore > 0.7 ? "score-high" : retrievalScore > 0.4 ? "score-mid" : "score-low";
            return `
            <div class="source-item" onclick="this.classList.toggle('open')">
                <div class="source-header">
                    <span class="source-title"><span class="source-num">${i+1}</span> ${esc(src.dokumen)} — ${esc(src.pasal)}</span>
                    <span class="source-score ${scoreClass}">${retrievalScore.toFixed(4)}</span>
                </div>
                <div class="source-meta">
                    <span><b>Jenis:</b> ${esc(src.jenis)}</span>
                    <span><b>Tahun:</b> ${src.tahun}</span>
                    <span><b>Topik:</b> ${esc(src.topik)}</span>
                </div>
                <div class="source-scores-detail">
                    <span>Retrieval: ${retrievalScore.toFixed(4)}</span>
                    <span>Semantic: ${semanticScore.toFixed(4)}</span>
                    <span>BM25: ${bm25Score.toFixed(2)}</span>
                    <span>Sem(norm): ${semanticNorm.toFixed(4)}</span>
                    <span>BM25(norm): ${bm25Norm.toFixed(4)}</span>
                </div>
                <div class="source-preview">${esc(src.preview)}…</div>
            </div>`;
        }).join("");

        // Score table
        const tableSources = sortSourcesByScore(data.sources || []);
        scoreTableBody.innerHTML = tableSources.map((src, i) => `
            <tr>
                <td>${i+1}</td>
                <td>${esc(src.dokumen)}</td>
                <td>${esc(src.pasal)}</td>
                <td>${getRetrievalScore(src).toFixed(4)}</td>
                <td>${getSemanticScore(src).toFixed(4)}</td>
                <td>${getBm25Score(src).toFixed(2)}</td>
            </tr>
        `).join("");
    }

    result.classList.remove("hidden");
}

// ---- Helpers ----
function esc(s) {
    if (!s) return "";
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
}

function toFiniteNumber(value, fallback = 0) {
    const num = Number(value);
    return Number.isFinite(num) ? num : fallback;
}

function getScore(source, key, fallback = 0) {
    return toFiniteNumber(source?.scores?.[key], fallback);
}

function sortSourcesByScore(sources) {
    return (sources || [])
        .map((src, idx) => ({ src, idx }))
        .sort((a, b) => {
            const scoreDiff = getRetrievalScore(b.src) - getRetrievalScore(a.src);
            return scoreDiff !== 0 ? scoreDiff : a.idx - b.idx;
        })
        .map(item => item.src);
}

function getRetrievalScore(source) {
    return toFiniteNumber(
        source?.retrieval_score ?? source?.scores?.retrieval_score ?? source?.scores?.hybrid,
        0
    );
}

function getSemanticScore(source) {
    return toFiniteNumber(source?.semantic_score ?? source?.scores?.semantic, 0);
}

function getBm25Score(source) {
    return toFiniteNumber(source?.bm25_score ?? source?.scores?.bm25, 0);
}

async function runRagasEvaluation() {
    const sampleSize = Math.max(1, parseInt(ragasSampleSize.value || "5", 10));
    const topK = parseInt(topKSlider.value, 10);
    const af = autoFilter.checked;

    runRagasBtn.disabled = true;
    ragasStatus.textContent = "Evaluasi berjalan...";

    try {
        const res = await fetch(`${API}/api/eval/ragas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sample_size: sampleSize, top_k: topK, auto_filter: af }),
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || "Gagal menjalankan evaluasi RAGAS");
        }

        renderRagasResult(data);
        ragasStatus.textContent = data.warning || "Evaluasi selesai";
    } catch (err) {
        ragasStatus.textContent = "Evaluasi gagal";
        const msg = (err && err.message === "Failed to fetch")
            ? "Tidak bisa terhubung ke backend. Pastikan `python server.py` aktif dan tidak berhenti."
            : err.message;
        alert("Error evaluasi RAGAS: " + msg);
    } finally {
        runRagasBtn.disabled = false;
    }
}

function renderRagasResult(data) {
    const s = data.summary || {};
    ragasMetrics.innerHTML = `
        <div class="metric-card"><div class="metric-label">Faithfulness</div><div class="metric-value">${(s.faithfulness || 0).toFixed(4)}</div></div>
        <div class="metric-card"><div class="metric-label">Answer Relevancy</div><div class="metric-value">${(s.answer_relevancy || 0).toFixed(4)}</div></div>
        <div class="metric-card"><div class="metric-label">Context Precision</div><div class="metric-value">${(s.context_precision || 0).toFixed(4)}</div></div>
        <div class="metric-card"><div class="metric-label">Context Recall</div><div class="metric-value">${(s.context_recall || 0).toFixed(4)}</div></div>
        <div class="metric-card"><div class="metric-label">Rata-rata Latency</div><div class="metric-value">${(s.avg_latency || 0).toFixed(2)}s</div></div>
    `;

    const files = data.files || {};
    ragasMeta.innerHTML = `
        <p><b>Jumlah pertanyaan:</b> ${s.num_questions || 0} | <b>Waktu evaluasi:</b> ${data.elapsed || 0}s</p>
        <p><b>File JSON:</b> ${esc(files.json || "-")}</p>
        <p><b>File CSV:</b> ${esc(files.csv || "-")}</p>
    `;

    ragasTableBody.innerHTML = (data.details || []).map((row) => `
        <tr>
            <td>${row.question_id}</td>
            <td>${esc(row.question)}</td>
            <td>${(row.faithfulness || 0).toFixed(4)}</td>
            <td>${(row.answer_relevancy || 0).toFixed(4)}</td>
            <td>${(row.context_precision || 0).toFixed(4)}</td>
            <td>${(row.context_recall || 0).toFixed(4)}</td>
            <td>${(row.latency || 0).toFixed(2)}</td>
        </tr>
    `).join("");

    ragasResult.classList.remove("hidden");
}
