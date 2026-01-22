"""Simulation API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID

from app.core.db import get_session
from app.models.snapshot import Snapshot
from app.models.run import SimulationRun, SimulationRequest, SimulationResponse, SimulationResult
from app.domain.scenarios import get_default_scenarios, get_scenario_params
from app.domain.simulator import FinancialSimulator, SimulationInput, calculate_risk_level
from app.domain.levers import calculate_levers

router = APIRouter(prefix="/simulate", tags=["simulation"])


@router.post("", response_model=SimulationResponse)
async def run_simulation(
    request: SimulationRequest,
    session: Session = Depends(get_session)
):
    """
    Run financial stress simulations for a snapshot.
    
    If scenarios are not specified, runs all default scenarios.
    """
    # Get the snapshot
    snapshot = session.get(Snapshot, request.snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Prepare simulation input
    sim_input = SimulationInput(
        monthly_income_takehome=snapshot.monthly_income_takehome,
        emergency_fund_balance=snapshot.emergency_fund_balance,
        essential_total=snapshot.essential_total,
        discretionary_total=snapshot.discretionary_total,
        horizon_months=12
    )
    
    # Determine which scenarios to run
    scenarios_to_run = request.scenarios if request.scenarios else get_default_scenarios()
    
    # Run simulations
    results = []
    for scenario in scenarios_to_run:
        scenario_type = scenario["type"]
        custom_params = scenario.get("params", {})
        
        # Get final params (merge custom with defaults)
        scenario_params = get_scenario_params(scenario_type, custom_params)
        
        # Run simulation
        simulator = FinancialSimulator(sim_input)
        sim_output = simulator.simulate(scenario_type, scenario_params)
        
        # Calculate risk level
        total_expenses = snapshot.essential_total + snapshot.discretionary_total
        risk_level = calculate_risk_level(sim_output.runway_months, total_expenses)
        
        # Calculate levers
        levers = calculate_levers(sim_input, scenario_type, scenario_params, sim_output.runway_months)
        
        # Create result
        result = SimulationResult(
            scenario_type=scenario_type,
            scenario_params=scenario_params,
            runway_months=round(sim_output.runway_months, 2),
            breach_month=sim_output.breach_month,
            balance_series=[round(b, 2) for b in sim_output.balance_series],
            risk_level=risk_level,
            min_balance=round(sim_output.min_balance, 2),
            ending_balance=round(sim_output.ending_balance, 2),
            top_levers=levers
        )
        
        results.append(result)
        
        # Save to database
        sim_run = SimulationRun(
            snapshot_id=snapshot.id,
            scenario_type=scenario_type,
            scenario_params_json=scenario_params,
            results_json=result.model_dump()
        )
        session.add(sim_run)
    
    session.commit()
    
    return SimulationResponse(
        snapshot_id=snapshot.id,
        results=results
    )


@router.get("/scenarios")
async def list_scenarios():
    """List all available scenarios."""
    return {"scenarios": get_default_scenarios()}


@router.get("/snapshots/{snapshot_id}/results")
async def get_snapshot_results(
    snapshot_id: UUID,
    session: Session = Depends(get_session)
):
    """Get all simulation results for a snapshot."""
    # Verify snapshot exists
    snapshot = session.get(Snapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    
    # Get all runs for this snapshot
    statement = select(SimulationRun).where(
        SimulationRun.snapshot_id == snapshot_id
    ).order_by(SimulationRun.created_at.desc())
    
    runs = session.exec(statement).all()
    
    # Convert to response format
    results = []
    for run in runs:
        result = SimulationResult(**run.results_json)
        results.append(result)
    
    return SimulationResponse(
        snapshot_id=snapshot_id,
        results=results
    )
