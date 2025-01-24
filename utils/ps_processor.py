from typing import Dict, List
import pandas as pd
from datetime import datetime
import io
import streamlit as st

class PSProcessor:
    def __init__(self):
        self.categories = {
            'shuttle': ['shuttle', 'free shuttle', 'replacement bus'],
            'reroute': ['via', 'rerouted', 'skip', 'bypass', 'two sections', 'detour'],
            'local': ['local', 'express to local', 'making local stops'],
            'suspended': ['suspended', 'no service', 'not running']
        }

    def process_single_line_alerts(self, data: Dict) -> pd.DataFrame:
        """Process alerts for single line detailed view"""
        alerts = []
        for entity in data.get('entity', []):
            if 'alert' in entity:
                alert = entity['alert']
                alert_type = alert.get('transit_realtime.mercury_alert', {}).get('alert_type', '')
                
                if 'Reduced Service' in alert_type:
                    continue
                    
                active_periods = alert.get('active_period', [])
                start_time = min((period.get('start', float('inf')) 
                                for period in active_periods), default=float('inf'))
                
                alerts.append({
                    'Start Time': datetime.fromtimestamp(start_time) if start_time != float('inf') else None,
                    'Type': alert_type,
                    'Header': alert.get('header_text', {}).get('translation', [{}])[0].get('text', ''),
                    'Period': alert.get('transit_realtime.mercury_alert', {}).get('human_readable_active_period', {}).get('translation', [{}])[0].get('text', '')
                })
        
        df = pd.DataFrame(alerts)
        if not df.empty and 'Start Time' in df.columns:
            return df.sort_values('Start Time')
        return df

    def categorize_alert(self, header: str, description: str, alert_type: str) -> str:
        """Categorize alert based on text content"""
        text = f"{header} {description} {alert_type}".lower()
        
        if any(keyword in text for keyword in self.categories['shuttle']):
            return 'Replacement Shuttles'
        elif any(keyword in text for keyword in self.categories['reroute']):
            return 'Reroute'
        elif any(keyword in text for keyword in self.categories['local']):
            return 'Run Local'
        elif any(keyword in text for keyword in self.categories['suspended']):
            return 'Suspended'
        else:
            return 'Other'

    def process_alerts_to_summary(self, data: Dict) -> Dict[str, pd.DataFrame]:
        """Process alerts into categorized DataFrames"""
        categories_data = {
            'Replacement Shuttles': [],
            'Reroute': [],
            'Run Local': [],
            'Suspended': [],
            'Other': []
        }
        
        for entity in data.get('entity', []):
            if 'alert' in entity:
                alert = entity['alert']
                
                alert_type = alert.get('transit_realtime.mercury_alert', {}).get('alert_type', '')
                if 'Reduced Service' in alert_type:
                    continue
                
                header = alert.get('header_text', {}).get('translation', [{}])[0].get('text', '')
                desc = alert.get('description_text', {}).get('translation', [{}])[0].get('text', '')
                
                routes = []
                for informed in alert.get('informed_entity', []):
                    if 'route_id' in informed:
                        routes.append(informed['route_id'])
                
                category = self.categorize_alert(header, desc, alert_type)
                
                alert_data = {
                    'Line': ', '.join(sorted(set(routes))),
                    'Date': alert.get('transit_realtime.mercury_alert', {}).get('human_readable_active_period', {}).get('translation', [{}])[0].get('text', ''),
                    'Type': alert_type,
                    'Impact': header,
                    'Description': desc,
                    'In GTFS': '',
                    'Notes': ''
                }
                
                categories_data[category].append(alert_data)
        
        return {category: pd.DataFrame(data) for category, data in categories_data.items() if data}

    def create_excel_summary(self, categorized_dfs: Dict[str, pd.DataFrame]) -> bytes:
        """Create formatted Excel file with multiple sheets for each category"""
        buffer = io.BytesIO()
        
        try:
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Write each category to a separate sheet
                for category, df in categorized_dfs.items():
                    sheet_name = category[:31]  # Excel sheet name length limit
                    if not df.empty:  # Only write non-empty dataframes
                        df.to_excel(writer, index=False, sheet_name=sheet_name)
                        
                        # Get worksheet
                        worksheet = writer.sheets[sheet_name]
                        
                        # Format columns
                        for idx, col in enumerate(df.columns):
                            try:
                                max_length = max(
                                    df[col].astype(str).apply(len).max(),
                                    len(str(col))
                                ) + 2
                                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
                            except Exception as e:
                                continue
            
            # Important: Get the bytes before returning
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            st.error(f"Error creating Excel file: {str(e)}")
            return None