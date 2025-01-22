# parsers/regex_parser.py
import re
from typing import Dict

class RegexParser:
    def parse(self, text: str) -> Dict:
        # Extract lines mentioned in brackets
        lines = re.findall(r'\[([A-Z])\]', text)
        
        # Extract service patterns (basic version)
        no_service = re.findall(r'No\s+([A-Z])\s+service\s+between\s+(.*?)\s+and\s+(.*?)(?:\n|$)', text)
        reroutes = re.findall(r'([A-Z])\s+trains\s+rerouted', text)
        
        return {
            "affected_lines": list(set(lines)),
            "service_changes": {
                "suspensions": no_service,
                "reroutes": reroutes
            },
            "method": "regex"
        }