# pages/1_PS_Data_Viewer.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import json

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

st.title("PS Data Viewer")

# Initialize fetcher
fetcher = PSDataFetcher()

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    
    # Date Selection Mode
    date_mode = st.radio(
        "Select Date Mode",
        ["Weekend/Weekday", "Custom Range"]
    )
    
    if date_mode == "Weekend/Weekday":
        # Get next weekend and weekday
        today = datetime.now()
        days_to_weekend = (5 - today.weekday()) % 7  # Days until Saturday
        next_weekend = today + timedelta(days=days_to_weekend)
        next_weekday = today + timedelta(days=(7 - today.weekday()) % 7 + 1)  # Next Monday
        
        is_weekend = st.checkbox("Weekend", True)
        if is_weekend:
            selected_date = next_weekend
            end_date = next_weekend + timedelta(days=1)  # Sunday
        else:
            selected_date = next_weekday
            end_date = next_weekday  # Just Monday
    else:
        col1, col2 = st.columns(2)
        with col1:
            selected_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")

    # Route Selection
    selected_route = st.selectbox(
        "Select Subway Line",
        fetcher.subway_lines
    )

if st.button("Fetch PS Data"):
    start_datetime = datetime.combine(selected_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    with st.spinner(f"Fetching data for line {selected_route}..."):
        # Fetch data for selected route
        data = fetcher.fetch_alerts(selected_route, start_datetime, end_datetime)
        
        # Show success message with alert count
        alert_count = len(data.get('entity', []))
        st.success(f"Found {alert_count} alerts for line {selected_route}")
        
        # Add tabs for different views
        tab1, tab2 = st.tabs(["JSON Preview", "Parsed Data"])
        
        with tab1:
            # Add expand/collapse option for JSON
            with st.expander("Raw JSON Data", expanded=True):
                st.json(data)
        
        # In the tab2 section, update the alerts parsing:
        with tab2:
            if alert_count > 0:
                # Parse and sort alerts, excluding Reduced Service
                alerts = []
                for entity in data['entity']:
                    if 'alert' in entity:
                        alert = entity['alert']
                        
                        # Skip Reduced Service alerts
                        alert_type = alert.get('transit_realtime.mercury_alert', {}).get('alert_type', '')
                        if 'Reduced Service' in alert_type:
                            continue
                            
                        # Get the earliest start time from active_periods
                        active_periods = alert.get('active_period', [])
                        if active_periods:
                            start_time = min(period.get('start', float('inf')) 
                                           for period in active_periods)
                        else:
                            start_time = float('inf')
                            
                        alerts.append({
                            'Start Time': datetime.fromtimestamp(start_time) if start_time != float('inf') else None,
                            'Type': alert_type,
                            'Header': alert.get('header_text', {}).get('translation', [{}])[0].get('text', ''),
                            'Period': alert.get('transit_realtime.mercury_alert', {}).get('human_readable_active_period', {}).get('translation', [{}])[0].get('text', '')
                        })
                
                # Create DataFrame and sort by start time
                df = pd.DataFrame(alerts)
                if not df.empty and df['Start Time'].notna().any():
                    df = df.sort_values('Start Time')
                
                if not df.empty:
                    st.dataframe(df)
                    st.text(f"Showing {len(df)} alerts")
                else:
                    st.info("No relevant alerts found for this line")

# Add help section
with st.sidebar:
    st.markdown("""
    ### How to use
    1. Choose date mode (Weekend/Weekday or Custom Range)
    2. Select dates
    3. Select a subway line
    4. Click 'Fetch PS Data'
    5. View results in JSON or table format
    """)