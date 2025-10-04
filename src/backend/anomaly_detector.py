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
        self.session_tracker = {}  # Track customer sessions across streams
        self.correlation_windows = {}  # Time-based correlation windows
        self.detection_thresholds = {
            'weight_tolerance': 0.15,  # 15% weight deviation
            'queue_length_threshold': 5,  # Max customers per station
            'wait_time_threshold': 120,  # Max wait time in seconds
            'accuracy_threshold': 0.8,  # Min product recognition accuracy
            'correlation_window': 30,  # Seconds for correlating events
            'session_timeout': 300,  # 5 minutes session timeout
        }
    
    def process_event(self, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process incoming event and detect anomalies using advanced correlation
        
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
        
        # Run stream-specific detection algorithms
        if dataset == 'POS_Transactions':
            detected_events.extend(self._detect_pos_anomalies(station_id, event_content, timestamp))
        elif dataset == 'RFID_data':
            detected_events.extend(self._detect_rfid_anomalies(station_id, event_content, timestamp))
        elif dataset == 'Queue_monitor':
            detected_events.extend(self._detect_queue_anomalies(station_id, event_content, timestamp))
        elif dataset == 'Product_recognism':
            detected_events.extend(self._detect_recognition_anomalies(station_id, event_content, timestamp))
        
        # Advanced cross-stream correlation detection (runs on every event)
        detected_events.extend(self._detect_cross_stream_anomalies(station_id, timestamp))
        
        # Session-based analysis for customer-related events
        customer_id = event_content.get('data', {}).get('customer_id')
        if customer_id:
            session_anomalies = self.analyze_customer_session_anomalies(customer_id)
            detected_events.extend(session_anomalies)
        
        return detected_events
    
    def _cache_event(self, station_id: str, dataset: str, event: Dict, timestamp: str):
        """Cache event for correlation analysis"""
        if station_id not in self.event_cache:
            self.event_cache[station_id] = {}
        if dataset not in self.event_cache[station_id]:
            self.event_cache[station_id][dataset] = []
            
        # Keep only recent events (last 60 seconds)
        cutoff_time = datetime.fromisoformat(timestamp) - timedelta(seconds=60)
        
        # Add new event with enriched metadata
        enriched_event = {
            'timestamp': timestamp,
            'dataset': dataset,
            'station_id': station_id,
            'data': event,
            'processed': False
        }
        
        self.event_cache[station_id][dataset].append(enriched_event)
        
        # Remove old events
        self.event_cache[station_id][dataset] = [
            e for e in self.event_cache[station_id][dataset]
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
        ]
        
        # Update session tracking
        self._update_session_tracking(station_id, dataset, event, timestamp)
    
    # @algorithm Temporal Correlation | Groups events by time windows for cross-stream analysis
    def _update_session_tracking(self, station_id: str, dataset: str, event: Dict, timestamp: str):
        """Track customer sessions across multiple data streams"""
        customer_id = event.get('data', {}).get('customer_id')
        
        if customer_id:
            session_key = f"{station_id}_{customer_id}"
            current_time = datetime.fromisoformat(timestamp)
            
            if session_key not in self.session_tracker:
                self.session_tracker[session_key] = {
                    'customer_id': customer_id,
                    'station_id': station_id,
                    'start_time': timestamp,
                    'last_activity': timestamp,
                    'events': [],
                    'status': 'active'
                }
            
            # Update session with new event
            session = self.session_tracker[session_key]
            session['last_activity'] = timestamp
            session['events'].append({
                'dataset': dataset,
                'timestamp': timestamp,
                'data': event
            })
            
            # Clean up expired sessions
            self._cleanup_expired_sessions(current_time)
    
    def _cleanup_expired_sessions(self, current_time: datetime):
        """Remove expired customer sessions"""
        timeout_threshold = current_time - timedelta(seconds=self.detection_thresholds['session_timeout'])
        
        expired_sessions = []
        for session_key, session in self.session_tracker.items():
            last_activity = datetime.fromisoformat(session['last_activity'])
            if last_activity < timeout_threshold:
                expired_sessions.append(session_key)
        
        for session_key in expired_sessions:
            del self.session_tracker[session_key]
    
    # @algorithm Cross Stream Correlation | Correlates events across multiple data streams within time windows
    def _get_correlated_events(self, station_id: str, timestamp: str, window_seconds: int = None) -> Dict[str, List]:
        """Get all events from different streams within a correlation time window"""
        if window_seconds is None:
            window_seconds = self.detection_thresholds['correlation_window']
            
        current_time = datetime.fromisoformat(timestamp)
        window_start = current_time - timedelta(seconds=window_seconds)
        window_end = current_time + timedelta(seconds=window_seconds)
        
        correlated_events = {
            'pos_transactions': [],
            'rfid_readings': [],
            'product_recognition': [],
            'queue_monitoring': [],
            'inventory_snapshots': []
        }
        
        # Map dataset names to correlation keys
        dataset_mapping = {
            'POS_Transactions': 'pos_transactions',
            'RFID_data': 'rfid_readings', 
            'Product_recognism': 'product_recognition',
            'Queue_monitor': 'queue_monitoring',
            'Current_inventory_data': 'inventory_snapshots'
        }
        
        if station_id in self.event_cache:
            for dataset, events in self.event_cache[station_id].items():
                correlation_key = dataset_mapping.get(dataset, dataset.lower())
                
                for event in events:
                    event_time = datetime.fromisoformat(event['timestamp'])
                    if window_start <= event_time <= window_end:
                        if correlation_key in correlated_events:
                            correlated_events[correlation_key].append(event)
        
        return correlated_events
    
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
        """Detect anomalies across multiple data streams using advanced correlation"""
        detected = []
        
        # Get correlated events within time window
        correlated_events = self._get_correlated_events(station_id, timestamp)
        
        # Detect Scanner Avoidance (RFID without corresponding POS)
        detected.extend(self._detect_scanner_avoidance_correlation(
            correlated_events, station_id, timestamp
        ))
        
        # Detect Barcode Switching (Product Recognition vs POS mismatch)
        detected.extend(self._detect_barcode_switching_correlation(
            correlated_events, station_id, timestamp
        ))
        
        # Detect Weight Fraud (Multiple weight readings for single transaction)
        detected.extend(self._detect_weight_fraud_correlation(
            correlated_events, station_id, timestamp
        ))
        
        # Detect System Issues (Missing expected correlations)
        detected.extend(self._detect_system_correlation_issues(
            correlated_events, station_id, timestamp
        ))
        
        # Detect Inventory Shrinkage Patterns
        detected.extend(self._detect_inventory_shrinkage_correlation(
            correlated_events, station_id, timestamp
        ))
        
        return detected
    
    # @algorithm Scanner Avoidance Correlation | Detects RFID readings without corresponding POS transactions
    def _detect_scanner_avoidance_correlation(self, correlated_events: Dict, station_id: str, timestamp: str) -> List[Dict]:
        """Detect scanner avoidance by correlating RFID and POS streams"""
        detected = []
        
        rfid_events = correlated_events.get('rfid_readings', [])
        pos_events = correlated_events.get('pos_transactions', [])
        
        # Get SKUs from POS transactions
        scanned_skus = set()
        for pos_event in pos_events:
            sku = pos_event.get('data', {}).get('data', {}).get('sku')
            if sku:
                scanned_skus.add(sku)
        
        # Check for RFID readings without corresponding POS scans
        for rfid_event in rfid_events:
            rfid_data = rfid_event.get('data', {}).get('data', {})
            sku = rfid_data.get('sku')
            location = rfid_data.get('location')
            
            if sku and location == 'IN_SCAN_AREA' and sku not in scanned_skus:
                detected.append({
                    'timestamp': timestamp,
                    'event_id': f"SA_CORR_{int(datetime.now().timestamp())}",
                    'event_data': {
                        'event_name': 'Scanner Avoidance',
                        'station_id': station_id,
                        'product_sku': sku,
                        'detection_method': 'RFID-POS correlation analysis',
                        'confidence': 0.85,
                        'evidence': {
                            'rfid_detected': True,
                            'pos_scanned': False,
                            'location': location
                        }
                    }
                })
        
        return detected
    
    # @algorithm Barcode Switching Correlation | Detects product recognition vs POS transaction mismatches
    def _detect_barcode_switching_correlation(self, correlated_events: Dict, station_id: str, timestamp: str) -> List[Dict]:
        """Detect barcode switching by correlating product recognition and POS data"""
        detected = []
        
        recognition_events = correlated_events.get('product_recognition', [])
        pos_events = correlated_events.get('pos_transactions', [])
        
        # Create temporal matching between recognition and POS events
        for recognition_event in recognition_events:
            recognition_data = recognition_event.get('data', {}).get('data', {})
            predicted_sku = recognition_data.get('predicted_product')
            recognition_time = datetime.fromisoformat(recognition_event.get('timestamp'))
            
            if not predicted_sku:
                continue
            
            # Find closest POS transaction within 10 seconds
            closest_pos = None
            min_time_diff = float('inf')
            
            for pos_event in pos_events:
                pos_time = datetime.fromisoformat(pos_event.get('timestamp'))
                time_diff = abs((recognition_time - pos_time).total_seconds())
                
                if time_diff <= 10 and time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_pos = pos_event
            
            if closest_pos:
                pos_sku = closest_pos.get('data', {}).get('data', {}).get('sku')
                
                # Check for mismatch between recognition and scanned product
                if pos_sku and predicted_sku != pos_sku:
                    # Verify this isn't just a recognition error by checking product categories
                    predicted_category = predicted_sku.split('_')[1] if '_' in predicted_sku else 'unknown'
                    scanned_category = pos_sku.split('_')[1] if '_' in pos_sku else 'unknown'
                    
                    # If different categories, likely barcode switching
                    if predicted_category != scanned_category:
                        detected.append({
                            'timestamp': timestamp,
                            'event_id': f"BS_CORR_{int(datetime.now().timestamp())}",
                            'event_data': {
                                'event_name': 'Barcode Switching',
                                'station_id': station_id,
                                'predicted_sku': predicted_sku,
                                'scanned_sku': pos_sku,
                                'detection_method': 'Recognition-POS correlation',
                                'confidence': 0.75,
                                'time_difference': min_time_diff
                            }
                        })
        
        return detected
    
    # @algorithm Weight Fraud Correlation | Detects suspicious weight patterns across transactions
    def _detect_weight_fraud_correlation(self, correlated_events: Dict, station_id: str, timestamp: str) -> List[Dict]:
        """Detect weight fraud by analyzing weight patterns in POS transactions"""
        detected = []
        
        pos_events = correlated_events.get('pos_transactions', [])
        
        # Group transactions by customer
        customer_transactions = {}
        for pos_event in pos_events:
            pos_data = pos_event.get('data', {}).get('data', {})
            customer_id = pos_data.get('customer_id')
            
            if customer_id:
                if customer_id not in customer_transactions:
                    customer_transactions[customer_id] = []
                customer_transactions[customer_id].append(pos_event)
        
        # Analyze weight patterns per customer
        for customer_id, transactions in customer_transactions.items():
            if len(transactions) < 2:
                continue
                
            weights = []
            skus = []
            
            for transaction in transactions:
                trans_data = transaction.get('data', {}).get('data', {})
                weight = trans_data.get('weight_g', 0)
                sku = trans_data.get('sku')
                
                if weight > 0 and sku:
                    weights.append(weight)
                    skus.append(sku)
            
            # Detect suspicious weight consistency (same weight for different products)
            if len(weights) > 1 and len(set(skus)) > 1:
                weight_variance = np.var(weights) if len(weights) > 1 else 0
                
                # If multiple different products have very similar weights, suspicious
                if weight_variance < 10:  # Less than 10g variance across products
                    detected.append({
                        'timestamp': timestamp,
                        'event_id': f"WF_{int(datetime.now().timestamp())}",
                        'event_data': {
                            'event_name': 'Weight Fraud Pattern',
                            'station_id': station_id,
                            'customer_id': customer_id,
                            'detection_method': 'Weight pattern correlation',
                            'weight_variance': round(weight_variance, 2),
                            'products_count': len(set(skus)),
                            'suspicious_weights': weights
                        }
                    })
        
        return detected
    
    def _detect_system_correlation_issues(self, correlated_events: Dict, station_id: str, timestamp: str) -> List[Dict]:
        """Detect system issues based on missing expected correlations"""
        detected = []
        
        pos_count = len(correlated_events.get('pos_transactions', []))
        rfid_count = len(correlated_events.get('rfid_readings', []))
        recognition_count = len(correlated_events.get('product_recognition', []))
        
        # System crash detection: No activity across all streams
        if pos_count == 0 and rfid_count == 0 and recognition_count == 0:
            detected.append({
                'timestamp': timestamp,
                'event_id': f"SC_{int(datetime.now().timestamp())}",
                'event_data': {
                    'event_name': 'System Crash',
                    'station_id': station_id,
                    'duration_seconds': 30,
                    'detection_method': 'Cross-stream correlation analysis'
                }
            })
        
        # Sensor malfunction: Significant imbalance in expected ratios
        elif pos_count > 0:
            expected_rfid_ratio = 0.8  # Expect RFID for 80% of POS transactions
            expected_recognition_ratio = 0.9  # Expect recognition for 90% of POS
            
            if rfid_count < pos_count * expected_rfid_ratio:
                detected.append({
                    'timestamp': timestamp,
                    'event_id': f"RF_FAIL_{int(datetime.now().timestamp())}",
                    'event_data': {
                        'event_name': 'RFID Sensor Malfunction',
                        'station_id': station_id,
                        'expected_ratio': expected_rfid_ratio,
                        'actual_ratio': rfid_count / pos_count if pos_count > 0 else 0
                    }
                })
            
            if recognition_count < pos_count * expected_recognition_ratio:
                detected.append({
                    'timestamp': timestamp,
                    'event_id': f"PR_FAIL_{int(datetime.now().timestamp())}",
                    'event_data': {
                        'event_name': 'Product Recognition System Failure',
                        'station_id': station_id,
                        'expected_ratio': expected_recognition_ratio,
                        'actual_ratio': recognition_count / pos_count if pos_count > 0 else 0
                    }
                })
        
        return detected
    
    def _detect_inventory_shrinkage_correlation(self, correlated_events: Dict, station_id: str, timestamp: str) -> List[Dict]:
        """Detect inventory shrinkage by correlating transactions with inventory updates"""
        detected = []
        
        pos_events = correlated_events.get('pos_transactions', [])
        inventory_events = correlated_events.get('inventory_snapshots', [])
        
        if not inventory_events:
            return detected
        
        # Get latest inventory snapshot
        latest_inventory = inventory_events[-1] if inventory_events else None
        if not latest_inventory:
            return detected
        
        inventory_data = latest_inventory.get('data', {}).get('data', {})
        
        # Check for products being sold but not properly deducted from inventory
        sold_skus = {}
        for pos_event in pos_events:
            pos_data = pos_event.get('data', {}).get('data', {})
            sku = pos_data.get('sku')
            if sku:
                sold_skus[sku] = sold_skus.get(sku, 0) + 1
        
        for sku, sold_quantity in sold_skus.items():
            current_inventory = inventory_data.get(sku, 0)
            
            # If high sales but inventory still high, potential shrinkage
            if sold_quantity >= 3 and current_inventory > 50:
                detected.append({
                    'timestamp': timestamp,
                    'event_id': f"IS_{int(datetime.now().timestamp())}",
                    'event_data': {
                        'event_name': 'Inventory Discrepancy',
                        'station_id': station_id,
                        'sku': sku,
                        'sold_quantity': sold_quantity,
                        'current_inventory': current_inventory,
                        'detection_method': 'Sales-inventory correlation'
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
    
    # @algorithm Session Pattern Analysis | Analyzes customer behavior patterns across complete sessions
    def analyze_customer_session_anomalies(self, customer_id: str = None) -> List[Dict]:
        """Analyze customer sessions for suspicious patterns"""
        detected = []
        
        # Get active sessions to analyze
        sessions_to_analyze = []
        if customer_id:
            session_key = f"*_{customer_id}"  # Find sessions for specific customer
            sessions_to_analyze = [
                s for k, s in self.session_tracker.items() 
                if s['customer_id'] == customer_id
            ]
        else:
            # Analyze all active sessions
            sessions_to_analyze = list(self.session_tracker.values())
        
        for session in sessions_to_analyze:
            session_anomalies = self._analyze_single_session(session)
            detected.extend(session_anomalies)
        
        return detected
    
    def _analyze_single_session(self, session: Dict) -> List[Dict]:
        """Analyze a single customer session for anomalies"""
        detected = []
        
        events = session.get('events', [])
        customer_id = session.get('customer_id')
        station_id = session.get('station_id')
        
        if len(events) < 2:
            return detected
        
        # Group events by type
        pos_events = [e for e in events if e['dataset'] == 'POS_Transactions']
        rfid_events = [e for e in events if e['dataset'] == 'RFID_data']
        recognition_events = [e for e in events if e['dataset'] == 'Product_recognism']
        
        # Detect rapid successive transactions (possible fraud)
        if len(pos_events) > 1:
            transaction_times = [
                datetime.fromisoformat(e['timestamp']) for e in pos_events
            ]
            transaction_times.sort()
            
            for i in range(1, len(transaction_times)):
                time_diff = (transaction_times[i] - transaction_times[i-1]).total_seconds()
                
                # Transactions less than 5 seconds apart are suspicious
                if time_diff < 5:
                    detected.append({
                        'timestamp': transaction_times[i].isoformat(),
                        'event_id': f"RT_{int(datetime.now().timestamp())}",
                        'event_data': {
                            'event_name': 'Rapid Transactions',
                            'station_id': station_id,
                            'customer_id': customer_id,
                            'time_difference': time_diff,
                            'detection_method': 'Session pattern analysis'
                        }
                    })
        
        # Detect RFID-POS mismatches within session
        rfid_skus = set()
        for rfid_event in rfid_events:
            sku = rfid_event.get('data', {}).get('data', {}).get('sku')
            location = rfid_event.get('data', {}).get('data', {}).get('location')
            if sku and location == 'IN_SCAN_AREA':
                rfid_skus.add(sku)
        
        pos_skus = set()
        for pos_event in pos_events:
            sku = pos_event.get('data', {}).get('data', {}).get('sku')
            if sku:
                pos_skus.add(sku)
        
        # Products detected by RFID but not scanned at POS
        unscanned_products = rfid_skus - pos_skus
        if unscanned_products:
            detected.append({
                'timestamp': session.get('last_activity'),
                'event_id': f"SP_{int(datetime.now().timestamp())}",
                'event_data': {
                    'event_name': 'Session Product Mismatch',
                    'station_id': station_id,
                    'customer_id': customer_id,
                    'unscanned_products': list(unscanned_products),
                    'detection_method': 'Session-based RFID-POS correlation'
                }
            })
        
        # Detect unusual session duration patterns
        start_time = datetime.fromisoformat(session.get('start_time'))
        end_time = datetime.fromisoformat(session.get('last_activity'))
        session_duration = (end_time - start_time).total_seconds()
        
        # Very short sessions with multiple items are suspicious
        if session_duration < 30 and len(pos_events) > 3:
            detected.append({
                'timestamp': session.get('last_activity'),
                'event_id': f"SS_{int(datetime.now().timestamp())}",
                'event_data': {
                    'event_name': 'Suspicious Short Session',
                    'station_id': station_id,
                    'customer_id': customer_id,
                    'session_duration': session_duration,
                    'items_count': len(pos_events),
                    'detection_method': 'Session duration analysis'
                }
            })
        
        return detected
    
    def get_correlation_statistics(self, station_id: str = None) -> Dict:
        """Get statistics about stream correlations for monitoring dashboard"""
        stats = {
            'total_events_cached': 0,
            'active_sessions': len(self.session_tracker),
            'correlation_success_rate': 0.0,
            'stream_health': {},
            'anomaly_detection_rate': 0.0
        }
        
        if station_id:
            stations_to_check = [station_id]
        else:
            stations_to_check = list(self.event_cache.keys())
        
        total_events = 0
        stream_counts = {}
        
        for station in stations_to_check:
            if station in self.event_cache:
                for dataset, events in self.event_cache[station].items():
                    count = len(events)
                    total_events += count
                    stream_counts[dataset] = stream_counts.get(dataset, 0) + count
        
        stats['total_events_cached'] = total_events
        stats['stream_health'] = stream_counts
        
        # Calculate correlation success rate (simplified)
        if 'POS_Transactions' in stream_counts and 'RFID_data' in stream_counts:
            pos_count = stream_counts['POS_Transactions']
            rfid_count = stream_counts['RFID_data']
            expected_correlation = min(pos_count, rfid_count)
            stats['correlation_success_rate'] = (expected_correlation / max(pos_count, 1)) * 100
        
        return stats