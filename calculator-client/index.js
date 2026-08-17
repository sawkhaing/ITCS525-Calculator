"use strict";

// ===== Settings =====
let API_BASE = "http://localhost:8000";

// ===== UI elements =====
const exprEl = document.getElementById("expr");
const valueEl = document.getElementById("value");
const grid = document.getElementById("grid");
const historyWrap = document.getElementById("history");
const clearHistoryBtn = document.getElementById("clearHistory");

// ===== Calculator state =====
let current = "0";
let expression = "";     // pretty string (× ÷ − %)
let lastWasEquals = false;
let pendingOp = null;    // "+", "−", "×", "÷"


// ===== Helpers =====
function updateDisplay() {
    exprEl.textContent = expression;
    valueEl.textContent = current;
}

function appendDigit(d) {
    if (lastWasEquals) { expression = ""; lastWasEquals = false; }
    const clearBtn = grid.querySelector('[data-action="clear"]');
    clearBtn.textContent = (current !== "0" || expression) ? "C" : "AC";

    if (d === ".") {
        if (!current.includes(".")) current += ".";
        updateDisplay();
        return;
    }
    current = (current === "0") ? d : current + d;
    updateDisplay();
}

function setOp(op) {
    if (pendingOp && !lastWasEquals) {
        equals();
        return;
    }
    const number = current;
    expression = expression ? `${expression} ${op}` : `${number} ${op}`;
    current = "0";
    pendingOp = op;
    lastWasEquals = false;
    updateActiveOps(op);
    updateDisplay();
}

function updateActiveOps(active) {
    grid.querySelectorAll(".btn-ops").forEach(b => {
        if (b.dataset.op === active) b.classList.add("active");
        else b.classList.remove("active");
    });
}

function negate() {
    if (current === "0") return;
    current = current.startsWith("-") ? current.slice(1) : "-" + current;
    updateDisplay();
}

function percent() {
    if (!current || current === "0") current = "0%";
    else if (!current.endsWith("%")) current = current + "%";
    updateDisplay();
}

function clearAllOrEntry() {
    if (current !== "0") {
        current = "0";
    } else {
        expression = "";
        pendingOp = null;
        updateActiveOps(null);
    }
    const clearBtn = grid.querySelector('[data-action="clear"]');
    clearBtn.textContent = (expression) ? "C" : "AC";
    updateDisplay();
}

// ===== History rendering =====
function renderHistory(items) {
    historyWrap.innerHTML = "";
    items.forEach(it => {
        const row = document.createElement("div");
        row.className = "h-item";
        row.innerHTML = `<span>${it.lhs ?? it.expr} =</span><b>${it.result}</b>`;
        historyWrap.appendChild(row);
    });
}


// ===== Server history API =====
async function fetchServerHistory() {

    const url = `${API_BASE}/history?limit=50`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`GET /history ${res.status}`);
    const data = await res.json();
    renderHistory(data);

}

async function clearServerHistory() {
    const url = `${API_BASE}/history`;
    const res = await fetch(url, { method: "DELETE" });
    if (!res.ok) throw new Error(`DELETE /history ${res.status}`);
    await fetchServerHistory();
}

// ===== Calculate =====
async function equals() {
    const displayExpr = expression ? `${expression} ${current}` : current;
    const sendExpr = displayExpr.trim();
    if (!sendExpr) return;

    try {
        const url = `${API_BASE}/calculate?expr=${encodeURIComponent(sendExpr)}`;
        const res = await fetch(url, { method: "POST" });
        const data = await res.json();

        if (data && data.ok) {
            const pretty = `${expression ? expression + " " : ""}${current}`;
            current = String(data.result);
            expression = "";
            pendingOp = null;
            lastWasEquals = true;
            updateActiveOps(null);
            updateDisplay();

            await fetchServerHistory();

        } else {
            showError((data && data.error) || "Error");
        }
    } catch (err) {
        showError(err.message || "Network error");
    }
}

function showError(msg) {
    valueEl.textContent = "Error";
    exprEl.textContent = msg;
    setTimeout(() => { valueEl.textContent = "0"; exprEl.textContent = ""; }, 1500);
}

// ===== Events =====
grid.addEventListener("click", (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;

    if (btn.dataset.key) appendDigit(btn.dataset.key);
    else if (btn.dataset.op) setOp(btn.dataset.op);
    else if (btn.dataset.action === "equals") equals();
    else if (btn.dataset.action === "clear") clearAllOrEntry();
    else if (btn.dataset.action === "negate") negate();
});

window.addEventListener("keydown", (e) => {
    const k = e.key;
    if (/\d/.test(k)) { appendDigit(k); return; }
    if (k === ".") { appendDigit("."); return; }
    if (k === "Enter" || k === "=") { e.preventDefault(); equals(); return; }
    if (k === "Backspace") { current = (current.length > 1) ? current.slice(0, -1) : "0"; updateDisplay(); return; }
    if (k === "Escape") { clearAllOrEntry(); return; }
    if (k === "%") { percent(); return; }
    if (k === "+") { setOp("+"); return; }
    if (k === "-") { setOp("−"); return; }
    if (k === "*" || k === "x" || k === "X") { setOp("×"); return; }
    if (k === "/") { setOp("÷"); return; }
});

document.querySelector('[data-key="%"]').addEventListener("click", percent);

clearHistoryBtn.addEventListener("click", () => {
    clearServerHistory()
});

// Initial paint & try to load server history
updateDisplay();
fetchServerHistory();
