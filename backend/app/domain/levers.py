"""Levers module for calculating actionable financial improvements."""
from dataclasses import dataclass
from app.domain.simulator import FinancialSimulator, SimulationInput


@dataclass
class Lever:
    """A lever represents an actionable change that can improve runway."""
    label: str
    description: str
    new_runway_months: float
    delta_months: float
    impact_category: str  # "expense_reduction", "income_increase", "emergency_fund"


def calculate_levers(
    base_input: SimulationInput,
    scenario_type: str,
    scenario_params: dict,
    base_runway: float
) -> list[dict]:
    """
    Calculate top actionable levers that would extend runway.
    
    Args:
        base_input: Original simulation input
        scenario_type: The scenario being analyzed
        scenario_params: Parameters for the scenario
        base_runway: The baseline runway months
        
    Returns:
        List of lever dictionaries, sorted by impact (delta_months)
    """
    levers = []
    
    # Lever 1: Cut discretionary spending by 30%
    if base_input.discretionary_total > 0:
        modified_input = SimulationInput(
            monthly_income_takehome=base_input.monthly_income_takehome,
            emergency_fund_balance=base_input.emergency_fund_balance,
            essential_total=base_input.essential_total,
            discretionary_total=base_input.discretionary_total * 0.7,
            horizon_months=base_input.horizon_months
        )
        simulator = FinancialSimulator(modified_input)
        result = simulator.simulate(scenario_type, scenario_params)
        
        delta = result.runway_months - base_runway
        if delta > 0.1:  # Only include if meaningful impact
            levers.append({
                "label": "Cut discretionary spending by 30%",
                "description": f"Reduce discretionary expenses from ${base_input.discretionary_total:.0f} to ${modified_input.discretionary_total:.0f}/month",
                "new_runway_months": round(result.runway_months, 2),
                "delta_months": round(delta, 2),
                "impact_category": "expense_reduction"
            })
    
    # Lever 2: Cut discretionary spending by 50%
    if base_input.discretionary_total > 0:
        modified_input = SimulationInput(
            monthly_income_takehome=base_input.monthly_income_takehome,
            emergency_fund_balance=base_input.emergency_fund_balance,
            essential_total=base_input.essential_total,
            discretionary_total=base_input.discretionary_total * 0.5,
            horizon_months=base_input.horizon_months
        )
        simulator = FinancialSimulator(modified_input)
        result = simulator.simulate(scenario_type, scenario_params)
        
        delta = result.runway_months - base_runway
        if delta > 0.1:
            levers.append({
                "label": "Cut discretionary spending by 50%",
                "description": f"Reduce discretionary expenses from ${base_input.discretionary_total:.0f} to ${modified_input.discretionary_total:.0f}/month",
                "new_runway_months": round(result.runway_months, 2),
                "delta_months": round(delta, 2),
                "impact_category": "expense_reduction"
            })
    
    # Lever 3: Reduce housing costs (roommate assumption - $300/month savings)
    housing_savings = min(300, base_input.essential_total * 0.15)  # Cap at 15% of essential
    if housing_savings > 100:
        modified_input = SimulationInput(
            monthly_income_takehome=base_input.monthly_income_takehome,
            emergency_fund_balance=base_input.emergency_fund_balance,
            essential_total=base_input.essential_total - housing_savings,
            discretionary_total=base_input.discretionary_total,
            horizon_months=base_input.horizon_months
        )
        simulator = FinancialSimulator(modified_input)
        result = simulator.simulate(scenario_type, scenario_params)
        
        delta = result.runway_months - base_runway
        if delta > 0.1:
            levers.append({
                "label": f"Reduce housing costs by ${housing_savings:.0f}/month",
                "description": "Get a roommate or move to cheaper housing",
                "new_runway_months": round(result.runway_months, 2),
                "delta_months": round(delta, 2),
                "impact_category": "expense_reduction"
            })
    
    # Lever 4: Side income ($400/month)
    # Only relevant for job loss or income cut scenarios
    if scenario_type in ["job_loss", "income_cut_20", "income_cut_40"]:
        side_income = 400
        modified_input = SimulationInput(
            monthly_income_takehome=base_input.monthly_income_takehome + side_income,
            emergency_fund_balance=base_input.emergency_fund_balance,
            essential_total=base_input.essential_total,
            discretionary_total=base_input.discretionary_total,
            horizon_months=base_input.horizon_months
        )
        simulator = FinancialSimulator(modified_input)
        result = simulator.simulate(scenario_type, scenario_params)
        
        delta = result.runway_months - base_runway
        if delta > 0.1:
            levers.append({
                "label": f"Add side income (+${side_income}/month)",
                "description": "Freelance work, gig economy, or part-time job",
                "new_runway_months": round(result.runway_months, 2),
                "delta_months": round(delta, 2),
                "impact_category": "income_increase"
            })
    
    # Lever 5: Increase emergency fund (if currently low)
    months_of_expenses = base_input.emergency_fund_balance / (
        base_input.essential_total + base_input.discretionary_total
    )
    if months_of_expenses < 3:
        # Suggest building to 3 months
        target_fund = (base_input.essential_total + base_input.discretionary_total) * 3
        increase_needed = target_fund - base_input.emergency_fund_balance
        
        modified_input = SimulationInput(
            monthly_income_takehome=base_input.monthly_income_takehome,
            emergency_fund_balance=target_fund,
            essential_total=base_input.essential_total,
            discretionary_total=base_input.discretionary_total,
            horizon_months=base_input.horizon_months
        )
        simulator = FinancialSimulator(modified_input)
        result = simulator.simulate(scenario_type, scenario_params)
        
        delta = result.runway_months - base_runway
        if delta > 0.1:
            levers.append({
                "label": f"Build emergency fund to 3 months expenses",
                "description": f"Increase emergency fund by ${increase_needed:.0f} (to ${target_fund:.0f} total)",
                "new_runway_months": round(result.runway_months, 2),
                "delta_months": round(delta, 2),
                "impact_category": "emergency_fund"
            })
    
    # Sort by impact (delta_months) descending
    levers.sort(key=lambda x: x["delta_months"], reverse=True)
    
    # Return top 3
    return levers[:3]
