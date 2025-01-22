# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import json
from parsers.gpt_parser import GPTParser
from parsers.mistral_parser import MistralParser
from parsers.regex_parser import RegexParser
from utils.metrics import calculate_metrics
from utils.visualization import visualize_differences
from utils.data_handler import save_results, load_sample_alerts

class PSAnalyzerApp:
    def __init__(self):
        st.set_page_config(page_title="PS Analyzer", layout="wide")
        self.initialize_session_state()
        
    def initialize_session_state(self):
        if 'test_results' not in st.session_state:
            st.session_state.test_results = []
            
    def main(self):
        self.render_sidebar()
        self.render_main_content()

    def render_sidebar(self):
        with st.sidebar:
            st.title("PS Analyzer Settings")
            
            # Model Selection
            st.subheader("Parser Selection")
            selected_models = st.multiselect(
                "Choose Models to Compare",
                ["GPT-3.5", "GPT-4", "Mistral", "Current Regex"],
                default=["GPT-3.5", "Current Regex"]
            )
            
            # Sample Data
            st.subheader("Test Data")
            data_option = st.radio(
                "Choose Data Source",
                ["Sample Alerts", "Custom Input", "Batch Testing"]
            )
            
            # Save results option
            if st.button("Export Results"):
                self.export_results()

    def render_main_content(self):
        st.title("MTA Planned Service Analyzer")
        
        # Input Section
        with st.expander("Input Configuration", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                alert_text = st.text_area(
                    "Enter PS Alert Text",
                    height=200,
                    placeholder="[M] Service changes..."
                )
                
            with col2:
                st.subheader("Alert Stats")
                if alert_text:
                    st.write(f"Characters: {len(alert_text)}")
                    st.write(f"Lines mentioned: {len(alert_text.split('['))}")
        
        # Analysis Section
        if st.button("Analyze Alert"):
            if alert_text:
                self.run_analysis(alert_text)
                
    def run_analysis(self, text):
        with st.spinner("Analyzing alert..."):
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs([
                "Parser Comparison", 
                "Visualization", 
                "Detailed Analysis"
            ])
            
            results = self.get_parsing_results(text)
            
            with tab1:
                self.show_parser_comparison(results)
                
            with tab2:
                self.show_visualizations(results)
                
            with tab3:
                self.show_detailed_analysis(results)
                
    def get_parsing_results(self, text):
        results = {}
        for model in ["gpt", "mistral", "regex"]:
            try:
                if model == "gpt":
                    parser = GPTParser()
                elif model == "mistral":
                    parser = MistralParser()
                else:
                    parser = RegexParser()
                    
                start_time = datetime.now()
                result = parser.parse(text)
                end_time = datetime.now()
                
                results[model] = {
                    "result": result,
                    "processing_time": (end_time - start_time).total_seconds(),
                    "success": True
                }
            except Exception as e:
                results[model] = {
                    "result": None,
                    "error": str(e),
                    "success": False
                }
        return results
    
    def show_parser_comparison(self, results):
        cols = st.columns(len(results))
        for idx, (model, data) in enumerate(results.items()):
            with cols[idx]:
                st.subheader(f"{model.upper()}")
                if data["success"]:
                    st.json(data["result"])
                    st.metric(
                        "Processing Time", 
                        f"{data['processing_time']:.3f}s"
                    )
                else:
                    st.error(f"Error: {data['error']}")
                    
    def export_results(self):
        if st.session_state.test_results:
            df = pd.DataFrame(st.session_state.test_results)
            st.download_button(
                "Download Results CSV",
                df.to_csv(index=False),
                "ps_analysis_results.csv",
                "text/csv"
            )

if __name__ == "__main__":
    app = PSAnalyzerApp()
    app.main()