/* =========================================================
   AquaSense frontend — talks to the Express backend for
   NLU parsing (client-side, below), classification, RAG-style
   tip retrieval, and forecasting (all server-side).
   ========================================================= */

// ---- Rule-based NLU: pull activity + litres out of free text ----
function parseMessage(text) {
  const t = text.toLowerCase();
  const activities = ["laundry", "bathing", "bath", "shower", "cooking", "cleaning", "gardening", "garden", "other"];
  const map = { bath: "bathing", shower: "bathing", garden: "gardening" };
  let activity = null;
  for (const a of activities) {
    if (t.includes(a)) { activity = map[a] || a; break; }
  }
  const numMatch = t.match(/(\d+(\.\d+)?)\s*(l|litre|litres|liter|liters)?/);
  const litres = numMatch ? parseFloat(numMatch[1]) : null;
  return { activity, litres };
}

// ---- UI wiring ----
function addChatBubble(text, who) {
  const log = document.getElementById("chatlog");
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.innerHTML = `<span class="tag">${who === "user" ? "You" : "AquaSense"}</span>${text}`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

async function logReading(activity, litres, date) {
  const { entry, classification, tip } = await AquaAPI.addEntry(activity, litres, date);
  await renderAll();

  if (classification.baseline === null) {
    return `Logged ${entry.litres}L for ${entry.activity} on ${entry.date}. This is your first ${entry.activity} entry, so I don't have a baseline yet — I'll compare future readings against this. Tip: ${tip.text}`;
  }
  const pct = Math.round(Math.abs(classification.ratio - 1) * 100);
  if (classification.level === "high") {
    return `⚠️ That's ${pct}% above your usual ${entry.activity} average (${entry.litres}L vs your ${classification.baseline.toFixed(1)}L baseline) — could be a leak or one-off overuse. ${tip.text}`;
  } else if (classification.level === "low") {
    return `Nice — that's ${pct}% below your usual ${entry.activity} average (${entry.litres}L vs ${classification.baseline.toFixed(1)}L). ${tip.text}`;
  }
  return `Logged ${entry.litres}L for ${entry.activity} — that's close to your usual average of ${classification.baseline.toFixed(1)}L. ${tip.text}`;
}

async function trendReply() {
  const s = await AquaAPI.stats();
  if (s.lastMonth === 0) {
    return `You've logged ${s.month}L so far this month. I don't have last month's data yet to compare — projected month-end total is about ${s.forecast}L at your current rate.`;
  }
  const delta = Math.round(((s.month - s.lastMonth) / s.lastMonth) * 100);
  const dir = delta <= 0 ? "below" : "above";
  return `You're tracking ${Math.abs(delta)}% ${dir} last month's pace so far (${s.month}L vs ${s.lastMonth}L). At this rate you'll land around ${s.forecast}L this month.`;
}

async function generalTipReply() {
  const { tip } = await AquaAPI.tip("general", "normal");
  return tip.text;
}

async function handleChatSend() {
  const input = document.getElementById("chatInput");
  const text = input.value.trim();
  if (!text) return;
  addChatBubble(text, "user");
  input.value = "";

  const lower = text.toLowerCase();
  let reply;
  try {
    if (lower.includes("trend") || (lower.includes("how") && lower.includes("usage"))) {
      reply = await trendReply();
    } else if (lower.includes("tip") && !lower.match(/\d/)) {
      reply = await generalTipReply();
    } else {
      const { activity, litres } = parseMessage(text);
      if (activity && litres !== null) {
        reply = await logReading(activity, litres);
      } else if (litres !== null && !activity) {
        reply = `Got ${litres}L, but I couldn't tell which activity that was for — try mentioning laundry, bathing, cooking, cleaning, or gardening.`;
      } else {
        reply = "Try something like \"Used 40 litres for laundry today\", or ask \"how is my usage trending?\"";
      }
    }
  } catch (err) {
    reply = `Sorry, I couldn't reach the AquaSense API (${err.message}). Is the backend running on ${API_BASE}?`;
  }
  addChatBubble(reply, "ai");
}

function quick(text) {
  document.getElementById("chatInput").value = text;
  handleChatSend();
}
document.addEventListener("keydown", (e) => {
  if (e.target.id === "chatInput" && e.key === "Enter") handleChatSend();
});

async function logFromForm() {
  const activity = document.getElementById("fActivity").value;
  const litres = parseFloat(document.getElementById("fLitres").value);
  const date = document.getElementById("fDate").value || new Date().toISOString().slice(0, 10);
  if (!litres || litres <= 0) { alert("Enter a valid number of litres."); return; }
  addChatBubble(`Logged via form: ${litres}L for ${activity} on ${date}`, "user");
  try {
    const reply = await logReading(activity, litres, date);
    addChatBubble(reply, "ai");
  } catch (err) {
    addChatBubble(`Couldn't save that reading: ${err.message}`, "ai");
  }
  document.getElementById("fLitres").value = "";
}

async function clearAll() {
  if (!confirm("Clear all logged data on the server?")) return;
  await AquaAPI.clearEntries();
  document.getElementById("chatlog").innerHTML = "";
  await renderAll();
}

async function seedDemoData() {
  const { seeded } = await AquaAPI.seed();
  await renderAll();
  addChatBubble(`Loaded ${seeded} demo readings across the last 30 days (with one intentional usage spike on laundry) so you can see the dashboard and anomaly detection in action.`, "ai");
}

// ---- Rendering ----
let chart = null;

async function renderAll() {
  const [{ entries }, stats] = await Promise.all([AquaAPI.listEntries(), AquaAPI.stats()]);
  renderStats(stats);
  renderTable(entries);
  renderChart(entries);
}

function renderStats(stats) {
  document.getElementById("statToday").textContent = stats.today + " L";
  document.getElementById("statMonth").textContent = stats.month + " L";
  document.getElementById("statForecast").textContent = stats.forecast + " L";
}

function renderTable(entries) {
  const tbody = document.getElementById("logTable");
  tbody.innerHTML = "";
  const rows = entries.slice(0, 15);
  rows.forEach((e) => {
    // Recompute a display-only baseline comparison from the already-sorted list
    const priorSameActivity = entries.filter((x) => x.activity === e.activity && x !== e);
    let flagHtml = "—";
    if (priorSameActivity.length > 0) {
      const baseline = priorSameActivity.reduce((s, x) => s + x.litres, 0) / priorSameActivity.length;
      const ratio = e.litres / baseline;
      if (ratio >= 1.3) flagHtml = `<span class="flag-high">+${Math.round((ratio - 1) * 100)}%</span>`;
      else if (ratio <= 0.7) flagHtml = `<span class="flag-low">-${Math.round((1 - ratio) * 100)}%</span>`;
      else flagHtml = "normal";
    }
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${e.date}</td><td>${e.activity}</td><td>${e.litres} L</td><td>${flagHtml}</td>`;
    tbody.appendChild(tr);
  });
}

function renderChart(entries) {
  const byDate = {};
  entries.forEach((e) => { byDate[e.date] = (byDate[e.date] || 0) + e.litres; });
  const dates = Object.keys(byDate).sort();
  const values = dates.map((d) => byDate[d]);
  const ctx = document.getElementById("usageChart");
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: dates,
      datasets: [{
        label: "Daily total (L)",
        data: values,
        borderColor: "#1C7293",
        backgroundColor: "rgba(6,90,130,0.15)",
        tension: 0.3,
        fill: true,
        pointRadius: 2
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { maxTicksLimit: 8 } },
        y: { beginAtZero: true, title: { display: true, text: "Litres" } }
      }
    }
  });
}

// ---- init ----
(async function init() {
  document.getElementById("fDate").value = new Date().toISOString().slice(0, 10);
  const statusEl = document.getElementById("apiStatus");
  try {
    await AquaAPI.health();
    statusEl.textContent = "API connected";
  } catch {
    statusEl.textContent = `API offline — start the backend (see README)`;
  }

  try {
    const { entries } = await AquaAPI.listEntries();
    if (entries.length === 0) {
      addChatBubble("Hi! I'm AquaSense. Tell me about your water use — e.g. \"Used 40 litres for laundry today\" — or click \"Load demo data\" on the right to explore with a sample month.", "ai");
    } else {
      addChatBubble("Welcome back — your previous log is loaded from the server.", "ai");
    }
    await renderAll();
  } catch (err) {
    addChatBubble(`Couldn't load data from the API: ${err.message}. Make sure the backend is running (see README.md).`, "ai");
  }
})();
