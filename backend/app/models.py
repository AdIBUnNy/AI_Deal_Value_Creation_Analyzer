from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    company_name: str = Field(min_length=1)
    description: str = ""
    revenue: float = Field(ge=0)
    employees: int = Field(ge=1)


class Opportunity(BaseModel):
    name: str
    description: str
    estimated_annual_savings_eur: float
    hours_saved_per_year: int
    implementation_difficulty: str
    priority_score: int


class RecommendedInitiative(BaseModel):
    name: str
    why_this_first: str
    expected_impact: str
    time_to_implement: str


class ValueCreationSummary(BaseModel):
    annual_savings_eur: float
    ebitda_impact_eur: float
    payback_period_months: float
    overall_automation_potential: str


class AnalyzeResponse(BaseModel):
    investment_fit_score: int
    investment_fit_explanation: str
    ai_maturity_score: int
    ai_maturity_classification: str
    ai_maturity_breakdown: dict[str, int]
    opportunities: list[Opportunity]
    recommended_initiative: RecommendedInitiative
    value_creation_summary: ValueCreationSummary
