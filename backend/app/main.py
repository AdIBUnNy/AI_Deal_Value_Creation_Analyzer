from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import analyze_company
from .models import AnalyzeRequest

app = FastAPI(title="NextGen AI Deal & Value Creation Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_COMPANIES = [
    {
        "name": "Alpha Facility Services GmbH",
        "country": "Germany",
        "industry": "Facility services",
        "revenue": 18500000,
        "employees": 210,
        "description": "Mid-sized provider of cleaning, building services, and on-site facility operations for commercial clients.",
    },
    {
        "name": "Swiss Logistics Operations AG",
        "country": "Switzerland",
        "industry": "Logistics services",
        "revenue": 32400000,
        "employees": 340,
        "description": "Regional logistics operator managing warehousing, dispatch, and route coordination for B2B customers.",
    },
    {
        "name": "Staffing Partners Deutschland GmbH",
        "country": "Germany",
        "industry": "Staffing services",
        "revenue": 27100000,
        "employees": 190,
        "description": "Flexible staffing and recruitment business serving industrial and administrative workforce needs.",
    },
    {
        "name": "B2B Consulting Group GmbH",
        "country": "Germany",
        "industry": "Consulting services",
        "revenue": 14200000,
        "employees": 95,
        "description": "Operational consulting firm supporting process improvement, transformation projects, and recurring advisory work.",
    },
    {
        "name": "Industrial Maintenance Austria GmbH",
        "country": "Austria",
        "industry": "Industrial maintenance services",
        "revenue": 22800000,
        "employees": 165,
        "description": "Maintenance and technical field-service provider for industrial equipment uptime, inspections, and repairs.",
    },
]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/mock-companies")
def mock_companies() -> list[dict[str, object]]:
    return MOCK_COMPANIES


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    return analyze_company(request)
