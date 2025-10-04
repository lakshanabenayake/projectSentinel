"""
Project Sentinel - Data Processing Module
Handles data correlation and validation algorithms
"""

from typing import Dict, Any, Set
from datetime import datetime

class DataProcessor:
    """Handles data processing and correlation logic"""
    
    def __init__(self):
        self.customer_sessions = {}  # customer_id -> session data
        self.station_states = {}     # station_id -> current state
        
    # @algorithm Data Correlation | Correlates RFID, POS, and product recognition data
    def correlate_customer_data(self, customer_id: str, dataset: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate data across different systems for a customer"""
        if customer_id not in self.customer_sessions:
            self.customer_sessions[customer_id] = {
                "rfid_items": set(),
                "scanned_items": set(),
                "recognized_items": set(),
                "total_weight": 0,
                "session_start": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
        
        session = self.customer_sessions[customer_id]
        session["last_activity"] = datetime.utcnow()
        
        correlation_result = {
            "customer_id": customer_id,
            "dataset": dataset,
            "anomalies": []
        }
        
        if dataset == "rfid_data":
            sku = data.get("sku")
            if sku:
                session["rfid_items"].add(sku)
                
        elif dataset == "pos_transactions":
            sku = data.get("sku")
            weight = data.get("weight_g", 0)
            if sku:
                session["scanned_items"].add(sku)
                session["total_weight"] += weight
                
                # Check if item was detected by RFID but not scanned (potential avoidance)
                if sku not in session["rfid_items"]:
                    correlation_result["anomalies"].append({
                        "type": "missing_rfid",
                        "sku": sku,
                        "description": "Item scanned but not detected by RFID"
                    })
                    
        elif dataset == "product_recognition":
            recognized_sku = data.get("predicted_product")
            if recognized_sku:
                session["recognized_items"].add(recognized_sku)
                
                # Check for barcode switching
                if session["scanned_items"]:
                    last_scanned = list(session["scanned_items"])[-1]
                    if recognized_sku != last_scanned:
                        correlation_result["anomalies"].append({
                            "type": "barcode_mismatch",
                            "recognized": recognized_sku,
                            "scanned": last_scanned,
                            "description": "Product recognition doesn't match scanned item"
                        })
        
        return correlation_result
    
    # @algorithm Weight Validation | Statistical analysis of weight discrepancies
    def validate_weight(self, expected: float, actual: float, tolerance: float = 50.0) -> Dict[str, Any]:
        """Validate weight with statistical analysis"""
        difference = abs(actual - expected)
        percentage_diff = (difference / expected * 100) if expected > 0 else 0
        
        result = {
            "expected": expected,
            "actual": actual,
            "difference": difference,
            "percentage_difference": percentage_diff,
            "is_valid": difference <= tolerance,
            "severity": "normal"
        }
        
        if difference > tolerance * 2:
            result["severity"] = "critical"
        elif difference > tolerance:
            result["severity"] = "warning"
            
        return result
    
    def cleanup_old_sessions(self, max_age_minutes: int = 30):
        """Clean up old customer sessions"""
        cutoff = datetime.utcnow().timestamp() - (max_age_minutes * 60)
        expired_customers = [
            cid for cid, session in self.customer_sessions.items()
            if session["last_activity"].timestamp() < cutoff
        ]
        
        for customer_id in expired_customers:
            del self.customer_sessions[customer_id]
            
        return len(expired_customers)
    
    def get_session_summary(self, customer_id: str) -> Dict[str, Any]:
        """Get summary of customer session"""
        if customer_id not in self.customer_sessions:
            return {"error": "Session not found"}
            
        session = self.customer_sessions[customer_id]
        
        return {
            "customer_id": customer_id,
            "session_duration": (datetime.utcnow() - session["session_start"]).total_seconds(),
            "rfid_items_count": len(session["rfid_items"]),
            "scanned_items_count": len(session["scanned_items"]),
            "recognized_items_count": len(session["recognized_items"]),
            "total_weight": session["total_weight"],
            "potential_issues": len(session["rfid_items"] - session["scanned_items"])
        }