# pages/1_PS_Data_Viewer.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, List
import json

class PSDataFetcher:
    def __init__(self):
        self.base_url = "https://collector-otp-prod.camsys-apps.com/realtime/gtfsrt/filtered/alerts"
        self.api_key = "qeqy84JE7hUKfaI0Lxm2Ttcm6ZA0bYrP"
        self.subway_lines = ["1", "2", "3", "4", "5", "6", "7", "A", "C", "E", "B", "D", "F", "M", "N", "Q", "R", "W", "G", "J", "Z", "L", "S"]

    def fetch_alerts(self, route_id: str) -> Dict:
        """Fetch alerts for a single route"""
        params = {
            "type": "json",
            "apikey": self.api_key,
            "routeId": route_id,
            "agencyId": "MTASBWY"
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

st.title("PS Data Viewer")

# Initialize fetcher
fetcher = PSDataFetcher()

# Add route selection
selected_route = st.selectbox(
    "Select Subway Line",
    fetcher.subway_lines
)

if st.button("Fetch PS Data"):
    with st.spinner(f"Fetching data for line {selected_route}..."):
        # Fetch data for selected route
        data = fetcher.fetch_alerts(selected_route)
        
        # Show success message with alert count
        alert_count = len(data.get('entity', []))
        st.success(f"Found {alert_count} alerts for line {selected_route}")
        
        # Add tabs for different views
        tab1, tab2 = st.tabs(["JSON Preview", "Parsed Data"])
        
        with tab1:
            # Add expand/collapse option for JSON
            with st.expander("Raw JSON Data", expanded=True):
                st.json(data)
        
        with tab2:
            if alert_count > 0:
                # Show parsed data in table format
                alerts = []
                for entity in data['entity']:
                    if 'alert' in entity:
                        alert = entity['alert']
                        alerts.append({
                            'Type': alert.get('transit_realtime.mercury_alert', {}).get('alert_type', ''),
                            'Header': alert.get('header_text', {}).get('translation', [{}])[0].get('text', ''),
                            'Period': alert.get('transit_realtime.mercury_alert', {}).get('human_readable_active_period', {}).get('translation', [{}])[0].get('text', '')
                        })
                
                df = pd.DataFrame(alerts)
                st.dataframe(df)
            else:
                st.info("No alerts found for this line")

# Add help section
with st.sidebar:
    st.markdown("""
    ### How to use
    1. Select a subway line from the dropdown
    2. Click 'Fetch PS Data'
    3. View raw JSON in the 'JSON Preview' tab
    4. See parsed data in the 'Parsed Data' tab
    """)