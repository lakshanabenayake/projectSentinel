"""
Event Generation Module for Project Sentinel
Handles event formatting and JSONL output generation
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import os

class EventGenerator:
    """Manages event collection and export to JSONL format"""
    
    def __init__(self):
        self.events = []
        self.event_counter = 0
    
    def add_event(self, event_data: Dict[str, Any]) -> str:
        """
        Add a new event to the collection
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Generated event ID
        """
        # Ensure proper event format
        formatted_event = {
            'timestamp': event_data.get('timestamp', datetime.now().isoformat()),
            'event_id': event_data.get('event_id', f"E{self.event_counter:03d}"),
            'event_data': event_data.get('event_data', event_data)
        }
        
        self.events.append(formatted_event)
        self.event_counter += 1
        
        return formatted_event['event_id']
    
    def get_events(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get events with optional limit"""
        if limit:
            return self.events[-limit:]
        return self.events
    
    def clear_events(self):
        """Clear all events from memory"""
        self.events = []
        self.event_counter = 0
    
    # @algorithm Event Formatting | Standardizes event output format for JSONL export
    def export_to_file(self, output_path: str) -> Dict[str, Any]:
        """
        Export events to JSONL file format
        
        Args:
            output_path: Path to output file
            
        Returns:
            Export status and statistics
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                for event in self.events:
                    f.write(json.dumps(event) + '\n')
            
            return {
                'status': 'success',
                'file_path': output_path,
                'events_exported': len(self.events),
                'file_size_bytes': os.path.getsize(output_path) if os.path.exists(output_path) else 0
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error_message': str(e),
                'events_exported': 0
            }
    
    def generate_sample_events(self) -> List[Dict[str, Any]]:
        """Generate sample events for testing"""
        sample_events = [
            {
                'timestamp': datetime.now().isoformat(),
                'event_id': 'E001',
                'event_data': {
                    'event_name': 'Scanner Avoidance',
                    'station_id': 'SCC1',
                    'customer_id': 'C001',
                    'product_sku': 'PRD_F_01'
                }
            },
            {
                'timestamp': datetime.now().isoformat(),
                'event_id': 'E002',
                'event_data': {
                    'event_name': 'Weight Discrepancies',
                    'station_id': 'SCC1',
                    'customer_id': 'C002',
                    'product_sku': 'PRD_F_02',
                    'expected_weight': 150,
                    'actual_weight': 200
                }
            },
            {
                'timestamp': datetime.now().isoformat(),
                'event_id': 'E003',
                'event_data': {
                    'event_name': 'Long Queue Length',
                    'station_id': 'SCC2',
                    'customer_count': 8
                }
            }
        ]
        
        for event in sample_events:
            self.add_event(event)
        
        return sample_events
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about collected events"""
        if not self.events:
            return {
                'total_events': 0,
                'event_types': {},
                'stations': {},
                'time_range': None
            }
        
        # Count events by type
        event_types = {}
        stations = {}
        timestamps = []
        
        for event in self.events:
            event_data = event.get('event_data', {})
            event_name = event_data.get('event_name', 'Unknown')
            station_id = event_data.get('station_id', 'Unknown')
            
            event_types[event_name] = event_types.get(event_name, 0) + 1
            stations[station_id] = stations.get(station_id, 0) + 1
            timestamps.append(event.get('timestamp'))
        
        timestamps = [ts for ts in timestamps if ts]
        time_range = None
        if timestamps:
            time_range = {
                'start': min(timestamps),
                'end': max(timestamps)
            }
        
        return {
            'total_events': len(self.events),
            'event_types': event_types,
            'stations': stations,
            'time_range': time_range
        }