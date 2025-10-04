"""
Project Sentinel - Anomaly Detection Module
Advanced algorithms for detecting retail anomalies and suspicious activities
"""

from typing import Dict, Any, List, Set
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, deque

class AnomalyDetector:
    """Advanced anomaly detection algorithms"""
    
    def __init__(self):
        self.baseline_metrics = {}
        self.historical_data = defaultdict(deque)  # Store recent data for pattern analysis
        self.alert_thresholds = {
            "queue_length": 5,
            "wait_time": 300,  # 5 minutes
            "weight_tolerance": 50,  # grams
            "scan_rate_threshold": 0.8  # 80% scan rate expected
        }
    
    # @algorithm Scanner Avoidance Detection | Advanced pattern analysis for theft detection
    def detect_scanner_avoidance_patterns(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced scanner avoidance detection with pattern analysis"""
        customer_id = customer_data.get("customer_id")
        rfid_items = customer_data.get("rfid_items", set())
        scanned_items = customer_data.get("scanned_items", set())
        
        # Calculate scan rate
        total_items = len(rfid_items)
        scanned_count = len(scanned_items)
        scan_rate = scanned_count / total_items if total_items > 0 else 1.0
        
        # Identify unscanned items
        unscanned_items = rfid_items - scanned_items
        
        # Behavioral pattern analysis
        patterns = {
            "low_scan_rate": scan_rate < self.alert_thresholds["scan_rate_threshold"],
            "selective_avoidance": len(unscanned_items) > 0 and scan_rate > 0.5,  # Some scanned, some avoided
            "complete_avoidance": scan_rate == 0 and total_items > 0,
            "high_value_avoidance": False  # Would need product pricing data
        }
        
        # Risk scoring
        risk_score = 0
        if patterns["complete_avoidance"]:
            risk_score += 10
        elif patterns["low_scan_rate"]:
            risk_score += 7
        elif patterns["selective_avoidance"]:
            risk_score += 5
            
        risk_score += min(len(unscanned_items) * 2, 10)  # Max 10 points for item count
        
        return {
            "customer_id": customer_id,
            "scan_rate": scan_rate,
            "unscanned_items": list(unscanned_items),
            "unscanned_count": len(unscanned_items),
            "patterns_detected": patterns,
            "risk_score": risk_score,
            "alert_level": self._get_alert_level(risk_score),
            "recommendation": self._get_avoidance_recommendation(patterns, risk_score)
        }
    
    # @algorithm Barcode Switching Detection | ML-based product recognition validation
    def detect_barcode_switching(self, transaction_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect barcode switching using product recognition validation"""
        anomalies = []
        
        for transaction in transaction_data:
            scanned_sku = transaction.get("scanned_sku")
            recognized_sku = transaction.get("recognized_sku")
            confidence = transaction.get("recognition_confidence", 0.0)
            
            if scanned_sku and recognized_sku and scanned_sku != recognized_sku:
                # Analyze switching patterns
                switch_analysis = {
                    "transaction_id": transaction.get("transaction_id"),
                    "customer_id": transaction.get("customer_id"),
                    "station_id": transaction.get("station_id"),
                    "scanned_sku": scanned_sku,
                    "recognized_sku": recognized_sku,
                    "confidence": confidence,
                    "timestamp": transaction.get("timestamp")
                }
                
                # Calculate suspicion level
                suspicion_level = "low"
                if confidence > 0.9:
                    suspicion_level = "high"
                elif confidence > 0.7:
                    suspicion_level = "medium"
                
                switch_analysis["suspicion_level"] = suspicion_level
                switch_analysis["recommended_action"] = self._get_switching_action(suspicion_level, confidence)
                
                anomalies.append(switch_analysis)
        
        return anomalies
    
    # @algorithm Queue Analysis | Predictive queue management and optimization
    def analyze_queue_patterns(self, queue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced queue analysis with predictive modeling"""
        station_id = queue_data.get("station_id")
        customer_count = queue_data.get("customer_count", 0)
        average_dwell = queue_data.get("average_dwell_time", 0)
        timestamp = datetime.fromisoformat(queue_data.get("timestamp", datetime.utcnow().isoformat()))
        
        # Store historical data
        self.historical_data[f"queue_{station_id}"].append({
            "timestamp": timestamp,
            "customer_count": customer_count,
            "dwell_time": average_dwell
        })
        
        # Keep only last 100 data points
        if len(self.historical_data[f"queue_{station_id}"]) > 100:
            self.historical_data[f"queue_{station_id}"].popleft()
        
        # Calculate trends
        recent_data = list(self.historical_data[f"queue_{station_id}"])
        if len(recent_data) >= 10:
            recent_counts = [d["customer_count"] for d in recent_data[-10:]]
            recent_dwell = [d["dwell_time"] for d in recent_data[-10:]]
            
            avg_count = statistics.mean(recent_counts)
            avg_dwell = statistics.mean(recent_dwell)
            
            # Trend analysis
            count_trend = "stable"
            dwell_trend = "stable"
            
            if len(recent_counts) >= 5:
                first_half_count = statistics.mean(recent_counts[:5])
                second_half_count = statistics.mean(recent_counts[5:])
                
                if second_half_count > first_half_count * 1.2:
                    count_trend = "increasing"
                elif second_half_count < first_half_count * 0.8:
                    count_trend = "decreasing"
            
            if len(recent_dwell) >= 5:
                first_half_dwell = statistics.mean(recent_dwell[:5])
                second_half_dwell = statistics.mean(recent_dwell[5:])
                
                if second_half_dwell > first_half_dwell * 1.2:
                    dwell_trend = "increasing"
                elif second_half_dwell < first_half_dwell * 0.8:
                    dwell_trend = "decreasing"
        else:
            avg_count = customer_count
            avg_dwell = average_dwell
            count_trend = "insufficient_data"
            dwell_trend = "insufficient_data"
        
        # Generate alerts and recommendations
        alerts = []
        recommendations = []
        
        if customer_count >= self.alert_thresholds["queue_length"]:
            alerts.append({
                "type": "long_queue",
                "severity": "warning",
                "message": f"Queue length ({customer_count}) exceeds threshold"
            })
            recommendations.append("Consider opening additional checkout lanes")
        
        if average_dwell >= self.alert_thresholds["wait_time"]:
            alerts.append({
                "type": "long_wait_time",
                "severity": "warning", 
                "message": f"Wait time ({average_dwell}s) exceeds threshold"
            })
            recommendations.append("Deploy additional staff to reduce wait times")
        
        if count_trend == "increasing" and dwell_trend == "increasing":
            recommendations.append("Queue congestion building - take immediate action")
        
        return {
            "station_id": station_id,
            "current_metrics": {
                "customer_count": customer_count,
                "average_dwell_time": average_dwell
            },
            "trends": {
                "customer_count_trend": count_trend,
                "dwell_time_trend": dwell_trend,
                "average_count": avg_count,
                "average_dwell": avg_dwell
            },
            "alerts": alerts,
            "recommendations": recommendations,
            "efficiency_score": self._calculate_efficiency_score(customer_count, average_dwell)
        }
    
    # @algorithm Product Recognition Validation | Computer vision validation algorithms
    def validate_product_recognition(self, recognition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product recognition against known patterns"""
        predicted_product = recognition_data.get("predicted_product")
        confidence = recognition_data.get("confidence", 0.0)
        image_quality = recognition_data.get("image_quality", "unknown")
        
        validation_result = {
            "predicted_product": predicted_product,
            "confidence": confidence,
            "image_quality": image_quality,
            "validation_status": "valid",
            "confidence_level": "high",
            "recommendations": []
        }
        
        # Confidence thresholds
        if confidence < 0.5:
            validation_result["validation_status"] = "low_confidence"
            validation_result["confidence_level"] = "low"
            validation_result["recommendations"].append("Manual verification required")
        elif confidence < 0.7:
            validation_result["confidence_level"] = "medium"
            validation_result["recommendations"].append("Consider secondary validation")
        
        # Image quality assessment
        if image_quality == "poor":
            validation_result["recommendations"].append("Improve lighting or camera angle")
        
        return validation_result
    
    def _get_alert_level(self, risk_score: int) -> str:
        """Convert risk score to alert level"""
        if risk_score >= 15:
            return "critical"
        elif risk_score >= 8:
            return "warning"
        else:
            return "info"
    
    def _get_avoidance_recommendation(self, patterns: Dict[str, bool], risk_score: int) -> str:
        """Get recommendation based on avoidance patterns"""
        if patterns["complete_avoidance"]:
            return "Immediate intervention required - possible theft attempt"
        elif patterns["low_scan_rate"]:
            return "Monitor customer closely - multiple unscanned items"
        elif patterns["selective_avoidance"]:
            return "Verify unscanned items - possible oversight or intentional avoidance"
        else:
            return "Normal scanning behavior detected"
    
    def _get_switching_action(self, suspicion_level: str, confidence: float) -> str:
        """Get recommended action for barcode switching"""
        if suspicion_level == "high":
            return "Alert security - high confidence product mismatch"
        elif suspicion_level == "medium":
            return "Staff verification recommended"
        else:
            return "Monitor - low confidence detection"
    
    def _calculate_efficiency_score(self, customer_count: int, dwell_time: float) -> float:
        """Calculate station efficiency score (0-100)"""
        # Base score starts at 100
        score = 100.0
        
        # Deduct points for long queues
        if customer_count > 5:
            score -= (customer_count - 5) * 5
        
        # Deduct points for long wait times
        if dwell_time > 180:  # 3 minutes
            score -= ((dwell_time - 180) / 60) * 10  # 10 points per additional minute
        
        return max(0.0, min(100.0, score))