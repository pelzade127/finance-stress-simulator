"""SimulationRun model for storing simulation results."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, JSON


class SimulationRun(SQLModel, table=True):
    """
    A simulation run represents one scenario execution for a snapshot.
    """
    __tablename__ = "simulation_runs"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    snapshot_id: UUID = Field(foreign_key="snapshots.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Scenario info
    scenario_type: str = Field(index=True)
    scenario_params_json: dict = Field(sa_column=Column(JSON))
    
    # Results (stored as JSON for flexibility)
    results_json: dict = Field(sa_column=Column(JSON))


class SimulationRequest(SQLModel):
    """Schema for requesting simulations."""
    snapshot_id: UUID
    scenarios: Optional[list[dict]] = None  # If None, run all default scenarios


class SimulationResult(SQLModel):
    """Schema for a single simulation result."""
    scenario_type: str
    scenario_params: dict
    runway_months: float
    breach_month: Optional[int]
    balance_series: list[float]
    risk_level: str
    min_balance: float
    ending_balance: float
    top_levers: list[dict]


class SimulationResponse(SQLModel):
    """Schema for simulation response."""
    snapshot_id: UUID
    results: list[SimulationResult]
