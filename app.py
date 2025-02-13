from dotenv import load_dotenv
import os
import streamlit as st
from parsers.gpt_parser import GPTParser
from parsers.regex_parser import RegexParser
from parsers.ollama_parser import OllamaParser
from datetime import datetime

load_dotenv()

def initialize_session_state():
    if 'results' not in st.session_state:
        st.session_state.results = {
            'regex': {'result': None, 'time': None},
            'gpt': {'result': None, 'time': None},
            'ollama': {'result': None, 'time': None}
        }

def display_results():
    col1, col2, col3 = st.columns(3)
    
    # Regex Results
    with col1:
        if st.session_state.results['regex']['result'] is not None:
            st.subheader("Regex Parser")
            st.json(st.session_state.results['regex']['result'])
            st.metric("Processing Time", f"{st.session_state.results['regex']['time']:.3f}s")
    
    # GPT Results        
    with col2:
        if st.session_state.results['gpt']['result'] is not None:
            st.subheader("GPT Parser")
            st.json(st.session_state.results['gpt']['result'])
            st.metric("Processing Time", f"{st.session_state.results['gpt']['time']:.3f}s")
    
    # Ollama Results
    with col3:
        if st.session_state.results['ollama']['result'] is not None:
            st.subheader("Ollama Parser")
            st.json(st.session_state.results['ollama']['result'])
            st.metric("Processing Time", f"{st.session_state.results['ollama']['time']:.3f}s")

def show_parser_comparison():
    initialize_session_state()
    
    # Sample alert toggle
    use_sample = st.checkbox("Use sample alert")
    
    if use_sample:
        sample_alert = """[F] is rerouted in Manhattan and Brooklyn
        Feb 3 - 7 and Feb 10 - 14, Mon to Fri, 9:30 PM to 5:00 AM
        No [F] service at 57 St, 47-50 Sts-Rockefeller Ctr, 42 St-Bryant Pk, 23 St, 14 St, W 4 St-Wash Sq, Broadway-Lafayette St, 2 Av, Delancey St-Essex St, East Broadway and York St.
        [F] runs via the [Q] between Lexington Av/63 St and 57 St-7 Av and via the [R] to/from 36 St in Brooklyn and via the [D] to/from Coney Island-Stillwell Av.
        [D runs via the [C] between 145 St and Jay St-MetroTechand replaces [F] service in Brooklyn to/from Coney Island-Stillwell Av.
        Free shuttle buses run between W 4 St-Wash Sq and East Broadway, stopping at Broadway-Lafayette St, 2 Av and Delancey St-Essex St.
        """
        alert_text = st.text_area("Alert text", value=sample_alert, height=150)
    else:
        alert_text = st.text_area("Enter alert text", height=150)

    # Buttons for each parser
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Run Regex Parser"):
            regex_parser = RegexParser()
            with st.spinner("Parsing with Regex..."):
                start_time = datetime.now()
                result = regex_parser.parse(alert_text)
                process_time = (datetime.now() - start_time).total_seconds()
                st.session_state.results['regex'] = {
                    'result': result,
                    'time': process_time
                }
    
    with col2:
        if st.button("Run GPT Parser"):
            gpt_parser = GPTParser()
            with st.spinner("Parsing with GPT..."):
                start_time = datetime.now()
                result = gpt_parser.parse(alert_text)
                process_time = (datetime.now() - start_time).total_seconds()
                st.session_state.results['gpt'] = {
                    'result': result,
                    'time': process_time
                }
    
    with col3:
        if st.button("Run Ollama Parser"):
            ollama_parser = OllamaParser()
            with st.spinner("Parsing with Ollama..."):
                start_time = datetime.now()
                result = ollama_parser.parse(alert_text)
                process_time = (datetime.now() - start_time).total_seconds()
                st.session_state.results['ollama'] = {
                    'result': result,
                    'time': process_time
                }
    
    # Display all results
    st.markdown("---")
    display_results()

def main():
    st.set_page_config(page_title="PS Parser", layout="wide")
    
    # Add sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Select Page",
            ["Parser Comparison", "PS Data Viewer"]
        )
    
    if page == "Parser Comparison":
        st.title("PS Parser Comparison")
        show_parser_comparison()
    else:
        st.title("PS Data Viewer")
        st.warning("Please navigate to the PS Data Viewer page using the pages dropdown in the sidebar.")

if __name__ == "__main__":
    main()