"""Tests for the financial simulator."""
import pytest
from app.domain.simulator import FinancialSimulator, SimulationInput, calculate_risk_level


def test_baseline_no_shock():
    """Test baseline scenario with positive cash flow."""
    sim_input = SimulationInput(
        monthly_income_takehome=5000,
        emergency_fund_balance=10000,
        essential_total=2000,
        discretionary_total=1000,
        horizon_months=12
    )
    
    simulator = FinancialSimulator(sim_input)
    result = simulator.simulate("baseline", {})
    
    # Should have runway beyond horizon
    assert result.runway_months == 12.0
    assert result.breach_month is None
    assert result.ending_balance > result.balance_series[0]


def test_job_loss_scenario():
    """Test job loss scenario."""
    sim_input = SimulationInput(
        monthly_income_takehome=5000,
        emergency_fund_balance=10000,
        essential_total=2000,
        discretionary_total=1000,
        horizon_months=12
    )
    
    simulator = FinancialSimulator(sim_input)
    result = simulator.simulate("job_loss", {"start_month": 1, "income_multiplier": 0.0})
    
    # Should breach within horizon
    assert result.breach_month is not None
    assert result.breach_month < 12
    assert result.runway_months < 12.0
    
    # Calculate expected runway: 10000 / 3000 = 3.33 months
    expected_runway = 10000 / 3000
    assert abs(result.runway_months - expected_runway) < 0.1


def test_income_cut_scenario():
    """Test 40% income cut."""
    sim_input = SimulationInput(
        monthly_income_takehome=5000,
        emergency_fund_balance=5000,
        essential_total=2000,
        discretionary_total=1000,
        horizon_months=12
    )
    
    simulator = FinancialSimulator(sim_input)
    result = simulator.simulate("income_cut_40", {"start_month": 1, "income_multiplier": 0.6})
    
    # With 60% income (3000) and 3000 expenses, net is 0
    # Should slowly drain emergency fund
    assert result.runway_months > 0
    assert result.ending_balance < result.balance_series[0]


def test_one_time_emergency():
    """Test one-time emergency expense."""
    sim_input = SimulationInput(
        monthly_income_takehome=5000,
        emergency_fund_balance=10000,
        essential_total=2000,
        discretionary_total=1000,
        horizon_months=12
    )
    
    simulator = FinancialSimulator(sim_input)
    result = simulator.simulate("one_time_emergency", {"month": 1, "amount": 1500})
    
    # Should impact month 1 balance
    assert result.balance_series[1] < result.balance_series[0] - 1500
    
    # But should recover and not breach if positive cash flow
    assert result.breach_month is None


def test_inflation_spike():
    """Test inflation increasing costs."""
    sim_input = SimulationInput(
        monthly_income_takehome=5000,
        emergency_fund_balance=10000,
        essential_total=2000,
        discretionary_total=1000,
        horizon_months=12
    )
    
    simulator = FinancialSimulator(sim_input)
    result = simulator.simulate("inflation_spike", {"monthly_increase_rate": 0.01})
    
    # Balance should grow more slowly than baseline
    assert result.ending_balance < 34000  # 10000 + (2000 * 12)


def test_risk_level_calculation():
    """Test risk level categorization."""
    assert calculate_risk_level(1.5, 3000) == "high"
    assert calculate_risk_level(4.0, 3000) == "medium"
    assert calculate_risk_level(8.0, 3000) == "low"


def test_runway_calculation_with_interpolation():
    """Test that runway correctly interpolates fractional months."""
    sim_input = SimulationInput(
        monthly_income_takehome=0,  # No income
        emergency_fund_balance=3500,
        essential_total=1000,
        discretionary_total=0,
        horizon_months=12
    )
    
    simulator = FinancialSimulator(sim_input)
    result = simulator.simulate("job_loss", {"start_month": 1, "income_multiplier": 0.0})
    
    # Expected: 3500 / 1000 = 3.5 months
    assert abs(result.runway_months - 3.5) < 0.1
    assert result.breach_month == 4  # Should breach in month 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
