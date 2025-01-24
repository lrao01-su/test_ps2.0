import streamlit as st
from utils.ps_processor import PSProcessor
from utils.data_fetcher import PSDataFetcher
from datetime import datetime, timedelta
import pandas as pd
import io

st.title("PS Data Viewer")

# Initialize services
fetcher = PSDataFetcher()
processor = PSProcessor()

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    
    view_mode = st.radio(
        "Select View Mode",
        ["Single Line Analysis", "All Lines Summary"]
    )
    
    date_mode = st.radio(
        "Select Date Mode",
        ["Weekend/Weekday", "Custom Range"]
    )
    
    if date_mode == "Weekend/Weekday":
        today = datetime.now()
        days_to_weekend = (5 - today.weekday()) % 7
        next_weekend = today + timedelta(days=days_to_weekend)
        next_weekday = today + timedelta(days=(7 - today.weekday()) % 7 + 1)
        
        is_weekend = st.checkbox("Weekend", True)
        if is_weekend:
            start_date = next_weekend
            end_date = next_weekend + timedelta(days=1)
        else:
            start_date = next_weekday
            end_date = next_weekday
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
    
    if view_mode == "Single Line Analysis":
        selected_route = st.selectbox(
            "Select Subway Line",
            fetcher.subway_lines
        )

# Convert dates to datetime
start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

if st.button("Fetch PS Data"):
    if view_mode == "Single Line Analysis":
        with st.spinner(f"Fetching data for line {selected_route}..."):
            data = fetcher.fetch_alerts(selected_route, start_datetime, end_datetime)
            
            alert_count = len(data.get('entity', []))
            st.success(f"Found {alert_count} alerts for line {selected_route}")
            
            tab1, tab2 = st.tabs(["JSON Preview", "Parsed Data"])
            
            with tab1:
                with st.expander("Raw JSON Data", expanded=True):
                    st.json(data)
            
            with tab2:
                if alert_count > 0:
                    detailed_df = processor.process_single_line_alerts(data)
                    if not detailed_df.empty:
                        st.dataframe(detailed_df)
                    else:
                        st.info("No relevant alerts after filtering")
    
    else:  # All Lines Summary
        with st.spinner("Fetching data for all lines..."):
            all_data = {"entity": []}
            for route in fetcher.subway_lines:
                route_data = fetcher.fetch_alerts(route, start_datetime, end_datetime)
                if 'entity' in route_data:
                    all_data["entity"].extend(route_data["entity"])
            
            categorized_dfs = processor.process_alerts_to_summary(all_data)
            
            if categorized_dfs:
                st.success("Found alerts for selected period")
                
                tabs = st.tabs(list(categorized_dfs.keys()))
                
                for tab, (category, df) in zip(tabs, categorized_dfs.items()):
                    with tab:
                        st.subheader(category)
                        st.dataframe(df)
                
                # Export to Excel
                excel_data = processor.create_excel_summary(categorized_dfs)
                if excel_data:
                    st.download_button(
                        label="📥 Download Excel Summary",
                        data=excel_data,
                        file_name=f"PS_Summary_{start_date.strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("No alerts found for the selected period")