#!/usr/bin/env python3
"""
Project Sentinel - Enhanced Event Detection Engine
Based on serve1.py reference implementation with proper state management and detection logic
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Set, Optional

class SentinelDetector:
    """Enhanced event detection engine matching serve1.py logic"""
    
    def __init__(self):
        # State stores matching serve1.py
        self.seen_rfids = {}            # customer_id -> set of SKUs detected by RFID
        self.scanned_items = {}         # customer_id -> set of SKUs scanned at POS
        self.expected_weights = {}      # customer_id -> total expected weight
        self.inventory_snapshot = {}    # SKU -> expected inventory
        self.event_counter = 0
        
        # Output configuration
        self.output_file = "evidence/output/final/events.json"
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """Ensure output directory exists"""
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
    
    def write_event(self, event_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Write event to JSONL file with proper format"""
        self.event_counter += 1
        event_id = f"E{self.event_counter:03d}"
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_id": event_id,
            "event_data": {"event_name": event_name, **data}
        }
        
        # Append to JSONL file
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
        
        # Also print to console for debugging
        print(f"📢 DETECTED: {event_name} -> {json.dumps(event, indent=2)}")
        
        return event
    
    def detect(self, streaming_event: dict) -> Optional[Dict[str, Any]]:
        """
        Main detection logic based on serve1.py
        
        Args:
            streaming_event: Raw event from stream server
            
        Returns:
            Detected event or None
        """
        dataset = streaming_event.get("dataset", "")
        dataset_lower = dataset.lower().replace("_", "")  # Normalize dataset names
        ev = streaming_event.get("event", {})
        status = ev.get("status")
        station = ev.get("station_id", "UNKNOWN")
        
        # Extract customer_id from nested data object (POS transactions)
        # or fallback to event level (for other datasets)
        data = ev.get("data", {})
        cust = data.get("customer_id") or ev.get("customer_id", "UNKNOWN")
        
        detected_event = None
        
        # 1. RFID Data Processing
        # Handles: RFID_data, rfid_readings, rfid_data
        if "rfid" in dataset_lower and status == "Active":
            detected_event = self._process_rfid_data(ev, station, cust)
        
        # 2. POS Transactions
        # Handles: POS_Transactions, pos_transactions
        elif "pos" in dataset_lower or "transaction" in dataset_lower:
            detected_event = self._process_pos_transaction(ev, station, cust, status)
        
        # 3. Product Recognition -> Barcode Switching
        # Handles: Product_recognism, product_recognition
        elif ("product" in dataset_lower and "recogni" in dataset_lower) and status == "Active":
            detected_event = self._process_product_recognition(ev, station, cust)
        
        # 4. Queue Monitoring
        # Handles: Queue_monitor, queue_monitoring
        elif "queue" in dataset_lower and status == "Active":
            detected_event = self._process_queue_monitoring(ev, station, cust)
        
        # 5. Inventory Snapshots
        # Handles: Current_inventory_data, inventory_snapshots
        elif "inventory" in dataset_lower and status == "Active":
            detected_event = self._process_inventory_snapshot(ev, station)
        
        # 6. Staffing Needs
        elif "staffing" in dataset_lower and status == "Active":
            detected_event = self._process_staffing(ev, station)
        
        # 7. Checkout Station Action
        elif "checkout" in dataset_lower and status == "Active":
            detected_event = self._process_checkout_action(ev, station)
        
        # 8. Check for Scanner Avoidance (runs after any event)
        self._check_scanner_avoidance(station)
        
        return detected_event
    
    def _process_rfid_data(self, ev: Dict, station: str, cust: str) -> Optional[Dict]:
        """Process RFID data and track seen items"""
        sku = ev.get("data", {}).get("sku")
        if sku:
            self.seen_rfids.setdefault(cust, set()).add(sku)
            print(f"🔖 RFID detected: Customer {cust} has SKU {sku}")
        return None
    
    def _process_pos_transaction(self, ev: Dict, station: str, cust: str, status: str) -> Optional[Dict]:
        """Process POS transactions and detect various events"""
        data = ev.get("data", {})
        sku = data.get("sku")
        weight = data.get("weight_g", 0)
        
        if sku:
            self.scanned_items.setdefault(cust, set()).add(sku)
            self.expected_weights[cust] = self.expected_weights.get(cust, 0) + weight
        
        # Check for system crash
        if status == "System Crash":
            return self.write_event("Unexpected Systems Crash", {
                "station_id": station,
                "duration_seconds": 180
            })
        
        # Check for success operation (RFID matches POS scan)
        if sku and sku in self.seen_rfids.get(cust, set()):
            self.seen_rfids[cust].discard(sku)  # Remove from RFID set
            return self.write_event("Succes Operation", {  # Note: matches expected typo
                "station_id": station,
                "customer_id": cust,
                "product_sku": sku
            })
        
        # Check for weight discrepancies
        actual_weight = data.get("weight_g")
        expected_weight = data.get("price")  # Using price as proxy for expected weight
        if actual_weight and expected_weight and abs(actual_weight - expected_weight) > 50:
            return self.write_event("Weight Discrepancies", {
                "station_id": station,
                "customer_id": cust,
                "product_sku": sku,
                "expected_weight": expected_weight,
                "actual_weight": actual_weight
            })
        
        return None
    
    def _process_product_recognition(self, ev: Dict, station: str, cust: str) -> Optional[Dict]:
        """Process product recognition and detect barcode switching"""
        data = ev.get("data", {})
        predicted_sku = data.get("predicted_product")
        
        # Get last scanned item for this customer
        last_scanned = None
        if cust in self.scanned_items and self.scanned_items[cust]:
            last_scanned = list(self.scanned_items[cust])[-1]
        
        if predicted_sku and last_scanned and predicted_sku != last_scanned:
            return self.write_event("Barcode Switching", {
                "station_id": station,
                "customer_id": cust,
                "actual_sku": predicted_sku,
                "scanned_sku": last_scanned
            })
        
        return None
    
    def _process_queue_monitoring(self, ev: Dict, station: str, cust: str) -> Optional[Dict]:
        """Process queue monitoring for long queues and wait times"""
        data = ev.get("data", {})
        customer_count = data.get("customer_count", 0)
        dwell = data.get("average_dwell_time", 0)
        
        # Check for long queue
        if customer_count >= 6:
            return self.write_event("Long Queue Length", {
                "station_id": station,
                "num_of_customers": customer_count
            })
        
        # Check for long wait time
        if dwell >= 300:
            return self.write_event("Long Wait Time", {
                "station_id": station,
                "customer_id": cust,
                "wait_time_seconds": dwell
            })
        
        return None
    
    def _process_inventory_snapshot(self, ev: Dict, station: str) -> Optional[Dict]:
        """Process inventory snapshots and detect discrepancies"""
        data = ev.get("data", {})
        
        for sku, qty in data.items():
            if sku in self.inventory_snapshot and qty != self.inventory_snapshot[sku]:
                event = self.write_event("Inventory Discrepancy", {
                    "SKU": sku,
                    "Expected_Inventory": self.inventory_snapshot[sku],
                    "Actual_Inventory": qty
                })
                self.inventory_snapshot[sku] = qty
                return event
            self.inventory_snapshot[sku] = qty
        
        return None
    
    def _process_staffing(self, ev: Dict, station: str) -> Optional[Dict]:
        """Process staffing events"""
        data = ev.get("data", {})
        return self.write_event("Staffing Needs", {
            "station_id": station,
            "Staff_type": data.get("Staff_type", "UNKNOWN")
        })
    
    def _process_checkout_action(self, ev: Dict, station: str) -> Optional[Dict]:
        """Process checkout station actions"""
        data = ev.get("data", {})
        return self.write_event("Checkout Station Action", {
            "station_id": station,
            "Action": data.get("Action", "Open")
        })
    
    def _check_scanner_avoidance(self, station: str):
        """Check for scanner avoidance across all customers"""
        for cust_id, rfids in list(self.seen_rfids.items()):
            scanned = self.scanned_items.get(cust_id, set())
            missing = rfids - scanned
            
            if missing:
                for sku in missing:
                    self.write_event("Scanner Avoidance", {
                        "station_id": station,
                        "customer_id": cust_id,
                        "product_sku": sku
                    })
                # Clear processed RFIDs
                self.seen_rfids[cust_id].clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current detection statistics"""
        return {
            "events_detected": self.event_counter,
            "customers_with_rfid": len(self.seen_rfids),
            "customers_with_scans": len(self.scanned_items),
            "inventory_items_tracked": len(self.inventory_snapshot),
            "output_file": self.output_file
        }
    
    def reset_state(self):
        """Reset all detection state"""
        self.seen_rfids.clear()
        self.scanned_items.clear()
        self.expected_weights.clear()
        self.inventory_snapshot.clear()
        self.event_counter = 0