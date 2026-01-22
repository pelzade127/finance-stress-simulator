"""Quick test script to verify the simulator works."""
from app.domain.simulator import FinancialSimulator, SimulationInput
from app.domain.scenarios import get_default_scenarios, get_scenario_params
from app.domain.levers import calculate_levers


def test_simulator():
    """Quick test of the simulator functionality."""
    print("🧪 Testing Financial Stress Simulator\n")
    
    # Create test input
    sim_input = SimulationInput(
        monthly_income_takehome=5000,
        emergency_fund_balance=10000,
        essential_total=2500,
        discretionary_total=1000,
        horizon_months=12
    )
    
    print("📊 Test Scenario:")
    print(f"   Income: ${sim_input.monthly_income_takehome}/month")
    print(f"   Emergency Fund: ${sim_input.emergency_fund_balance}")
    print(f"   Essential Expenses: ${sim_input.essential_total}/month")
    print(f"   Discretionary: ${sim_input.discretionary_total}/month")
    print()
    
    # Test job loss scenario
    print("💼 Scenario: Job Loss")
    print("-" * 50)
    
    scenario_params = get_scenario_params("job_loss")
    simulator = FinancialSimulator(sim_input)
    result = simulator.simulate("job_loss", scenario_params)
    
    print(f"   Runway: {result.runway_months:.2f} months")
    print(f"   Breach Month: {result.breach_month}")
    print(f"   Ending Balance: ${result.ending_balance:.2f}")
    print(f"   Min Balance: ${result.min_balance:.2f}")
    print()
    
    # Test levers
    print("🎯 Top Recommended Actions:")
    print("-" * 50)
    
    levers = calculate_levers(sim_input, "job_loss", scenario_params, result.runway_months)
    
    for i, lever in enumerate(levers, 1):
        print(f"{i}. {lever['label']}")
        print(f"   Impact: +{lever['delta_months']:.2f} months runway")
        print(f"   New Runway: {lever['new_runway_months']:.2f} months")
        print(f"   {lever['description']}")
        print()
    
    print("✅ Simulator test completed successfully!")
    print()
    print("Available scenarios:")
    for scenario in get_default_scenarios():
        print(f"  - {scenario['name']}: {scenario['description']}")


if __name__ == "__main__":
    test_simulator()
