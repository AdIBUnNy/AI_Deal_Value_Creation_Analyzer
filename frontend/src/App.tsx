import { useState } from 'react';
import { analyzeCompany } from './api';
import type { AnalysisResponse } from './types';
import './styles.css';

const DEFAULT_FORM = {
  companyName: '',
  description: '',
  revenue: '',
  employees: ''
};

function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-CH', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 0
  }).format(value);
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('en-CH', {
    maximumFractionDigits: 0
  }).format(value);
}

function scoreClass(score: number) {
  if (score >= 75) return 'score score-high';
  if (score >= 50) return 'score score-medium';
  return 'score score-low';
}

function difficultyClass(difficulty: string) {
  if (difficulty === 'Low') return 'tag tag-low';
  if (difficulty === 'Medium') return 'tag tag-medium';
  return 'tag tag-high';
}

function ProgressBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="progress-row">
      <div className="progress-label">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

export default function App() {
  const [companyName, setCompanyName] = useState(DEFAULT_FORM.companyName);
  const [description, setDescription] = useState(DEFAULT_FORM.description);
  const [revenue, setRevenue] = useState(DEFAULT_FORM.revenue);
  const [employees, setEmployees] = useState(DEFAULT_FORM.employees);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleAnalyze() {
    setError('');
    setLoading(true);
    try {
      const result = await analyzeCompany({
        company_name: companyName.trim(),
        description: description.trim(),
        revenue: Number(revenue),
        employees: Number(employees)
      });
      setAnalysis(result);
    } catch (analysisError) {
      setError(analysisError instanceof Error ? analysisError.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <main className="layout">
        <section className="hero card compact-hero">
          <div className="hero-copy">
            <p className="eyebrow"></p>
            <h1>Evaluate real companies and surface AI-driven value creation.</h1>
            <p className="hero-text">
              Enter any existing company, then let the model suggest fit, automation opportunity, and the best first initiative.
            </p>
          </div>
        </section>

        <section className="content-grid">
          <div className="card form-card">
            <div className="section-head">
              <div>
                <p className="section-label">Company Analyzer</p>
                <h2>Real-company intake</h2>
              </div>
            </div>

            <label className="field">
              <span>Company name</span>
              <input value={companyName} onChange={(event) => setCompanyName(event.target.value)} placeholder="e.g. Siemens Mobility" />
            </label>

            <label className="field">
              <span>Website or description</span>
              <textarea
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Briefly describe the business, service model, and growth context"
                rows={5}
              />
            </label>

            <div className="form-row">
              <label className="field">
                <span>Estimated revenue (€)</span>
                <input value={revenue} onChange={(event) => setRevenue(event.target.value)} type="number" min="0" />
              </label>
              <label className="field">
                <span>Employees</span>
                <input value={employees} onChange={(event) => setEmployees(event.target.value)} type="number" min="1" />
              </label>
            </div>

            <button className="primary-button" onClick={handleAnalyze} disabled={loading || !companyName || !description}>
              {loading ? 'Analyzing...' : 'Analyze Company'}
            </button>
            {error ? <p className="error-box">{error}</p> : null}
          </div>

          <div className="card insights-card">
            <div className="section-head">
              <div>
                <p className="section-label">Core Output</p>
                <h2>AI deal analysis</h2>
              </div>
              <span className="muted">Actionable fit score, maturity, and value creation</span>
            </div>

            {analysis ? (
              <div className="analysis-stack">
                <div className="metric-grid">
                  <article className="metric-card">
                    <span>Investment fit score</span>
                    <strong className={scoreClass(analysis.investment_fit_score)}>{analysis.investment_fit_score}</strong>
                    <p>{analysis.investment_fit_explanation}</p>
                  </article>
                  <article className="metric-card">
                    <span>AI maturity score</span>
                    <strong className={scoreClass(analysis.ai_maturity_score)}>{analysis.ai_maturity_score}</strong>
                    <p>
                      {analysis.ai_maturity_classification} maturity, based on automation across sales, operations,
                      support, and knowledge management.
                    </p>
                  </article>
                </div>

                <article className="panel">
                  <div className="panel-head">
                    <div>
                      <h3>AI maturity snapshot</h3>
                      <p className="panel-note">How ready the business is to capture AI value across core workflows.</p>
                    </div>
                    <span className="pill">{analysis.ai_maturity_classification}</span>
                  </div>
                  <ProgressBar label="Sales automation readiness" value={analysis.ai_maturity_breakdown.sales_automation_level} />
                  <ProgressBar label="Operations automation readiness" value={analysis.ai_maturity_breakdown.operations_automation_level} />
                  <ProgressBar label="Support automation readiness" value={analysis.ai_maturity_breakdown.customer_support_automation_level} />
                  <ProgressBar label="Knowledge management readiness" value={analysis.ai_maturity_breakdown.knowledge_management_maturity} />
                </article>

                <article className="panel">
                  <div className="panel-head">
                    <h3>Top 5 AI value creation opportunities</h3>
                    <span className="muted">Ranked by priority</span>
                  </div>
                  <div className="opportunity-list">
                    {analysis.opportunities.map((opportunity) => (
                      <div className="opportunity-card" key={opportunity.name}>
                        <div className="opportunity-head">
                          <div>
                            <h4>{opportunity.name}</h4>
                            <p>{opportunity.description}</p>
                          </div>
                          <span className="priority-badge">{opportunity.priority_score}</span>
                        </div>
                        <div className="opportunity-meta">
                          <span>{formatCurrency(opportunity.estimated_annual_savings_eur)} annual savings</span>
                          <span>{formatNumber(opportunity.hours_saved_per_year)} hours saved</span>
                          <span className={difficultyClass(opportunity.implementation_difficulty)}>
                            {opportunity.implementation_difficulty} difficulty
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </article>

                <article className="panel recommendation">
                  <div className="panel-head">
                    <h3>Recommended first initiative</h3>
                    <span className="pill">Highest ROI</span>
                  </div>
                  <h4>{analysis.recommended_initiative.name}</h4>
                  <p>{analysis.recommended_initiative.why_this_first}</p>
                  <p>{analysis.recommended_initiative.expected_impact}</p>
                  <p className="muted">Time to implement: {analysis.recommended_initiative.time_to_implement}</p>
                </article>

                <article className="panel summary-panel">
                  <div className="panel-head">
                    <h3>Value creation summary</h3>
                    <span className="pill">{analysis.value_creation_summary.overall_automation_potential} automation potential</span>
                  </div>
                  <div className="summary-grid">
                    <div>
                      <span>Estimated annual cost savings</span>
                      <strong>{formatCurrency(analysis.value_creation_summary.annual_savings_eur)}</strong>
                    </div>
                    <div>
                      <span>Estimated EBITDA impact</span>
                      <strong>{formatCurrency(analysis.value_creation_summary.ebitda_impact_eur)}</strong>
                    </div>
                    <div>
                      <span>Payback period</span>
                      <strong>{analysis.value_creation_summary.payback_period_months} months</strong>
                    </div>
                  </div>
                </article>
              </div>
            ) : (
              <div className="empty-state">
                <h3>Run an analysis to see the deal view</h3>
                <p>
                  The result should read like a short investment memo: fit score, AI maturity, prioritized opportunities,
                  and one first move.
                </p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
