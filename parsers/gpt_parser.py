# parsers/gpt_parser.py
import streamlit as st
from typing import Dict
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

class GPTParser:
    def __init__(self):
        load_dotenv()
        try:
        # First try to get API key from Streamlit secrets
            api_key = st.secrets["OPENAI_API_KEY"]
        except (KeyError, AttributeError):
        # If not in Streamlit or key not in secrets, try environment variable
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found! Please check your .env file or Streamlit secrets")
        self.client = OpenAI(api_key=api_key)
    
    def parse(self, text: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Using GPT-4
                messages=[{
                    "role": "system",
                    "content": """You are a specialized MTA subway alert parser. Your task is to:
                    1. Identify ALL affected subway lines (both explicit [X] mentions and implicit mentions in descriptions)
                    2. Extract service changes including:
                       - Service suspensions and their locations
                       - Reroutes and alternate service
                       - Skip-stop patterns
                       - Running sections
                    
                    Respond in this exact JSON format:
                    {
                        "affected_lines": ["A", "B"],  // all impacted lines
                        "service_changes": {
                            "suspensions": [{"line": "A", "from": "station1", "to": "station2"}],
                            "reroutes": [{"line": "A", "detail": "reroute info"}],
                            "alternate_service": [{"line": "B", "detail": "alternate service info"}]
                        }
                    }"""
                }, {
                    "role": "user",
                    "content": f"Parse this MTA alert:\n\n{text}"
                }]
            )
            
            result = json.loads(response.choices[0].message.content)
            result["method"] = "gpt4"
            return result
            
        except json.JSONDecodeError as e:
            return {
                "error": f"JSON parsing error: {str(e)}",
                "method": "gpt4",
                "affected_lines": [],
                "service_changes": {}
            }
        except Exception as e:
            return {
                "error": str(e),
                "method": "gpt4",
                "affected_lines": [],
                "service_changes": {}
            }