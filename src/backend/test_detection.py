#!/usr/bin/env python3
"""
Test Enhanced Event Detection
Validates that our SentinelDetector produces the expected output format
"""

import json
import os
from sentinel_detector import SentinelDetector

def test_detection_logic():
    """Test the enhanced detection with sample data"""
    
    print("=== Testing Enhanced Event Detection ===\n")
    
    # Initialize detector
    detector = SentinelDetector()
    
    # Test data samples based on streaming format
    test_events = [
        # RFID Detection
        {
            "dataset": "rfid_data",
            "event": {
                "status": "Active",
                "station_id": "SCC1",
                "customer_id": "C001",
                "data": {"sku": "PRD_F_03"}
            }
        },
        # POS Transaction (Success Operation)
        {
            "dataset": "pos_transactions",
            "event": {
                "status": "Active",
                "station_id": "SCC1",
                "customer_id": "C001",
                "data": {"sku": "PRD_F_03", "weight_g": 150, "price": 280}
            }
        },
        # Different customer RFID
        {
            "dataset": "rfid_data",
            "event": {
                "status": "Active",
                "station_id": "SCC1",
                "customer_id": "C004",
                "data": {"sku": "PRD_S_04"}
            }
        },
        # Product Recognition (Barcode Switching)
        {
            "dataset": "pos_transactions",
            "event": {
                "status": "Active",
                "station_id": "SCC1",
                "customer_id": "C009",
                "data": {"sku": "PRD_F_07", "weight_g": 200}
            }
        },
        {
            "dataset": "product_recognition",
            "event": {
                "status": "Active",
                "station_id": "SCC1",
                "customer_id": "C009",
                "data": {"predicted_product": "PRD_F_08"}
            }
        },
        # Weight Discrepancy
        {
            "dataset": "pos_transactions",
            "event": {
                "status": "Active",
                "station_id": "SCC1",
                "customer_id": "C007",
                "data": {"sku": "PRD_F_09", "weight_g": 680, "price": 425}
            }
        },
        # System Crash
        {
            "dataset": "pos_transactions",
            "event": {
                "status": "System Crash",
                "station_id": "SCC1",
                "customer_id": "C010",
                "data": {}
            }
        },
        # Queue Monitoring
        {
            "dataset": "queue_monitor",
            "event": {
                "status": "Active",
                "station_id": "SCC1",
                "customer_id": "C015",
                "data": {"customer_count": 6, "average_dwell_time": 350}
            }
        },
        # Inventory Discrepancy
        {
            "dataset": "inventory_snapshots",
            "event": {
                "status": "Active",
                "station_id": "WAREHOUSE",
                "data": {"PRD_F_03": 120}
            }
        },
        {
            "dataset": "inventory_snapshots",
            "event": {
                "status": "Active",
                "station_id": "WAREHOUSE", 
                "data": {"PRD_F_03": 150}
            }
        },
        # Staffing
        {
            "dataset": "staffing",
            "event": {
                "status": "Active",
                "station_id": "SCC1",
                "data": {"Staff_type": "Cashier"}
            }
        },
        # Checkout Action
        {
            "dataset": "checkout_action",
            "event": {
                "status": "Active",
                "station_id": "SCC1",
                "data": {"Action": "Open"}
            }
        }
    ]
    
    print("Processing test events...")
    
    for i, event in enumerate(test_events, 1):
        print(f"\n--- Processing Event {i} ({event['dataset']}) ---")
        result = detector.detect(event)
        if result:
            print(f"✅ Event detected!")
        else:
            print("ℹ️  No event generated (state updated)")
    
    # Check for scanner avoidance (C004 had RFID but no POS scan)
    print("\n--- Final Scanner Avoidance Check ---")
    detector._check_scanner_avoidance("SCC1")
    
    print(f"\n=== Detection Complete ===")
    stats = detector.get_statistics()
    print(f"📊 Statistics: {json.dumps(stats, indent=2)}")
    
    # Check output file
    if os.path.exists(stats['output_file']):
        print(f"\n📄 Output file created: {stats['output_file']}")
        with open(stats['output_file'], 'r') as f:
            lines = f.readlines()
            print(f"📝 Events written: {len(lines)}")
            
            print("\n🎯 Sample Events Generated:")
            for i, line in enumerate(lines[:3], 1):
                event = json.loads(line.strip())
                print(f"{i}. {event['event_data']['event_name']} -> {event['event_id']}")
    else:
        print("❌ Output file not created")

if __name__ == "__main__":
    test_detection_logic()