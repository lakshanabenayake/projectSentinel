"""
Data Processing Module for Project Sentinel
Handles real-time data ingestion and preprocessing
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3

class DataProcessor:
    """Main data processor for handling streaming retail data"""
    
    def __init__(self):
        self.current_inventory = {}
        self.products_catalog = {}
        self.customers_data = {}
        self.load_reference_data()
    
    def load_reference_data(self):
        """Load products and customer reference data"""
        try:
            # Get the base directory (go up to zebra folder)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.join(current_dir, '..', '..', '..', '..')
            
            # Load products catalog
            products_path = os.path.join(base_dir, 'data', 'input', 'products_list.csv')
            products_df = pd.read_csv(products_path)
            self.products_catalog = products_df.set_index('SKU').to_dict('index')
            
            # Load customer data
            customers_path = os.path.join(base_dir, 'data', 'input', 'customer_data.csv')
            customers_df = pd.read_csv(customers_path)
            self.customers_data = customers_df.set_index('Customer_ID').to_dict('index')
            
            print(f"✅ Loaded {len(self.products_catalog)} products and {len(self.customers_data)} customers")
            
        except Exception as e:
            print(f"Warning: Could not load reference data: {e}")
            # Use fallback empty dictionaries
            self.products_catalog = {}
            self.customers_data = {}
    
    # @algorithm Data Correlation | Correlates multi-stream sensor data for anomaly detection
    def correlate_station_events(self, station_id: str, time_window: int = 10) -> Dict[str, List[Dict]]:
        """
        Correlate events from different data streams for a specific station within time window
        
        Args:
            station_id: Station to analyze (e.g., 'SCC1', 'RC1')
            time_window: Time window in seconds to correlate events
            
        Returns:
            Dictionary containing correlated events by data stream type
        """
        conn = sqlite3.connect('sentinel.db')
        cursor = conn.cursor()
        
        # Get events within time window
        cursor.execute('''
            SELECT dataset, timestamp, data 
            FROM stream_data 
            WHERE station_id = ? 
            AND datetime(timestamp) > datetime('now', '-{} seconds')
            ORDER BY timestamp
        '''.format(time_window), (station_id,))
        
        events = cursor.fetchall()
        conn.close()
        
        # Group events by dataset type
        correlated_events = {
            'pos_transactions': [],
            'rfid_readings': [],
            'queue_monitoring': [],
            'product_recognition': [],
            'inventory_snapshots': []
        }
        
        for event in events:
            dataset, timestamp, data_json = event
            data = json.loads(data_json) if data_json else {}
            
            event_obj = {
                'timestamp': timestamp,
                'data': data
            }
            
            if dataset in correlated_events:
                correlated_events[dataset].append(event_obj)
        
        return correlated_events
    
    # @algorithm Weight Validation | Validates product weights against expected catalog values  
    def validate_product_weight(self, sku: str, actual_weight: float, tolerance: float = 0.1) -> bool:
        """
        Validate if actual product weight matches expected catalog weight
        
        Args:
            sku: Product SKU
            actual_weight: Actual measured weight in grams
            tolerance: Acceptable weight deviation percentage (default 10%)
            
        Returns:
            True if weight is within tolerance, False otherwise
        """
        if sku not in self.products_catalog:
            return False
            
        expected_weight = self.products_catalog[sku].get('weight', 0)
        if expected_weight == 0:
            return False
            
        deviation = abs(actual_weight - expected_weight) / expected_weight
        return deviation <= tolerance
    
    def get_product_info(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product information by SKU"""
        return self.products_catalog.get(sku)
    
    def get_customer_info(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer information by ID"""
        return self.customers_data.get(customer_id)
    
    # @algorithm EPC Validation | Maps RFID EPC codes to product SKUs using catalog ranges
    def validate_epc_to_sku(self, epc: str, claimed_sku: str) -> bool:
        """
        Validate if EPC code matches the claimed SKU based on catalog EPC ranges
        
        Args:
            epc: RFID EPC code
            claimed_sku: SKU claimed to match the EPC
            
        Returns:
            True if EPC is valid for the SKU, False otherwise
        """
        if claimed_sku not in self.products_catalog:
            return False
            
        epc_range = self.products_catalog[claimed_sku].get('EPC_range', '')
        if not epc_range or '-' not in epc_range:
            return False
            
        try:
            range_start, range_end = epc_range.split('-')
            # Convert EPC to integer for range comparison
            epc_int = int(epc.replace('E', ''), 16)
            start_int = int(range_start.replace('E', ''), 16)  
            end_int = int(range_end.replace('E', ''), 16)
            
            return start_int <= epc_int <= end_int
        except ValueError:
            return False
    
    def update_inventory(self, inventory_data: Dict[str, int]):
        """Update current inventory levels"""
        self.current_inventory = inventory_data
    
    def get_inventory_level(self, sku: str) -> int:
        """Get current inventory level for a product"""
        return self.current_inventory.get(sku, 0)
    
    # @algorithm Transaction Aggregation | Aggregates POS data for customer behavior analysis
    def aggregate_customer_transactions(self, customer_id: str, hours: int = 1) -> Dict[str, Any]:
        """
        Aggregate transaction data for a customer within specified time window
        
        Args:
            customer_id: Customer ID to analyze
            hours: Time window in hours
            
        Returns:
            Aggregated transaction statistics
        """
        conn = sqlite3.connect('sentinel.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data 
            FROM stream_data 
            WHERE dataset = 'POS_Transactions' 
            AND json_extract(data, '$.data.customer_id') = ?
            AND datetime(timestamp) > datetime('now', '-{} hours')
        '''.format(hours), (customer_id,))
        
        transactions = cursor.fetchall()
        conn.close()
        
        total_amount = 0
        item_count = 0
        unique_products = set()
        
        for transaction in transactions:
            data = json.loads(transaction[0])
            transaction_data = data.get('data', {})
            
            total_amount += transaction_data.get('price', 0)
            item_count += 1
            unique_products.add(transaction_data.get('sku'))
        
        return {
            'total_amount': total_amount,
            'item_count': item_count,
            'unique_products': len(unique_products),
            'average_item_price': total_amount / item_count if item_count > 0 else 0
        }