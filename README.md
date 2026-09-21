# 💧 AquaSense — AI-Powered Smart Water Usage Advisor


> **SDG 6 — Clean Water and Sanitation** (secondary: SDG 12, SDG 13)

AquaSense lets a household or hostel log water usage in plain language, flags readings that look like a leak or overuse against a personal rolling baseline, retrieves a relevant conservation tip from a small curated knowledge base (a simplified, retrieval-augmented approach), and forecasts month-end usage from the trend observed so far.

## Features

- **Conversational logging** — type "Used 40 litres for laundry today" and it's parsed and logged automatically
- **Anomaly / leak detection** — every reading is compared to a rolling per-activity baseline
- **Retrieval-augmented tips** — a curated knowledge base of conservation guidance, retrieved by activity + severity
- **Forecasting** — projects the month-end total from the current daily rate
- **Dashboard** — live chart, stat cards, and a usage log table
- **Responsible AI panel** — states the fairness / transparency / ethics / privacy approach up front
- **Vibrant, glassmorphism UI** — an Aqua/Eco-SaaS visual design with translucent cards, gradient accents, and header/card imagery (all styling is self-contained in `index.html`, no separate CSS file)
- **No Node.js required** — both the backend (Python) and the simplest way to serve the frontend (Python's built-in web server) only need Python

## Project Structure

```
aquasense/
├── frontend/                  # Static HTML/CSS/JS client
│   ├── index.html             # single file — all styling is embedded in a <style> block
│   └── js/
│       ├── vendor/chart.umd.js # Chart.js, bundled locally (no CDN/internet dependency)
│       ├── api.js             # fetch() wrapper around the backend REST API
│       └── app.js             # UI logic, chat parsing, chart rendering
├── backend/                   # Flask REST API
│   ├── app.py                 # app entry point — run this
│   ├── routes/
│   │   ├── entries.py         # GET/POST/DELETE /api/entries
│   │   └── stats.py           # GET /api/stats, /api/tips, POST /api/seed
│   ├── utils/
│   │   ├── classify.py        # baseline calculation + anomaly detection + tip retrieval
│   │   └── forecast.py        # month-end usage forecasting
│   ├── data/
│   │   ├── knowledge_base.py  # the "RAG" knowledge base of tips
│   │   └── store.py           # simple JSON file persistence
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

##  Getting Started

### Prerequisites

Just Python 3.9+. Check with:

```bash
python3 --version
```

If that command isn't found, install Python from [python.org] (on Windows, tick "Add Python to PATH" during install).

### 1. Set up and run the backend

```bash
cd backend

# Create an isolated environment (recommended, keeps your system Python clean)
python3 -m venv venv

# Activate it:
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows (Command Prompt or PowerShell)

# Install dependencies
pip install -r requirements.txt

# (optional) copy the example env file — defaults work out of the box
cp .env.example .env

# Start the server
python app.py
```

You should see Flask log `Running on http://127.0.0.1:5000`. Leave this terminal open. Check it's alive from another terminal:

```bash
curl http://localhost:5000/api/health
```

### 2. Serve the frontend

Open a **second, separate terminal** (don't reuse the one running Flask):

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://localhost:5500` in your browser. The header badge should read **"API connected"**.

> If you deploy the backend somewhere other than `localhost:5000`, set `window.AQUASENSE_API_BASE = "https://your-api-url/api"` in a `<script>` tag before `js/api.js` loads in `index.html`.

### 3. Try it out

- Click **Load demo data** to populate 30 days of sample readings (with one intentional anomaly)
- Type things like *"Used 40 litres for laundry today"* or *"How is my usage trending?"*
- Watch the dashboard chart, stat cards, and log table update live

## 🔌 API Reference

Identical to the Node.js edition — same endpoints, same request/response shapes.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/entries` | List all logged readings (newest first) |
| POST | `/api/entries` | Log a reading — body: `{ activity, litres, date? }`. Returns the entry, its classification, a retrieved tip, and updated stats |
| DELETE | `/api/entries` | Clear all logged data |
| GET | `/api/stats` | Today / this-month / last-month / forecast totals |
| GET | `/api/tips?activity=laundry&level=high` | Retrieval-augmented tip lookup |
| POST | `/api/seed` | Populate 30 days of demo data |

**Example:**

```bash
curl -X POST http://localhost:5000/api/entries \
  -H "Content-Type: application/json" \
  -d '{"activity":"laundry","litres":40}'
```

##  How the "AI" Works

1. **NLU (frontend, rule-based):** `parseMessage()` in `frontend/js/app.js` extracts an activity keyword and a number of litres from free text using simple keyword and regex matching. This runs in the browser, same as the Node edition.
2. **Pattern detection (backend):** `classify()` in `backend/utils/classify.py` compares a new reading to the mean of all previous readings for that activity — flags `high` (≥30% above baseline, possible leak/overuse) or `low` (≥30% below, good behaviour).
3. **Retrieval-augmented tips (backend):** `retrieve_tip()` performs lexical retrieval over a small curated knowledge base (`backend/data/knowledge_base.py`), matching first on activity tag, then on severity — the same shape as a real RAG pipeline, just with a hand-written knowledge base instead of a vector store.
4. **Forecasting (backend):** `forecast_month_total()` in `backend/utils/forecast.py` projects the month-end total from the average daily rate observed so far.

This keeps the whole system dependency-light and explainable — every number the app shows can be traced back to a simple, auditable rule, which directly supports the **Transparency** requirement in the Responsible AI guidelines.

### Swapping in a real LLM / RAG pipeline

To extend this into a true LLM-backed assistant (e.g. with IBM Granite or IBM BOB):
- Replace `parseMessage()` with a call to an LLM for intent/entity extraction
- Replace the flat `knowledge_base.py` list with embeddings + a vector store (e.g. Chroma, FAISS) and do similarity search instead of tag matching in `retrieve_tip()`
- Everything else (classification, forecasting, routes, frontend) stays the same

##  Responsible AI

| Principle | How it's addressed |
|---|---|
| **Fairness** | Baselines are calculated per activity from the user's *own* history, not a generic average |
| **Transparency** | Every alert states the exact comparison that triggered it (e.g. "40L vs your 25L average") |
| **Ethics** | Tone is supportive, never punitive — the goal is habit change, not shaming |
| **Privacy** | Data is stored in a local JSON file for this prototype; no third-party sharing, and it's straightforward to add per-user auth, encryption, or delete-on-request for a production version |

##  Deployment Notes

- **Backend:** deploy `backend/` to Render, Railway, PythonAnywhere, or a small VM. Use a production WSGI server (e.g. `gunicorn app:app`) instead of Flask's built-in dev server — `pip install gunicorn` and run `gunicorn -w 2 -b 0.0.0.0:5000 app:app` from inside `backend/`. Set `PORT` and `CORS_ORIGIN` env vars.
- **Frontend:** deploy `frontend/` as a static site (Netlify, Vercel, GitHub Pages). Set `window.AQUASENSE_API_BASE` to your deployed backend URL.
- **Database:** the JSON file store in `backend/data/store.py` is fine for a demo; swap in Postgres (via SQLAlchemy) or MongoDB (via PyMongo) for multi-user production use.

##  A Note on the Design

`frontend/index.html` loads a Google Font (Plus Jakarta Sans) and a couple of Unsplash photos for the header banner and one card accent, both over the internet. If that request is offline or a network blocks those domains, the page still looks correct — it falls back to system fonts and a plain gradient background (no broken layout, just less imagery). Everything the app actually *does* (logging, chat, the dashboard) is unaffected either way, since that only depends on your local backend, not on those external assets.

##  Verified Working

This exact folder was run and tested end-to-end before packaging: `pip install`, `python app.py`, all 7 API endpoints (health, list/add/delete entries, stats, tips, seed), and the static frontend served against the live API with a real CORS preflight check — all passed.


