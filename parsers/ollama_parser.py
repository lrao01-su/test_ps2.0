# parsers/ollama_parser.py
import ollama
from typing import Dict
import json

class OllamaParser:
    def __init__(self):
        self.model = 'mistral'
    
    def parse(self, text: str) -> Dict:
        try:
            prompt = f"""
            You are a specialized MTA subway alert parser. Parse this alert and extract information in a specific JSON structure.
            Focus on these key elements:
            1. All affected subway lines (both from [X] brackets and text mentions)
            2. Station names involved
            3. Type of service change
            4. Time periods
            5. Description of changes

            Alert text:
            {text}

            Return ONLY valid JSON with this exact structure (no explanation, only JSON):
            {{
                "parsed_alert": {{
                    "affected_lines": [],
                    "service_type": "",
                    "locations": {{
                        "stations": [],
                        "stops_added": [],
                        "stops_skipped": []
                    }},
                    "time_periods": {{
                        "summary": "",
                        "type": ""
                    }},
                    "changes": {{
                        "type": "",
                        "description": ""
                    }}
                }},
                "method": "ollama_mistral"
            }}
            """
            
            response = ollama.generate(
                model=self.model,
                prompt=prompt
            )
            
            result = json.loads(response['response'])
            return result
        except json.JSONDecodeError as e:
            return {
                "error": f"JSON parsing error: {str(e)}",
                "method": "ollama_mistral"
            }
        except Exception as e:
            return {
                "error": str(e),
                "method": "ollama_mistral"
            }