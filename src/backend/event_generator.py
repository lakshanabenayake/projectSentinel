"""
Project Sentinel - Event Generator Module
Standardized event creation and formatting
"""

import json
from datetime import datetime
from typing import Dict, Any, List
import os

class EventGenerator:
    """Handles standardized event creation and output formatting"""
    
    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = output_dir
        self.event_counter = 0
        self.event_categories = {
            "security": ["Scanner Avoidance", "Barcode Switching", "Unexpected Systems Crash"],
            "operational": ["Long Queue Length", "Long Wait Time", "Staffing Needs", "Checkout Station Action"],
            "inventory": ["Inventory Discrepancy", "Weight Discrepancies"],
            "success": ["Success Operation"]
        }
        
    # @algorithm Event Formatting | Standardizes event structure and metadata
    def create_standardized_event(self, event_name: str, data: Dict[str, Any], 
                                priority: str = "info", category: str = None) -> Dict[str, Any]:
        """Create a standardized event with proper formatting"""
        self.event_counter += 1
        event_id = f"E{self.event_counter:03d}"
        
        # Auto-detect category if not provided
        if not category:
            category = self._detect_category(event_name)
        
        # Create standardized event structure
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_id": event_id,
            "event_data": {
                "event_name": event_name,
                **data
            },
            "metadata": {
                "priority": priority,
                "category": category,
                "processed_at": datetime.utcnow().isoformat(),
                "source": "project_sentinel_detector"
            }
        }
        
        return event
    
    def write_event_to_file(self, event: Dict[str, Any], filename: str = "events.jsonl"):
        """Write event to JSONL file"""
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    
    def create_batch_events(self, events_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple events in batch"""
        events = []
        for event_data in events_data:
            event = self.create_standardized_event(
                event_data.get("event_name"),
                event_data.get("data", {}),
                event_data.get("priority", "info"),
                event_data.get("category")
            )
            events.append(event)
        return events
    
    def _detect_category(self, event_name: str) -> str:
        """Auto-detect event category based on event name"""
        for category, event_names in self.event_categories.items():
            if event_name in event_names:
                return category
        return "general"
    
    def get_event_summary(self) -> Dict[str, Any]:
        """Get summary of generated events"""
        return {
            "total_events": self.event_counter,
            "output_directory": self.output_dir,
            "categories": self.event_categories
        }
    
    def reset_counter(self):
        """Reset event counter"""
        self.event_counter = 0