# utils/gtfs_comparator.py
from typing import Dict, Tuple

class GTFSComparator:
    def compare_route_patterns(self, 
                             regular_patterns: Dict, 
                             supplemented_patterns: Dict) -> Dict:
        """Compare patterns between regular and supplemented GTFS"""
        differences = {
            'direction_0': [],  # Northbound
            'direction_1': []   # Southbound
        }
        
        for direction in ['direction_0', 'direction_1']:
            reg_patterns = regular_patterns.get(direction, [])
            supp_patterns = supplemented_patterns.get(direction, [])
            
            # Compare each supplemented pattern with regular patterns
            for supp_pattern in supp_patterns:
                pattern_diff = {
                    'pattern_type': self._categorize_pattern_change(
                        reg_patterns[0]['stop_ids'],  # Using main pattern as reference
                        supp_pattern['stop_ids']
                    ),
                    'skipped_stops': [],
                    'added_stops': [],
                    'trips_affected': supp_pattern['count']
                }
                
                # Find skipped and added stops
                reg_stops = set(reg_patterns[0]['stop_ids'])
                supp_stops = set(supp_pattern['stop_ids'])
                
                pattern_diff['skipped_stops'] = list(reg_stops - supp_stops)
                pattern_diff['added_stops'] = list(supp_stops - reg_stops)
                
                if pattern_diff['pattern_type'] != 'normal':
                    differences[direction].append(pattern_diff)
        
        return differences
    
    def _categorize_pattern_change(self, 
                                 regular_stops: Tuple[str], 
                                 supplemented_stops: Tuple[str]) -> str:
        """Categorize the type of pattern change"""
        if regular_stops == supplemented_stops:
            return 'normal'
        
        # Check if it's just skipping stops
        if all(stop in regular_stops for stop in supplemented_stops):
            return 'skip_stops'
            
        # Check if it's running in sections
        if len(supplemented_stops) < len(regular_stops) * 0.5:
            return 'running_sections'
            
        # Must be rerouted
        return 'rerouted'