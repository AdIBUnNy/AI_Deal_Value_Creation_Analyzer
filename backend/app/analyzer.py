from __future__ import annotations

import json
import os
import math
import urllib.error
import urllib.request
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

from .models import (
    AnalyzeRequest,
    AnalyzeResponse,
    Opportunity,
    RecommendedInitiative,
    ValueCreationSummary,
)


SERVICE_KEYWORDS = [
    "service",
    "facility",
    "logistics",
    "staffing",
    "consulting",
    "maintenance",
    "operations",
    "outsourcing",
    "support",
    "field",
    "industrial",
]

AUTOMATION_THEMES = [
    (
        "Scheduling Automation",
        "Automate dispatching, shift planning, and resource allocation to reduce manual coordination.",
        "Operations automation level",
        0.95,
        260,
    ),
    (
        "Proposal Generation Automation",
        "Use AI to draft proposals, service quotes, and scope-of-work documents faster.",
        "Sales automation level",
        0.9,
        200,
    ),
    (
        "Customer Support Copilot",
        "Provide frontline staff with an AI assistant for repetitive client questions and case handling.",
        "Customer support automation level",
        0.75,
        180,
    ),
    (
        "Document Processing Automation",
        "Extract data from invoices, service reports, and contracts to eliminate manual back-office work.",
        "Operations automation level",
        0.85,
        220,
    ),
    (
        "Internal Knowledge Assistant",
        "Make SOPs, policies, and project learnings searchable through a secure internal copilot.",
        "Knowledge management maturity",
        0.7,
        140,
    ),
]


@dataclass(frozen=True)
class CompanySignals:
    service_fit: float
    mittelstand_fit: float
    fragmentation_fit: float
    scalability_fit: float
    automation_fit: float


def _normalized_text(value: str) -> str:
    return value.lower().strip()


def _estimate_company_signals(request: AnalyzeRequest) -> CompanySignals:
    text = _normalized_text(f"{request.company_name} {request.description}")
    service_fit = 0.62 + 0.38 * any(keyword in text for keyword in SERVICE_KEYWORDS)
    mittelstand_fit = 0.72 + 0.18 * (request.revenue <= 200_000_000 and request.employees <= 2_000)
    fragmentation_fit = 0.65
    if any(keyword in text for keyword in ["staffing", "logistics", "facility", "maintenance", "consulting"]):
        fragmentation_fit = 0.9
    elif any(keyword in text for keyword in ["software", "platform", "digital", "cloud"]):
        fragmentation_fit = 0.78
    scalability_fit = 0.5 + max(0, (2500 - request.employees) / 4500)
    if request.revenue < 20_000_000:
        scalability_fit += 0.08
    automation_usefulness = 0.52 + 0.4 * any(keyword in text for keyword in ["manual", "repetitive", "dispatch", "support", "documents", "scheduling", "paper", "invoice", "report"])
    automation_fit = min(1.0, automation_usefulness + (request.employees / 2000) * 0.14)
    return CompanySignals(
        service_fit=min(1.0, service_fit),
        mittelstand_fit=min(1.0, mittelstand_fit),
        fragmentation_fit=min(1.0, fragmentation_fit),
        scalability_fit=min(1.0, max(0.45, scalability_fit)),
        automation_fit=min(1.0, automation_fit),
    )


def _fit_score(signals: CompanySignals) -> tuple[int, str]:
    score = round(
        100
        * (
            signals.service_fit * 0.28
            + signals.mittelstand_fit * 0.22
            + signals.scalability_fit * 0.18
            + signals.fragmentation_fit * 0.16
            + signals.automation_fit * 0.16
        )
    )
    score = max(0, min(100, score))
    explanation_parts = []
    if signals.service_fit > 0.8:
        explanation_parts.append("The business reads as service-heavy, which is attractive for buy-and-build consolidation.")
    if signals.mittelstand_fit > 0.8:
        explanation_parts.append("Its size looks like a typical DACH Mittelstand target with operational leverage potential.")
    if signals.fragmentation_fit > 0.85:
        explanation_parts.append("The market appears fragmented enough to support a roll-up strategy.")
    if signals.automation_fit > 0.8:
        explanation_parts.append("The operating model likely contains repetitive workflows that AI can improve quickly.")
    if not explanation_parts:
        explanation_parts.append("The company has some characteristics of a PE-backed services platform, but the fit is more moderate.")
    return score, " ".join(explanation_parts)


