import React, { useState } from 'react';
import axios from 'axios';
import { Line, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './App.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
function App() {
  const [step, setStep] = useState(1); // 1 = input form, 2 = results
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    city: 'Grand Prairie, Texas',
    monthly_income_takehome: 4500,
    emergency_fund_balance: 8000,
    essential_total: 2200,
    discretionary_total: 800,
  });
  const [results, setResults] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'city' ? value : parseFloat(value) || 0
    }));
  };

  const runSimulation = async () => {
    setLoading(true);
    try {
      // Step 1: Create snapshot
      const snapshotResponse = await axios.post(`${API_BASE}/snapshots`, {
        ...formData,
        use_col_baseline: false
      });

      const snapshotId = snapshotResponse.data.id;

      // Step 2: Run simulation
      const simulationResponse = await axios.post(`${API_BASE}/simulate`, {
        snapshot_id: snapshotId
      });

      setResults(simulationResponse.data.results);
      setStep(2);
    } catch (error) {
      console.error('Error running simulation:', error);
      alert('Error running simulation. Make sure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  const getMonthlyNet = () => {
    return formData.monthly_income_takehome - formData.essential_total - formData.discretionary_total;
  };

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getScenarioName = (type) => {
    const names = {
      'job_loss': '💼 Job Loss',
      'income_cut_20': '📉 20% Income Cut',
      'income_cut_40': '📉 40% Income Cut',
      'rent_increase': '🏠 Rent Increase',
      'one_time_emergency': '🚨 Emergency Expense',
      'inflation_spike': '📈 Inflation Spike'
    };
    return names[type] || type;
  };

  const getScenarioDescription = (type) => {
    const descriptions = {
      'job_loss': 'Complete loss of income starting immediately',
      'income_cut_20': 'Income reduced by 20% (reduced hours, pay cut)',
      'income_cut_40': 'Income reduced by 40% (major pay cut)',
      'rent_increase': 'Housing costs increase by 15%',
      'one_time_emergency': 'Unexpected $1,500 expense (medical, car repair)',
      'inflation_spike': 'Essential expenses increase by 5% per year'
    };
    return descriptions[type] || '';
  };

  if (step === 1) {
    const monthlyNet = getMonthlyNet();
    const isSaving = monthlyNet > 0;

    return (
      <div className="App">
        <div className="container">
          <header className="header">
            <h1>💰 Financial Stress Simulator</h1>
            <p>See how long you'd survive different financial disasters</p>
          </header>

          <div className="card">
            <h2>Your Financial Snapshot</h2>
            <p className="subtitle">Enter your current financial situation</p>

            <div className="form">
              <div className="form-group">
                <label>
                  📍 City
                  <input
                    type="text"
                    name="city"
                    value={formData.city}
                    onChange={handleInputChange}
                    placeholder="e.g., Austin, Texas"
                  />
                </label>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>
                    💵 Monthly Income (after taxes)
                    <input
                      type="number"
                      name="monthly_income_takehome"
                      value={formData.monthly_income_takehome}
                      onChange={handleInputChange}
                      placeholder="4500"
                    />
                  </label>
                </div>

                <div className="form-group">
                  <label>
                    🏦 Emergency Fund
                    <input
                      type="number"
                      name="emergency_fund_balance"
                      value={formData.emergency_fund_balance}
                      onChange={handleInputChange}
                      placeholder="8000"
                    />
                  </label>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>
                    🏠 Essential Expenses (rent, food, bills)
                    <input
                      type="number"
                      name="essential_total"
                      value={formData.essential_total}
                      onChange={handleInputChange}
                      placeholder="2200"
                    />
                  </label>
                </div>

                <div className="form-group">
                  <label>
                    🎉 Fun Money (dining, hobbies, etc.)
                    <input
                      type="number"
                      name="discretionary_total"
                      value={formData.discretionary_total}
                      onChange={handleInputChange}
                      placeholder="800"
                    />
                  </label>
                </div>
              </div>

              <div className="summary-box">
                <h3>Right Now:</h3>
                <div className="summary-stats">
                  <div className="stat">
                    <span className="stat-label">Monthly Income:</span>
                    <span className="stat-value">{formatCurrency(formData.monthly_income_takehome)}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Total Expenses:</span>
                    <span className="stat-value">
                      {formatCurrency(formData.essential_total + formData.discretionary_total)}
                    </span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Net per month:</span>
                    <span className={`stat-value ${isSaving ? 'positive' : 'negative'}`}>
                      {isSaving ? '+' : ''}{formatCurrency(monthlyNet)}
                    </span>
                  </div>
                </div>
                {isSaving ? (
                  <p className="summary-message positive">
                    ✅ You're saving {formatCurrency(monthlyNet)}/month. Nice!
                  </p>
                ) : (
                  <p className="summary-message negative">
                    ⚠️ You're losing {formatCurrency(Math.abs(monthlyNet))}/month!
                  </p>
                )}
              </div>

              <button
                className="btn-primary"
                onClick={runSimulation}
                disabled={loading}
              >
                {loading ? '🔄 Running Simulation...' : '🚀 Run "What If" Scenarios'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // RESULTS VIEW
  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>📊 Your Financial Stress Test Results</h1>
          <button className="btn-secondary" onClick={() => { setStep(1); setResults(null); }}>
            ← Run New Simulation
          </button>
        </header>

        <div className="results-grid">
          {results && results.map((result, index) => {
            const chartData = result.balance_series.map((balance, month) => ({
              month,
              balance: Math.round(balance)
            }));

            return (
              <div key={index} className="result-card">
                <div className="result-header">
                  <div>
                    <h3>{getScenarioName(result.scenario_type)}</h3>
                    <p className="scenario-description">{getScenarioDescription(result.scenario_type)}</p>
                  </div>
                  <div className="risk-badge" style={{ backgroundColor: getRiskColor(result.risk_level) }}>
                    {result.risk_level.toUpperCase()}
                  </div>
                </div>

                <div className="metrics">
                  <div className="metric">
                    <span className="metric-label">Runway</span>
                    <span className="metric-value">
                      {result.runway_months} months
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">You hit $0 in</span>
                    <span className="metric-value">
                      {result.breach_month ? `Month ${result.breach_month}` : 'Never! 🎉'}
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Ending Balance</span>
                    <span className={`metric-value ${result.ending_balance >= 0 ? 'positive' : 'negative'}`}>
                      {formatCurrency(result.ending_balance)}
                    </span>
                  </div>
                </div>

                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis 
                        dataKey="month" 
                        label={{ value: 'Months', position: 'insideBottom', offset: -5 }}
                      />
                      <YAxis 
                        tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                      />
                      <Tooltip 
                        formatter={(value) => formatCurrency(value)}
                        labelFormatter={(month) => `Month ${month}`}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="balance" 
                        stroke="#8b5cf6" 
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {result.top_levers && result.top_levers.length > 0 && (
                  <div className="levers">
                    <h4>💡 What You Can Do:</h4>
                    {result.top_levers.map((lever, idx) => (
                      <div key={idx} className="lever">
                        <div className="lever-header">
                          <span className="lever-label">{lever.label}</span>
                          <span className="lever-impact">+{lever.delta_months} months</span>
                        </div>
                        <p className="lever-description">{lever.description}</p>
                        <p className="lever-result">
                          New runway: <strong>{lever.new_runway_months} months</strong>
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default App;
