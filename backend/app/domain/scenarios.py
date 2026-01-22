"""Scenario definitions and configurations."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ScenarioType(str, Enum):
    """Available scenario types."""
    JOB_LOSS = "job_loss"
    INCOME_CUT_20 = "income_cut_20"
    INCOME_CUT_40 = "income_cut_40"
    RENT_INCREASE = "rent_increase"
    ONE_TIME_EMERGENCY = "one_time_emergency"
    INFLATION_SPIKE = "inflation_spike"


@dataclass
class ScenarioDefinition:
    """Definition of a scenario with its parameters."""
    type: ScenarioType
    name: str
    description: str
    default_params: dict


# Default scenario configurations
DEFAULT_SCENARIOS = [
    ScenarioDefinition(
        type=ScenarioType.JOB_LOSS,
        name="Job Loss",
        description="Complete loss of income starting immediately",
        default_params={"start_month": 1, "income_multiplier": 0.0}
    ),
    ScenarioDefinition(
        type=ScenarioType.INCOME_CUT_20,
        name="20% Income Reduction",
        description="Income reduced by 20% (pay cut, reduced hours)",
        default_params={"start_month": 1, "income_multiplier": 0.8}
    ),
    ScenarioDefinition(
        type=ScenarioType.INCOME_CUT_40,
        name="40% Income Reduction",
        description="Income reduced by 40% (major pay cut)",
        default_params={"start_month": 1, "income_multiplier": 0.6}
    ),
    ScenarioDefinition(
        type=ScenarioType.RENT_INCREASE,
        name="Rent/Housing Increase",
        description="Housing costs increase by 15%",
        default_params={"start_month": 1, "increase_percent": 0.15}
    ),
    ScenarioDefinition(
        type=ScenarioType.ONE_TIME_EMERGENCY,
        name="Emergency Expense",
        description="Unexpected $1,500 expense (medical, car repair, etc.)",
        default_params={"month": 1, "amount": 1500}
    ),
    ScenarioDefinition(
        type=ScenarioType.INFLATION_SPIKE,
        name="Inflation Spike",
        description="Essential expenses increase by 5% per year",
        default_params={"monthly_increase_rate": 0.05 / 12}  # 5% annual = ~0.4% monthly
    ),
]


def get_default_scenarios() -> list[dict]:
    """Get all default scenarios as dictionaries."""
    return [
        {
            "type": scenario.type.value,
            "name": scenario.name,
            "description": scenario.description,
            "params": scenario.default_params,
        }
        for scenario in DEFAULT_SCENARIOS
    ]


def get_scenario_params(scenario_type: str, custom_params: Optional[dict] = None) -> dict:
    """Get scenario parameters, merging custom params with defaults."""
    # Find default scenario
    default_scenario = next(
        (s for s in DEFAULT_SCENARIOS if s.type.value == scenario_type), None
    )
    
    if not default_scenario:
        raise ValueError(f"Unknown scenario type: {scenario_type}")
    
    # Merge with custom params
    params = default_scenario.default_params.copy()
    if custom_params:
        params.update(custom_params)
    
    return params
