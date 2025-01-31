# pages/2_GTFS_Data_Precheck.py
import streamlit as st
import pandas as pd
import zipfile
import io

def load_gtfs_zip(uploaded_zip):
    """Load GTFS files from zip into a dictionary of DataFrames"""
    gtfs_data = {}
    try:
        with zipfile.ZipFile(io.BytesIO(uploaded_zip.read())) as z:
            # List all txt files in zip
            txt_files = [f for f in z.namelist() if f.endswith('.txt')]
            
            for txt_file in txt_files:
                file_name = txt_file.replace('.txt', '')
                with z.open(txt_file) as f:
                    gtfs_data[file_name] = pd.read_csv(f)
                    
            return gtfs_data
    except Exception as e:
        st.error(f"Error reading zip file: {str(e)}")
        return None

def display_gtfs_info(gtfs_data, title):
    """Display detailed information about GTFS data"""
    st.subheader(title)
    
    if 'routes' in gtfs_data:
        with st.expander("Routes Information", expanded=True):
            st.write(f"Total Routes: {len(gtfs_data['routes'])}")
            # Show routes table
            st.dataframe(
                gtfs_data['routes'][['route_id', 'route_short_name', 'route_long_name']],
                use_container_width=True
            )
    
    if 'trips' in gtfs_data:
        with st.expander("Trips Information"):
            st.write(f"Total Trips: {len(gtfs_data['trips'])}")
            # Show sample of trips
            st.write("Sample of trips:")
            st.dataframe(gtfs_data['trips'].head(), use_container_width=True)
    
    if 'stops' in gtfs_data:
        with st.expander("Stops Information"):
            st.write(f"Total Stops: {len(gtfs_data['stops'])}")
            # Show sample of stops
            st.write("Sample of stops:")
            st.dataframe(gtfs_data['stops'].head(), use_container_width=True)

st.title("GTFS Data Precheck")

# Upload section
with st.sidebar:
    st.header("Upload GTFS Files")
    st.markdown("""
    Required files in zip:
    - stops.txt
    - stop_times.txt
    - trips.txt
    - routes.txt
    """)

    # File uploaders
    regular_zip = st.file_uploader(
        "Upload Regular GTFS",
        type=['zip'],
        key="regular_gtfs"
    )
    
    supplemented_zip = st.file_uploader(
        "Upload Supplemented GTFS",
        type=['zip'],
        key="supplemented_gtfs"
    )

# Process uploaded files
if regular_zip and supplemented_zip:
    try:
        with st.spinner("Loading GTFS files..."):
            regular_gtfs = load_gtfs_zip(regular_zip)
            supplemented_gtfs = load_gtfs_zip(supplemented_zip)
        
        if regular_gtfs and supplemented_gtfs:
            st.success("GTFS files loaded successfully!")
            
            # Add tabs for different views
            tab1, tab2 = st.tabs(["Regular GTFS", "Supplemented GTFS"])
            
            with tab1:
                display_gtfs_info(regular_gtfs, "Regular GTFS Details")
            
            with tab2:
                display_gtfs_info(supplemented_gtfs, "Supplemented GTFS Details")
            
            # Add comparison section
            st.markdown("---")
            st.subheader("GTFS Comparison")
            if st.button("Compare GTFS Files"):
                with st.spinner("Comparing GTFS files..."):
                    # Compare route counts
                    reg_routes = set(regular_gtfs['routes']['route_id'])
                    supp_routes = set(supplemented_gtfs['routes']['route_id'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Routes in Regular", len(reg_routes))
                        st.metric("Routes in Supplemented", len(supp_routes))
                    
                    with col2:
                        st.metric("Routes only in Regular", len(reg_routes - supp_routes))
                        st.metric("Routes only in Supplemented", len(supp_routes - reg_routes))

    except Exception as e:
        st.error(f"Error processing GTFS files: {str(e)}")