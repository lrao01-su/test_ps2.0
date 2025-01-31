# parsers/gtfs_parser.py
from typing import Dict
import pandas as pd

class GTFSParser:
    def __init__(self):
        # Define main routes and their variants
        self.route_groups = {
            '5': ['5', '5X'],
            '6': ['6', '6X'],
            '7': ['7', '7X'],
            'F': ['F', 'FX'],
            'S': ['FS', 'GS', 'H'],  # All shuttle services
            'J': ['J', 'Z'],  # Group J/Z since they're related
        }
        
        # All possible route IDs
        self.all_routes = [
            '1', '2', '3', '4', '5', '5X', '6', '6X', '7', '7X',
            'A', 'B', 'C', 'D', 'E', 'F', 'FX', 'G', 
            'J', 'Z', 'L', 'M', 'N', 'Q', 'R', 'W',
            'FS', 'GS', 'H'  # Shuttles
        ]

    def get_route_patterns(self, gtfs_data: Dict[str, pd.DataFrame], route_id: str, include_variants: bool = True) -> Dict:
        """Extract patterns for a route and its variants"""
        # Determine which route IDs to include
        routes_to_check = [route_id]
        if include_variants:
            # Add variants if they exist
            for group, variants in self.route_groups.items():
                if route_id in variants:
                    routes_to_check = variants
                    break
        
        patterns = {
            'direction_0': [],  # Northbound/Uptown
            'direction_1': []   # Southbound/Downtown
        }
        
        for r_id in routes_to_check:
            route_trips = gtfs_data['trips'][gtfs_data['trips']['route_id'].isin([r_id])]
            
            # Process patterns for each direction
            for direction in [0, 1]:
                direction_trips = route_trips[route_trips['direction_id'] == direction]
                if not direction_trips.empty:
                    for trip_id in direction_trips['trip_id']:
                        stops = self._get_stop_sequence(gtfs_data, trip_id)
                        if stops is not None:
                            patterns[f'direction_{direction}'].append({
                                'route_id': r_id,
                                'stop_sequence': stops,
                                'trip_id': trip_id
                            })
        
        return patterns

    def _get_stop_sequence(self, gtfs_data: Dict[str, pd.DataFrame], trip_id: str) -> pd.DataFrame:
        """Get the stop sequence for a specific trip"""
        stops = gtfs_data['stop_times'][
            gtfs_data['stop_times']['trip_id'] == trip_id
        ].sort_values('stop_sequence')[['stop_id', 'stop_sequence']]
        
        if not stops.empty:
            # Add stop names
            stops = stops.merge(
                gtfs_data['stops'][['stop_id', 'stop_name']],
                on='stop_id',
                how='left'
            )
            return stops
        return None