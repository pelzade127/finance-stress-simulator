"""Snapshot model for storing financial snapshots."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, JSON


class Snapshot(SQLModel, table=True):
    """
    A financial snapshot representing a user's financial state at a point in time.
    """
    __tablename__ = "snapshots"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Location
    city: str = Field(index=True)
    
    # Income
    monthly_income_takehome: float = Field(ge=0)
    
    # Savings
    emergency_fund_balance: float = Field(ge=0)
    
    # Expenses
    essential_total: float = Field(ge=0)
    discretionary_total: float = Field(ge=0)
    
    # Cost of Living profile (stored as JSON)
    col_profile_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class SnapshotCreate(SQLModel):
    """Schema for creating a new snapshot."""
    city: str
    monthly_income_takehome: float
    emergency_fund_balance: float
    essential_total: Optional[float] = None  # Optional for autofill
    discretionary_total: float
    use_col_baseline: bool = False  # Whether to autofill from COL data


class SnapshotResponse(SQLModel):
    """Schema for snapshot response."""
    id: UUID
    created_at: datetime
    city: str
    monthly_income_takehome: float
    emergency_fund_balance: float
    essential_total: float
    discretionary_total: float
    col_profile_json: Optional[dict] = None
