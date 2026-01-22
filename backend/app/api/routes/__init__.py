"""API routes."""
from app.api.routes.health import router as health_router
from app.api.routes.snapshots import router as snapshots_router
from app.api.routes.simulate import router as simulate_router

__all__ = ["health_router", "snapshots_router", "simulate_router"]
