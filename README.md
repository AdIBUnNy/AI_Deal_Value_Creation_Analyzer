# NextGen AI Deal & Value Creation Analyzer

A student-built prototype for screening DACH Mittelstand service companies and identifying AI-driven value creation opportunities for private equity buy-and-build deals.

## Project structure

This project is structured as a lightweight monorepo:

- `frontend/`
  - React + TypeScript application
  - Vite-powered UI
  - `src/App.tsx` contains the main user workflow and result rendering
  - `src/api.ts` handles requests to the backend
  - `src/styles.css` contains the core layout and visual design
  - `src/types.ts` describes the response schema the app expects

- `backend/`
  - Python FastAPI service
  - `app/main.py` defines the API endpoints and mock company data endpoint
  - `app/analyzer.py` contains the core scoring, maturity, opportunity, and recommendation logic
  - `app/models.py` defines Pydantic request/response models
  - `.env` provides the live AI key and endpoint configuration when available
  - `requirements.txt` lists Python dependencies

## How it works end to end

1. **User input**
   - The user enters a company name, revenue, employee count, and a short description.
   - This is designed for real companies rather than mock picks.

2. **Frontend request**
   - The form sends a POST request to `http://localhost:8000/analyze`.
   - `frontend/src/api.ts` builds the payload and parses the response.

3. **Backend analysis**
   - FastAPI receives the request in `backend/app/main.py`.
   - `backend/app/analyzer.py` first checks whether `OPENAI_API_KEY` is configured.
   - If the key exists, it attempts a live OpenAI-compatible request through the provided gateway.
   - If the AI call is unavailable or invalid, it falls back to deterministic scoring logic.

4. **Decision output**
   - The backend returns structured JSON including:
     - `investment_fit_score`
     - `investment_fit_explanation`
     - `ai_maturity_score`
     - `ai_maturity_breakdown`
     - `opportunities`
     - `recommended_initiative`
     - `value_creation_summary`

5. **UI rendering**
   - The frontend displays the scores, maturity bars, prioritized opportunity cards, and the recommended first initiative.
   - The design is focused on readable decision support rather than a dashboard full of charts.

## Running the app locally

### Backend

From the project root or inside `backend/`:

```bash
cd /Users/adityabankar/Documents/Case_Study_NextGen/backend
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

If the virtual environment is not activated, use:

```bash
../.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

From the frontend folder:

```bash
cd /Users/adityabankar/Documents/Case_Study_NextGen/frontend
npm install
npm run dev
```

Then open the Vite URL shown in the terminal. The frontend expects the backend at `http://localhost:8000`.

## Live AI mode

The backend supports live AI analysis when these environment variables are set:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`

If the API key or gateway is unavailable, the backend automatically uses the built-in rule-based analyzer, so the app remains stable.

## What makes this project interview-worthy

- **Clear business focus**: It is a decision-support tool for PE deal screening, not a generic dashboard or chatbot.
- **Hybrid architecture**: deterministic fallback logic plus optional real AI integration.
- **Explainable outputs**: scores are accompanied by rationales and ranked opportunity recommendations.
- **Simple, clean frontend**: a lightweight React UI with clear card-based results and no unnecessary clutter.
- **Domain-relevant sample use**: the model is tuned for service businesses in the DACH Mittelstand.

## Interview explanation guide

### Short summary
"This is a prototype AI-powered deal screening tool for DACH service companies. It takes a company profile, evaluates PE fit and AI readiness, ranks potential value creation opportunities, and recommends the highest-ROI first initiative."

### Architecture story
1. "I built a React + TypeScript frontend for clean input and card-based output."
2. "The backend is FastAPI, which keeps the API simple and fast."
3. "The core analysis lives in a dedicated analyzer module, so the scoring logic is isolated and testable."
4. "I also added an optional live AI mode using environment-configured OpenAI credentials, while preserving a deterministic fallback for reliability."

### What to highlight
- "This is not a CRM, it’s a decision-support engine for early deal screening."
- "I prioritized output explainability: scores, maturity breakdown, and a single recommended initiative."
- "The tool is built for real company names and real PE workflows, with a focus on service companies and buy-and-build logic."

### Demo talking points
1. "Enter any company name and business description."
2. "The backend evaluates investment fit and AI maturity." 
3. "It then ranks five AI value creation opportunities and selects the first recommended initiative."
4. "This is the kind of analysis an operating associate would use before drafting a deal memo."

### Strong closing points
- "This prototype shows I can fuse domain understanding with a practical product approach."
- "I built a reliable pipeline with both deterministic business logic and optional generative AI." 
- "It is designed to scale into a production-grade tool by adding persistence, user workflows, and deal-level calibration."

## Notes
- The frontend and backend are intentionally separated to keep the system modular.
- The backend can run with or without a live AI key.
- The UI emphasizes readable investment output rather than a data-heavy dashboard.
