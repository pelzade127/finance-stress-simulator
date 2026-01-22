"""Cost of Living API client service."""
import json
import httpx
from pathlib import Path
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class COLClient:
    """Client for fetching cost of living data."""
    
    def __init__(self):
        self.base_url = settings.COL_API_BASE_URL
        self.timeout = settings.COL_API_TIMEOUT_SECONDS
        self.fallback_path = Path(settings.COL_FALLBACK_PATH)
    
    async def get_col_profile(self, city: str) -> dict:
        """
        Get cost of living profile for a city.
        
        Tries to fetch from live API first, falls back to cached data.
        
        Args:
            city: City name (e.g., "San Francisco, CA")
            
        Returns:
            Dictionary with COL data including housing, food, transportation, etc.
        """
        # Try live API first
        try:
            profile = await self._fetch_from_api(city)
            if profile:
                profile["source"] = "live"
                return profile
        except Exception as e:
            print(f"Failed to fetch from COL API: {e}")
        
        # Fall back to cached data
        try:
            profile = self._load_from_fallback(city)
            if profile:
                profile["source"] = "fallback"
                return profile
        except Exception as e:
            print(f"Failed to load fallback data: {e}")
        
        # Ultimate fallback - return generic profile
        return self._get_generic_profile(city)
    
    async def _fetch_from_api(self, city: str) -> Optional[dict]:
        """Fetch from live COL API."""
        # Note: Adjust endpoint path based on your actual COL API structure
        url = f"{self.base_url}/api/cost-of-living/{city}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Normalize the response structure
            return self._normalize_col_data(data)
    
    def _load_from_fallback(self, city: str) -> Optional[dict]:
        """Load from local fallback JSON file."""
        if not self.fallback_path.exists():
            return None
        
        with open(self.fallback_path, "r") as f:
            fallback_data = json.load(f)
        
        # Look for city in fallback data
        city_lower = city.lower()
        for entry in fallback_data.get("cities", []):
            if entry.get("city", "").lower() == city_lower:
                return self._normalize_col_data(entry)
        
        return None
    
    def _normalize_col_data(self, data: dict) -> dict:
        """
        Normalize COL data to a consistent structure.
        
        Expected structure:
        {
            "city": "San Francisco, CA",
            "housing": 2500,
            "food": 600,
            "transportation": 200,
            "utilities": 150,
            "healthcare": 100,
            "other": 200,
            "total": 3750
        }
        """
        # If data is already normalized, return it
        if "total" in data and "housing" in data:
            return data
        
        # Try to extract and normalize from various structures
        # This depends on your actual COL API structure
        normalized = {
            "city": data.get("city", "Unknown"),
            "housing": data.get("housing", data.get("rent", 1500)),
            "food": data.get("food", data.get("groceries", 400)),
            "transportation": data.get("transportation", 150),
            "utilities": data.get("utilities", 100),
            "healthcare": data.get("healthcare", 80),
            "other": data.get("other", 150),
        }
        
        normalized["total"] = sum([
            normalized["housing"],
            normalized["food"],
            normalized["transportation"],
            normalized["utilities"],
            normalized["healthcare"],
            normalized["other"],
        ])
        
        return normalized
    
    def _get_generic_profile(self, city: str) -> dict:
        """
        Return a generic profile when all else fails.
        
        Uses national averages.
        """
        return {
            "city": city,
            "housing": 1500,
            "food": 400,
            "transportation": 150,
            "utilities": 100,
            "healthcare": 80,
            "other": 150,
            "total": 2380,
            "source": "generic",
            "note": "Using national average estimates"
        }