def _maturity_score(request: AnalyzeRequest, signals: CompanySignals) -> tuple[int, str, dict[str, int]]:
    base = 20 + (1 - signals.automation_fit) * 18
    revenue_factor = min(request.revenue / 10_000_000, 2.5)
    sales = min(95, round(base + revenue_factor * 10 + (1 if "proposal" in _normalized_text(request.description) else 0) * 8))
    operations = min(95, round(base + min(request.employees / 50, 22) + (1 if "field" in _normalized_text(request.description) or "dispatch" in _normalized_text(request.description) else 0) * 10))
    support = min(95, round(base + 6 + (1 if "support" in _normalized_text(request.description) or "service desk" in _normalized_text(request.description) else 0) * 12))
    knowledge = min(95, round(base + 6 + (1 if request.employees > 120 else 0) * 10 + (1 if "training" in _normalized_text(request.description) or "knowledge" in _normalized_text(request.description) else 0) * 6))
    breakdown = {
        "sales_automation_level": round(sales * 1.0),
        "operations_automation_level": round(operations * 1.0),
        "customer_support_automation_level": round(support * 1.0),
        "knowledge_management_maturity": round(knowledge * 1.0),
    }
    average = round(sum(breakdown.values()) / len(breakdown))
    classification = "Low" if average < 45 else "Medium" if average < 70 else "High"
    return average, classification, breakdown


def _opportunity_priority(base_score: int, revenue: float, employees: int, scale: float, complexity: float) -> int:
    size_boost = min(18, revenue / 4_500_000)
    headcount_boost = min(15, employees / 45)
    priority = round(base_score + size_boost + headcount_boost - complexity * 9)
    return max(0, min(100, priority))


def _opportunities(request: AnalyzeRequest, maturity_breakdown: dict[str, int]) -> list[Opportunity]:
    labor_cost_proxy = max(55_000, request.revenue / max(request.employees, 1) * 0.35)
    opportunities: list[Opportunity] = []
    for name, description, maturity_key, scale, hours_multiplier in AUTOMATION_THEMES:
        maturity_value = maturity_breakdown[maturity_key.replace(" ", "_").lower()]
        annual_savings = round(labor_cost_proxy * scale * (0.45 + maturity_value / 180), 0)
        hours_saved = round(request.employees * hours_multiplier * scale)
        difficulty = "Low" if scale >= 0.9 else "Medium" if scale >= 0.8 else "High"
        priority = _opportunity_priority(int(scale * 70 + maturity_value * 0.35), request.revenue, request.employees, scale, 1.2 if difficulty == "High" else 0.5 if difficulty == "Medium" else 0.2)
        opportunities.append(
            Opportunity(
                name=name,
                description=description,
                estimated_annual_savings_eur=annual_savings,
                hours_saved_per_year=hours_saved,
                implementation_difficulty=difficulty,
                priority_score=priority,
            )
        )
    opportunities.sort(key=lambda item: item.priority_score, reverse=True)
    return opportunities


def _recommendation(opportunity: Opportunity, request: AnalyzeRequest, maturity_breakdown: dict[str, int]) -> RecommendedInitiative:
    if opportunity.name == "Scheduling Automation":
        impact = f"Likely saves about €{opportunity.estimated_annual_savings_eur:,.0f} per year while reducing planner workload and service delays."
        time_to_implement = "6-10 weeks"
    elif opportunity.name == "Document Processing Automation":
        impact = f"Likely saves about €{opportunity.estimated_annual_savings_eur:,.0f} per year by cutting manual back-office handling."
        time_to_implement = "4-8 weeks"
    elif opportunity.name == "Proposal Generation Automation":
        impact = f"Likely saves about €{opportunity.estimated_annual_savings_eur:,.0f} per year and shortens response times in sales."
        time_to_implement = "4-6 weeks"
    elif opportunity.name == "Customer Support Copilot":
        impact = f"Likely saves about €{opportunity.estimated_annual_savings_eur:,.0f} per year by helping teams answer recurring questions faster."
        time_to_implement = "6-12 weeks"
    else:
        impact = f"Likely saves about €{opportunity.estimated_annual_savings_eur:,.0f} per year by centralizing operational know-how."
        time_to_implement = "5-9 weeks"

    why_first = (
        "This is the highest-ROI first move because it is quick to deploy, improves a recurring workflow, "
        "and creates visible value without requiring a major system change."
    )
    return RecommendedInitiative(
        name=opportunity.name,
        why_this_first=why_first,
        expected_impact=impact,
        time_to_implement=time_to_implement,
    )


