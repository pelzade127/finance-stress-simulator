"""Core simulation engine for financial stress modeling."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SimulationInput:
    """Input parameters for a simulation."""
    monthly_income_takehome: float
    emergency_fund_balance: float
    essential_total: float
    discretionary_total: float
    horizon_months: int = 12


@dataclass
class SimulationOutput:
    """Output results from a simulation."""
    runway_months: float
    breach_month: Optional[int]
    balance_series: list[float]
    min_balance: float
    ending_balance: float


class FinancialSimulator:
    """
    Core simulation engine that models financial fragility under various scenarios.
    
    This is pure domain logic - no dependencies on FastAPI, database, etc.
    """
    
    def __init__(self, input_data: SimulationInput):
        self.income = input_data.monthly_income_takehome
        self.initial_balance = input_data.emergency_fund_balance
        self.essential = input_data.essential_total
        self.discretionary = input_data.discretionary_total
        self.horizon = input_data.horizon_months
    
    def simulate(
        self,
        scenario_type: str,
        scenario_params: dict
    ) -> SimulationOutput:
        """
        Run a simulation for a given scenario.
        
        Args:
            scenario_type: Type of scenario to simulate
            scenario_params: Parameters specific to the scenario
            
        Returns:
            SimulationOutput with results
        """
        # Initialize tracking
        balance = self.initial_balance
        balance_series = [balance]
        breach_month = None
        
        # Run month-by-month simulation
        for month in range(1, self.horizon + 1):
            # Calculate income for this month
            income = self._calculate_income(month, scenario_type, scenario_params)
            
            # Calculate expenses for this month
            expenses = self._calculate_expenses(month, scenario_type, scenario_params)
            
            # Apply one-time shocks
            one_time_shock = self._calculate_one_time_shock(month, scenario_type, scenario_params)
            
            # Update balance
            balance = balance + income - expenses - one_time_shock
            balance_series.append(balance)
            
            # Track first breach
            if breach_month is None and balance < 0:
                breach_month = month
        
        # Calculate runway
        runway_months = self._calculate_runway(balance_series)
        
        return SimulationOutput(
            runway_months=runway_months,
            breach_month=breach_month,
            balance_series=balance_series,
            min_balance=min(balance_series),
            ending_balance=balance_series[-1]
        )
    
    def _calculate_income(self, month: int, scenario_type: str, params: dict) -> float:
        """Calculate income for a given month based on scenario."""
        if scenario_type in ["job_loss", "income_cut_20", "income_cut_40"]:
            start_month = params.get("start_month", 1)
            multiplier = params.get("income_multiplier", 1.0)
            
            if month >= start_month:
                return self.income * multiplier
        
        return self.income
    
    def _calculate_expenses(self, month: int, scenario_type: str, params: dict) -> float:
        """Calculate total expenses for a given month based on scenario."""
        essential = self.essential
        discretionary = self.discretionary
        
        # Rent/housing increase (assuming housing is ~30-40% of essential costs)
        if scenario_type == "rent_increase":
            start_month = params.get("start_month", 1)
            increase_percent = params.get("increase_percent", 0.15)
            
            if month >= start_month:
                # Estimate housing as 35% of essential costs
                housing_portion = essential * 0.35
                housing_increase = housing_portion * increase_percent
                essential = essential + housing_increase
        
        # Inflation spike (compounds monthly)
        if scenario_type == "inflation_spike":
            monthly_rate = params.get("monthly_increase_rate", 0.05 / 12)
            essential = essential * ((1 + monthly_rate) ** month)
        
        return essential + discretionary
    
    def _calculate_one_time_shock(self, month: int, scenario_type: str, params: dict) -> float:
        """Calculate one-time expense shocks."""
        if scenario_type == "one_time_emergency":
            shock_month = params.get("month", 1)
            amount = params.get("amount", 1500)
            
            if month == shock_month:
                return amount
        
        return 0.0
    
    def _calculate_runway(self, balance_series: list[float]) -> float:
        """
        Calculate runway in months (fractional).
        
        Runway is defined as how long funds last before hitting $0.
        Uses linear interpolation for fractional months.
        """
        for i in range(len(balance_series) - 1):
            if balance_series[i] >= 0 and balance_series[i + 1] < 0:
                # Linear interpolation to find exact crossing point
                curr_balance = balance_series[i]
                next_balance = balance_series[i + 1]
                decline = curr_balance - next_balance
                
                if decline > 0:
                    fraction = curr_balance / decline
                    return i + fraction
        
        # If never breached, runway is the full horizon (or longer)
        if balance_series[-1] >= 0:
            return float(self.horizon)
        
        # If started negative
        return 0.0


def calculate_risk_level(runway_months: float, monthly_expenses: float) -> str:
    """
    Calculate risk level based on runway and expenses.
    
    Rules:
    - High risk: < 2 months runway
    - Medium risk: 2-6 months runway
    - Low risk: > 6 months runway
    """
    if runway_months < 2:
        return "high"
    elif runway_months < 6:
        return "medium"
    else:
        return "low"
