"""Snapshots API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID

from app.core.db import get_session
from app.models.snapshot import Snapshot, SnapshotCreate, SnapshotResponse
from app.services.col_client import COLClient

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.post("", response_model=SnapshotResponse, status_code=201)
async def create_snapshot(
    snapshot_data: SnapshotCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new financial snapshot.
    
    If use_col_baseline is True and essential_total is not provided,
    the essential costs will be auto-filled from Cost of Living data.
    """
    # Fetch COL profile
    col_client = COLClient()
    col_profile = await col_client.get_col_profile(snapshot_data.city)
    
    # Determine essential_total
    essential_total = snapshot_data.essential_total
    if snapshot_data.use_col_baseline and essential_total is None:
        # Use COL data as baseline
        essential_total = col_profile.get("total", 2000)
    elif essential_total is None:
        # Must provide essential_total if not using COL baseline
        raise HTTPException(
            status_code=400,
            detail="essential_total must be provided or use_col_baseline must be True"
        )
    
    # Create snapshot
    snapshot = Snapshot(
        city=snapshot_data.city,
        monthly_income_takehome=snapshot_data.monthly_income_takehome,
        emergency_fund_balance=snapshot_data.emergency_fund_balance,
        essential_total=essential_total,
        discretionary_total=snapshot_data.discretionary_total,
        col_profile_json=col_profile
    )
    
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    
    return snapshot


@router.get("/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot(
    snapshot_id: UUID,
    session: Session = Depends(get_session)
):
    """Get a snapshot by ID."""
    snapshot = session.get(Snapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


@router.get("", response_model=list[SnapshotResponse])
async def list_snapshots(
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """List recent snapshots."""
    statement = select(Snapshot).order_by(Snapshot.created_at.desc()).limit(limit)
    snapshots = session.exec(statement).all()
    return snapshots
