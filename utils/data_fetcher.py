# utils/data_fetcher.py
import requests
from datetime import datetime
from typing import Dict, List
import pandas as pd

class PSDataFetcher:
    def __init__(self):
        self.base_url = "https://collector-otp-prod.camsys-apps.com/realtime/gtfsrt/filtered/alerts"
        self.api_key = "qeqy84JE7hUKfaI0Lxm2Ttcm6ZA0bYrP"
        self.subway_lines = ["1", "2", "3", "4", "5", "6", "7", "A", "C", "E", "B", "D", "F", "M", "N", "Q", "R", "W", "G", "J", "Z", "L", "S"]

    def fetch_all_ps_data(self) -> List[Dict]:
        all_alerts = []
        
        for line in self.subway_lines:
            params = {
                "type": "json",
                "apikey": self.api_key,
                "routeId": line,
                "agencyId": "MTASBWY"
            }
            
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'entity' in data:
                    for entity in data['entity']:
                        if 'alert' in entity:
                            alert = entity['alert']
                            alert['route_id'] = line
                            all_alerts.append(alert)
                            
            except requests.RequestException as e:
                raise Exception(f"Error fetching data for line {line}: {str(e)}")
                
        return all_alerts

    def parse_alerts_to_df(self, alerts: List[Dict]) -> pd.DataFrame:
        parsed_data = []
        
        for alert in alerts:
            try:
                row = {
                    'Route': alert.get('route_id', ''),
                    'Type': alert.get('transit_realtime.mercury_alert', {}).get('alert_type', ''),
                    'Header': alert.get('header_text', {}).get('translation', [{}])[0].get('text', ''),
                    'Description': alert.get('description_text', {}).get('translation', [{}])[0].get('text', ''),
                    'Active Period': alert.get('transit_realtime.mercury_alert', {}).get('human_readable_active_period', {}).get('translation', [{}])[0].get('text', '')
                }
                parsed_data.append(row)
                
            except Exception as e:
                raise Exception(f"Error parsing alert: {str(e)}")
                
        return pd.DataFrame(parsed_data)