import requests
from datetime import datetime
from typing import Dict

class PSDataFetcher:
    def __init__(self):
        self.base_url = "https://collector-otp-prod.camsys-apps.com/realtime/gtfsrt/filtered/alerts"
        self.api_key = "qeqy84JE7hUKfaI0Lxm2Ttcm6ZA0bYrP"
        self.subway_lines = ["1", "2", "3", "4", "5", "6", "7", "A", "C", "E", "B", "D", "F", "M", "N", "Q", "R", "W", "G", "J", "Z", "L", "S"]

    def fetch_alerts(self, route_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Fetch alerts for a single route within date range"""
        params = {
            "type": "json",
            "apikey": self.api_key,
            "routeId": route_id,
            "agencyId": "MTASBWY",
            "startDate": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "endDate": end_date.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}