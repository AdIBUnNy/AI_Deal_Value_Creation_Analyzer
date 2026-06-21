export type Opportunity = {
  name: string;
  description: string;
  estimated_annual_savings_eur: number;
  hours_saved_per_year: number;
  implementation_difficulty: 'Low' | 'Medium' | 'High';
  priority_score: number;
};

export type AnalysisResponse = {
  investment_fit_score: number;
  investment_fit_explanation: string;
  ai_maturity_score: number;
  ai_maturity_classification: 'Low' | 'Medium' | 'High';
  ai_maturity_breakdown: {
    sales_automation_level: number;
    operations_automation_level: number;
    customer_support_automation_level: number;
    knowledge_management_maturity: number;
  };
  opportunities: Opportunity[];
  recommended_initiative: {
    name: string;
    why_this_first: string;
    expected_impact: string;
    time_to_implement: string;
  };
  value_creation_summary: {
    annual_savings_eur: number;
    ebitda_impact_eur: number;
    payback_period_months: number;
    overall_automation_potential: 'Low' | 'Medium' | 'High';
  };
};