def _value_summary(opportunities: list[Opportunity]) -> ValueCreationSummary:
    annual_savings = round(sum(item.estimated_annual_savings_eur for item in opportunities[:3]) * 0.72, 0)
    ebitda_impact = round(annual_savings * 0.7, 0)
    implementation_cost = max(55_000, annual_savings * 0.35)
    payback_period_months = round((implementation_cost / max(annual_savings, 1)) * 12, 1)
    automation_ratio = min(0.85, 0.25 + sum(item.priority_score for item in opportunities) / 700)
    overall = "High" if automation_ratio > 0.6 else "Medium" if automation_ratio > 0.4 else "Low"
    return ValueCreationSummary(
        annual_savings_eur=annual_savings,
        ebitda_impact_eur=ebitda_impact,
        payback_period_months=payback_period_months,
        overall_automation_potential=overall,
    )


def analyze_company(request: AnalyzeRequest) -> AnalyzeResponse:
    signals = _estimate_company_signals(request)
    fit_score, fit_explanation = _fit_score(signals)
    maturity_score, maturity_classification, maturity_breakdown = _maturity_score(request, signals)
    live_response = _analyze_with_openai(request)
    if live_response is not None:
        return live_response
    opportunities = _opportunities(request, maturity_breakdown)
    recommended_initiative = _recommendation(opportunities[0], request, maturity_breakdown)
    value_creation_summary = _value_summary(opportunities)

    return AnalyzeResponse(
        investment_fit_score=fit_score,
        investment_fit_explanation=fit_explanation,
        ai_maturity_score=maturity_score,
        ai_maturity_classification=maturity_classification,
        ai_maturity_breakdown=maturity_breakdown,
        opportunities=opportunities,
        recommended_initiative=recommended_initiative,
        value_creation_summary=value_creation_summary,
    )


def _analyze_with_openai(request: AnalyzeRequest) -> AnalyzeResponse | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    prompt = {
        "company_name": request.company_name,
        "description": request.description,
        "revenue": request.revenue,
        "employees": request.employees,
        "instructions": (
            "Act as a private equity investment associate focused on DACH Mittelstand buy-and-build opportunities. "
            "Return ONLY valid JSON matching this shape: "
            "{investment_fit_score, investment_fit_explanation, ai_maturity_score, ai_maturity_classification, "
            "ai_maturity_breakdown:{sales_automation_level,operations_automation_level,customer_support_automation_level,knowledge_management_maturity}, "
            "opportunities:[{name,description,estimated_annual_savings_eur,hours_saved_per_year,implementation_difficulty,priority_score}], "
            "recommended_initiative:{name,why_this_first,expected_impact,time_to_implement}, "
            "value_creation_summary:{annual_savings_eur,ebitda_impact_eur,payback_period_months,overall_automation_potential}}. "
            "Use realistic euro amounts and keep implementation_difficulty as Low, Medium, or High. "
            "Do not wrap the JSON in markdown."
        ),
    }

    request_body = json.dumps(
        {
            "model": model,
            "input": [
                {
                    "role": "system",
                    "content": "You are an investment associate producing concise structured outputs for a PE screening tool.",
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt),
                },
            ],
            "temperature": 0.2,
        }
    ).encode("utf-8")

    request_object = urllib.request.Request(
        f"{api_base}/responses",
        data=request_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request_object, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None

    text = _extract_openai_text(payload)
    if not text:
        return None

    try:
        data = json.loads(text)
        return AnalyzeResponse.model_validate(data)
    except (json.JSONDecodeError, ValueError):
        return None


def _extract_openai_text(payload: dict[str, object]) -> str:
    output = payload.get("output", [])
    if not isinstance(output, list):
        return ""

    collected: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        content = item.get("content", [])
        if not isinstance(content, list):
            continue
        for content_item in content:
            if not isinstance(content_item, dict):
                continue
            text = content_item.get("text")
            if isinstance(text, str) and text.strip():
                collected.append(text.strip())

    return "\n".join(collected)
