"""
Anomaly Detection Module for Project Sentinel
Implements algorithms to detect retail security and operational issues
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from data_processor import DataProcessor

class AnomalyDetector:
    """Main anomaly detection engine for retail surveillance"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.event_cache = {}
        self.detection_thresholds = {
            'weight_tolerance': 0.15,  # 15% weight deviation
            'queue_length_threshold': 5,  # Max customers per station
            'wait_time_threshold': 120,  # Max wait time in seconds
            'accuracy_threshold': 0.8,  # Min product recognition accuracy
        }
    
    def process_event(self, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process incoming event and detect anomalies
        
        Args:
            event_data: Streaming event data
            
        Returns:
            List of detected anomaly events
        """
        detected_events = []
        
        dataset = event_data.get('dataset')
        event_content = event_data.get('event', {})
        station_id = event_content.get('station_id')
        timestamp = event_data.get('timestamp')
        
        if not station_id or not timestamp:
            return detected_events
        
        # Cache event for correlation analysis
        self._cache_event(station_id, dataset, event_content, timestamp)
        
        # Run detection algorithms based on data type
        if dataset == 'POS_Transactions':
            detected_events.extend(self._detect_pos_anomalies(station_id, event_content, timestamp))
        elif dataset == 'RFID_data':
            detected_events.extend(self._detect_rfid_anomalies(station_id, event_content, timestamp))
        elif dataset == 'Queue_monitor':
            detected_events.extend(self._detect_queue_anomalies(station_id, event_content, timestamp))
        elif dataset == 'Product_recognism':
            detected_events.extend(self._detect_recognition_anomalies(station_id, event_content, timestamp))
        
        # Cross-stream correlation detection
        detected_events.extend(self._detect_cross_stream_anomalies(station_id, timestamp))
        
        return detected_events
    
    def _cache_event(self, station_id: str, dataset: str, event: Dict, timestamp: str):
        """Cache event for correlation analysis"""
        if station_id not in self.event_cache:
            self.event_cache[station_id] = {}
        if dataset not in self.event_cache[station_id]:
            self.event_cache[station_id][dataset] = []
            
        # Keep only recent events (last 60 seconds)
        cutoff_time = datetime.fromisoformat(timestamp) - timedelta(seconds=60)
        
        # Add new event
        self.event_cache[station_id][dataset].append({
            'timestamp': timestamp,
            'data': event
        })
        
        # Remove old events
        self.event_cache[station_id][dataset] = [
            e for e in self.event_cache[station_id][dataset]
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
        ]
    
    # @algorithm Scanner Avoidance Detection | Detects items in RFID but missing from POS transactions
    def _detect_pos_anomalies(self, station_id: str, pos_event: Dict, timestamp: str) -> List[Dict]:
        """Detect POS-related anomalies"""
        detected = []
        
        # Get product data
        sku = pos_event.get('data', {}).get('sku')
        weight = pos_event.get('data', {}).get('weight_g', 0)
        customer_id = pos_event.get('data', {}).get('customer_id')
        
        if not sku:
            return detected
        
        # Check for weight discrepancies
        product_info = self.data_processor.get_product_info(sku)
        if product_info and weight > 0:
            expected_weight = product_info.get('weight', 0)
            if expected_weight > 0:
                deviation = abs(weight - expected_weight) / expected_weight
                if deviation > self.detection_thresholds['weight_tolerance']:
                    detected.append({
                        'timestamp': timestamp,
                        'event_id': f"WD_{int(datetime.now().timestamp())}",
                        'event_data': {
                            'event_name': 'Weight Discrepancies',
                            'station_id': station_id,
                            'customer_id': customer_id,
                            'product_sku': sku,
                            'expected_weight': expected_weight,
                            'actual_weight': weight,
                            'deviation_percent': round(deviation * 100, 2)
                        }
                    })
        
        return detected
    
    # @algorithm Barcode Switching Detection | Validates RFID EPC against scanned barcode for fraud detection
    def _detect_rfid_anomalies(self, station_id: str, rfid_event: Dict, timestamp: str) -> List[Dict]:
        """Detect RFID-related anomalies"""
        detected = []
        
        epc = rfid_event.get('data', {}).get('epc')
        sku = rfid_event.get('data', {}).get('sku') 
        location = rfid_event.get('data', {}).get('location')
        
        if not epc or not sku:
            return detected
        
        # Validate EPC to SKU mapping
        if not self.data_processor.validate_epc_to_sku(epc, sku):
            detected.append({
                'timestamp': timestamp,
                'event_id': f"BS_{int(datetime.now().timestamp())}",
                'event_data': {
                    'event_name': 'Barcode Switching',
                    'station_id': station_id,
                    'epc': epc,
                    'claimed_sku': sku,
                    'location': location
                }
            })
        
        # Check for scanner avoidance (RFID detected but no recent POS)
        if location == 'IN_SCAN_AREA':
            recent_pos = self._get_recent_events(station_id, 'POS_Transactions', 10)
            pos_skus = [e['data'].get('data', {}).get('sku') for e in recent_pos]
            
            if sku not in pos_skus:
                detected.append({
                    'timestamp': timestamp,
                    'event_id': f"SA_{int(datetime.now().timestamp())}",
                    'event_data': {
                        'event_name': 'Scanner Avoidance',
                        'station_id': station_id,
                        'product_sku': sku,
                        'epc': epc,
                        'detection_method': 'RFID without POS'
                    }
                })
        
        return detected
    
    # @algorithm Queue Analysis | Monitors customer queue length and wait times for optimization
    def _detect_queue_anomalies(self, station_id: str, queue_event: Dict, timestamp: str) -> List[Dict]:
        """Detect queue-related issues"""
        detected = []
        
        customer_count = queue_event.get('data', {}).get('customer_count', 0)
        avg_dwell_time = queue_event.get('data', {}).get('average_dwell_time', 0)
        
        # Long queue detection
        if customer_count > self.detection_thresholds['queue_length_threshold']:
            detected.append({
                'timestamp': timestamp,
                'event_id': f"LQ_{int(datetime.now().timestamp())}",
                'event_data': {
                    'event_name': 'Long Queue Length',
                    'station_id': station_id,
                    'customer_count': customer_count,
                    'threshold': self.detection_thresholds['queue_length_threshold']
                }
            })
            
            # Recommend staffing action
            detected.append({
                'timestamp': timestamp,
                'event_id': f"SN_{int(datetime.now().timestamp())}",
                'event_data': {
                    'event_name': 'Staffing Needs',
                    'station_id': station_id,
                    'staff_type': 'Cashier',
                    'reason': 'Long queue detected',
                    'priority': 'high'
                }
            })
        
        # Long wait time detection
        if avg_dwell_time > self.detection_thresholds['wait_time_threshold']:
            detected.append({
                'timestamp': timestamp,
                'event_id': f"LW_{int(datetime.now().timestamp())}",
                'event_data': {
                    'event_name': 'Long Wait Time',
                    'station_id': station_id,
                    'wait_time_seconds': avg_dwell_time,
                    'threshold': self.detection_thresholds['wait_time_threshold']
                }
            })
        
        return detected
    
    # @algorithm Product Recognition Validation | Validates ML predictions against transaction data
    def _detect_recognition_anomalies(self, station_id: str, recognition_event: Dict, timestamp: str) -> List[Dict]:
        """Detect product recognition issues"""
        detected = []
        
        predicted_sku = recognition_event.get('data', {}).get('predicted_product')
        accuracy = recognition_event.get('data', {}).get('accuracy', 0)
        
        # Low accuracy detection
        if accuracy < self.detection_thresholds['accuracy_threshold']:
            detected.append({
                'timestamp': timestamp,
                'event_id': f"RA_{int(datetime.now().timestamp())}",
                'event_data': {
                    'event_name': 'Low Recognition Accuracy',
                    'station_id': station_id,
                    'predicted_sku': predicted_sku,
                    'accuracy': accuracy,
                    'threshold': self.detection_thresholds['accuracy_threshold']
                }
            })
        
        return detected
    
    def _detect_cross_stream_anomalies(self, station_id: str, timestamp: str) -> List[Dict]:
        """Detect anomalies across multiple data streams"""
        detected = []
        
        # Get recent events from all streams
        recent_pos = self._get_recent_events(station_id, 'POS_Transactions', 30)
        recent_rfid = self._get_recent_events(station_id, 'RFID_data', 30)
        
        # Detect potential system crashes (no activity across streams)
        if len(recent_pos) == 0 and len(recent_rfid) == 0:
            all_recent = self._get_all_recent_events(station_id, 60)
            if len(all_recent) == 0:
                detected.append({
                    'timestamp': timestamp,
                    'event_id': f"SC_{int(datetime.now().timestamp())}",
                    'event_data': {
                        'event_name': 'Potential System Crash',
                        'station_id': station_id,
                        'duration_seconds': 60,
                        'detection_method': 'No activity across streams'
                    }
                })
        
        return detected
    
    def _get_recent_events(self, station_id: str, dataset: str, seconds: int) -> List[Dict]:
        """Get recent events from cache for a specific dataset"""
        if station_id not in self.event_cache:
            return []
        if dataset not in self.event_cache[station_id]:
            return []
            
        cutoff = datetime.now() - timedelta(seconds=seconds)
        return [
            e for e in self.event_cache[station_id][dataset]
            if datetime.fromisoformat(e['timestamp']) > cutoff
        ]
    
    def _get_all_recent_events(self, station_id: str, seconds: int) -> List[Dict]:
        """Get all recent events from cache regardless of dataset"""
        if station_id not in self.event_cache:
            return []
            
        all_events = []
        cutoff = datetime.now() - timedelta(seconds=seconds)
        
        for dataset in self.event_cache[station_id]:
            all_events.extend([
                e for e in self.event_cache[station_id][dataset]
                if datetime.fromisoformat(e['timestamp']) > cutoff
            ])
        
        return all_events