# Project Sentinel - System Architecture Guide

## 🎯 System Overview

Project Sentinel is a **real-time retail intelligence system** that consumes multiple data streams, correlates events across different sensors, and detects anomalies to combat inventory shrinkage, self-checkout fraud, and operational inefficiencies.

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMING SERVER (port 8765)                  │
│  Emits: POS_Transactions, RFID_data, Queue_monitor,             │
│         Product_recognism, Current_inventory_data                │
└───────────────────┬─────────────────────────────────────────────┘
                    │ TCP Socket (JSONL)
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              STREAMING CLIENT (streaming_client.py)              │
│  • Connects to server                                            │
│  • Parses JSON events                                            │
│  • Routes to data processor                                      │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│            DATA PROCESSOR (data_processor.py)                    │
│  • Loads reference data (products, customers)                    │
│  • Validates weights, EPCs, barcodes                             │
│  • Stores events in SQLite for correlation                       │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│           ANOMALY DETECTOR (anomaly_detector.py)                 │
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║  EVENT CORRELATION ENGINE                                 ║  │
│  ║  • Time-window correlation (30-second windows)            ║  │
│  ║  • Session tracking (per customer + station)              ║  │
│  ║  • Cross-stream analysis                                  ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
│                                                                   │
│  Detection Algorithms:                                           │
│  ✓ Scanner Avoidance (RFID without POS)                         │
│  ✓ Barcode Switching (Product Recognition vs POS mismatch)      │
│  ✓ Weight Discrepancies (POS weight vs catalog)                 │
│  ✓ System Crashes (POS status detection)                        │
│  ✓ Long Queue Length (Queue monitor thresholds)                 │
│  ✓ Long Wait Time (Dwell time analysis)                         │
│  ✓ Inventory Discrepancy (Sales vs inventory correlation)       │
│  ✓ Staffing Needs (Queue-based recommendations)                 │
│  ✓ Session Pattern Analysis (Customer behavior anomalies)       │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│          EVENT GENERATOR (event_generator.py)                    │
│  • Formats detected events to JSONL                              │
│  • Writes to evidence/output/*/events.jsonl                      │
│  • Generates event IDs (E001, E002, ...)                         │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              FLASK + SOCKET.IO SERVER (app.py)                   │
│  • REST API endpoints for historical events                      │
│  • WebSocket for real-time event streaming                       │
│  • Connects backend to frontend dashboard                        │
└───────────────────┬─────────────────────────────────────────────┘
                    │ WebSocket
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│           REACT DASHBOARD (frontend/)                            │
│  • Real-time event visualization                                 │
│  • Alert management                                              │
│  • Statistics and metrics                                        │
│  • Station status monitoring                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Event Correlation Logic

### Time-Based Correlation Windows

Events happening within **30 seconds** of each other at the **same station** are grouped for correlation analysis:

```python
# Example: Detecting Scanner Avoidance
┌──────────────────────────────────────────────────────────┐
│ Time Window: 16:00:00 - 16:00:30 @ Station SCC1         │
├──────────────────────────────────────────────────────────┤
│ 16:00:04 - RFID Reading: SKU=PRD_T_03, Location=IN_SCAN │
│ 16:00:01 - POS Transaction: SKU=PRD_F_14                │
│                                                          │
│ DETECTION: PRD_T_03 detected by RFID but NOT in POS     │
│ ➜ EVENT: Scanner Avoidance (PRD_T_03)                   │
└──────────────────────────────────────────────────────────┘
```

### Session-Based Tracking

Customer sessions track all events for a **customer_id + station_id** combination:

```python
Session: C056_SCC1
├─ Start: 16:00:00
├─ Events:
│  ├─ POS: PRD_F_14 (weight=400g)
│  ├─ RFID: PRD_T_03 (IN_SCAN_AREA)
│  ├─ Product Recognition: PRD_A_03 (accuracy=0.67)
│  └─ POS: PRD_F_14 (weight=400g)
├─ Last Activity: 16:00:45
└─ Status: Active

DETECTION LOGIC:
✓ Compare RFID products vs POS products → Scanner Avoidance
✓ Compare Product Recognition vs POS → Barcode Switching
✓ Validate POS weights vs catalog → Weight Discrepancies
✓ Analyze transaction timing → Rapid Transaction Fraud
```

---

## 🧠 Core Detection Algorithms

### 1. Scanner Avoidance Detection

**Goal:** Detect items in RFID scan area that aren't scanned at POS

```python
# @algorithm Scanner Avoidance Detection
def detect_scanner_avoidance(station_id, timestamp):
    # Get correlated events within 30-second window
    correlated = get_correlated_events(station_id, timestamp, 30)

    rfid_skus = [e.sku for e in correlated.rfid_readings
                 if e.location == 'IN_SCAN_AREA']
    pos_skus = [e.sku for e in correlated.pos_transactions]

    # Items detected by RFID but not scanned
    unscanned = set(rfid_skus) - set(pos_skus)

    for sku in unscanned:
        emit_event("Scanner Avoidance", {
            "station_id": station_id,
            "product_sku": sku,
            "detection_method": "RFID-POS correlation"
        })
```

### 2. Barcode Switching Detection

**Goal:** Detect when product recognition doesn't match POS scan

```python
# @algorithm Barcode Switching Detection
def detect_barcode_switching(station_id, timestamp):
    correlated = get_correlated_events(station_id, timestamp, 30)

    # Match recognition events with closest POS transaction (within 10s)
    for recognition in correlated.product_recognition:
        predicted_sku = recognition.predicted_product
        recognition_time = recognition.timestamp

        closest_pos = find_closest_pos(correlated.pos_transactions,
                                       recognition_time, 10)

        if closest_pos and closest_pos.sku != predicted_sku:
            # Check if different product categories (stronger indicator)
            if get_category(predicted_sku) != get_category(closest_pos.sku):
                emit_event("Barcode Switching", {
                    "station_id": station_id,
                    "predicted_sku": predicted_sku,
                    "scanned_sku": closest_pos.sku,
                    "time_diff": abs(recognition_time - closest_pos.timestamp)
                })
```

### 3. Weight Discrepancy Detection

**Goal:** Validate POS transaction weights against catalog

```python
# @algorithm Weight Validation
def detect_weight_discrepancy(pos_event):
    sku = pos_event.data.sku
    actual_weight = pos_event.data.weight_g

    expected_weight = products_catalog[sku].weight
    deviation = abs(actual_weight - expected_weight) / expected_weight

    if deviation > 0.15:  # 15% tolerance
        emit_event("Weight Discrepancies", {
            "station_id": pos_event.station_id,
            "customer_id": pos_event.data.customer_id,
            "product_sku": sku,
            "expected_weight": expected_weight,
            "actual_weight": actual_weight,
            "deviation_percent": round(deviation * 100, 2)
        })
```

### 4. System Crash Detection

**Goal:** Detect POS system crashes or sensor failures

```python
# @algorithm System Health Monitoring
def detect_system_crashes(pos_event):
    if pos_event.status == "System Crash":
        emit_event("Unexpected Systems Crash", {
            "station_id": pos_event.station_id,
            "duration_seconds": 180,  # Estimated downtime
            "detection_time": pos_event.timestamp
        })

    # Also detect via correlation absence
    correlated = get_correlated_events(station_id, timestamp, 30)

    if (len(correlated.pos_transactions) == 0 and
        len(correlated.rfid_readings) == 0 and
        len(correlated.product_recognition) == 0):
        emit_event("System Crash", {
            "station_id": station_id,
            "detection_method": "No activity across all streams"
        })
```

### 5. Queue Monitoring

**Goal:** Detect long queues and wait times

```python
# @algorithm Queue Analysis
def detect_queue_issues(queue_event):
    customer_count = queue_event.data.customer_count
    avg_dwell_time = queue_event.data.average_dwell_time

    # Long queue
    if customer_count > 5:
        emit_event("Long Queue Length", {
            "station_id": queue_event.station_id,
            "customer_count": customer_count,
            "threshold": 5
        })

        # Recommend staffing
        emit_event("Staffing Needs", {
            "station_id": queue_event.station_id,
            "staff_type": "Cashier",
            "reason": "Long queue detected",
            "priority": "high"
        })

    # Long wait time
    if avg_dwell_time > 120:  # 2 minutes
        emit_event("Long Wait Time", {
            "station_id": queue_event.station_id,
            "wait_time_seconds": avg_dwell_time,
            "threshold": 120
        })
```

### 6. Inventory Discrepancy Detection

**Goal:** Detect inventory shrinkage through sales correlation

```python
# @algorithm Inventory Shrinkage Detection
def detect_inventory_discrepancies(station_id, timestamp):
    correlated = get_correlated_events(station_id, timestamp, 600)  # 10 min

    # Count sold items
    sold_items = {}
    for pos in correlated.pos_transactions:
        sku = pos.data.sku
        sold_items[sku] = sold_items.get(sku, 0) + 1

    # Get latest inventory snapshot
    latest_inventory = correlated.inventory_snapshots[-1]

    for sku, sold_count in sold_items.items():
        current_inventory = latest_inventory.data.get(sku, 0)
        expected_inventory = initial_inventory[sku] - sold_count

        discrepancy = abs(current_inventory - expected_inventory)

        if discrepancy > 5:  # More than 5 units difference
            emit_event("Inventory Discrepancy", {
                "sku": sku,
                "expected_inventory": expected_inventory,
                "actual_inventory": current_inventory,
                "discrepancy": discrepancy
            })
```

---

## 📤 Output Format

All detected events are written to `events.jsonl` in this exact format:

```json
{"timestamp": "2025-10-04T06:59:20.506181", "event_id": "E147", "event_data": {"event_name": "Weight Discrepancies", "station_id": "SCC1", "customer_id": "UNKNOWN", "product_sku": "PRD_F_14", "expected_weight": 540.0, "actual_weight": 400.0}}
{"timestamp": "2025-10-04T06:59:20.809300", "event_id": "E148", "event_data": {"event_name": "Scanner Avoidance", "station_id": "SCC1", "customer_id": "UNKNOWN", "product_sku": "PRD_T_03"}}
```

### Event Types

| Event Name                 | Fields                                                               | Description                           |
| -------------------------- | -------------------------------------------------------------------- | ------------------------------------- |
| `Scanner Avoidance`        | station_id, customer_id, product_sku                                 | RFID detected, not scanned at POS     |
| `Barcode Switching`        | station_id, customer_id, actual_sku, scanned_sku                     | Product recognition mismatch with POS |
| `Weight Discrepancies`     | station_id, customer_id, product_sku, expected_weight, actual_weight | Weight deviation > 15%                |
| `Unexpected Systems Crash` | station_id, duration_seconds                                         | POS system failure                    |
| `Long Queue Length`        | station_id, num_of_customers                                         | Queue exceeds threshold               |
| `Long Wait Time`           | station_id, wait_time_seconds                                        | Dwell time exceeds threshold          |
| `Inventory Discrepancy`    | SKU, Expected_Inventory, Actual_Inventory                            | Sales-inventory mismatch              |
| `Staffing Needs`           | station_id, Staff_type                                               | Recommendation to add staff           |
| `Checkout Station Action`  | station_id, Action                                                   | Open/close station recommendation     |

---

## 🚀 Running the System

### 1. Start the Streaming Server

```bash
cd d:/ProjectSentinel/zebra/data/streaming-server
python stream_server.py --port 8765 --speed 10 --loop
```

### 2. Start the Backend Server

```bash
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/backend
python app.py
```

### 3. Start the Frontend Dashboard

```bash
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/frontend
npm install
npm run dev
```

### 4. View Real-Time Events

- Dashboard: `http://localhost:5173`
- API: `http://localhost:5000/api/events`
- Output file: `evidence/output/final/events.jsonl`

---

## 🔍 Key Implementation Details

### Event Caching Strategy

```python
# Events are cached per station for 60 seconds
event_cache = {
    'SCC1': {
        'POS_Transactions': [event1, event2, ...],
        'RFID_data': [event1, event2, ...],
        'Queue_monitor': [event1, event2, ...],
        'Product_recognism': [event1, event2, ...],
    },
    'SCC2': { ... }
}
```

### Session Tracking

```python
# Active sessions tracked by station + customer
session_tracker = {
    'SCC1_C056': {
        'customer_id': 'C056',
        'station_id': 'SCC1',
        'start_time': '2025-10-04T16:00:00',
        'last_activity': '2025-10-04T16:00:45',
        'events': [event1, event2, ...],
        'status': 'active'
    }
}
```

### Detection Thresholds

```python
detection_thresholds = {
    'weight_tolerance': 0.15,           # 15% weight deviation
    'queue_length_threshold': 5,        # Max 5 customers
    'wait_time_threshold': 120,         # Max 2 minutes wait
    'accuracy_threshold': 0.8,          # 80% min recognition accuracy
    'correlation_window': 30,           # 30-second correlation window
    'session_timeout': 300,             # 5-minute session timeout
}
```

---

## 📝 Algorithm Tagging

All algorithms are tagged with the required format:

```python
# @algorithm Name | Purpose
def algorithm_function():
    pass
```

Examples in codebase:

- `# @algorithm Cross Stream Correlation | Correlates events across multiple data streams`
- `# @algorithm Scanner Avoidance Detection | Detects items in RFID but missing from POS`
- `# @algorithm Weight Validation | Validates product weights against expected catalog values`

---

## 🎯 Next Steps for Hackathon

1. **Test with provided datasets** - Run system with initial, test, and final datasets
2. **Optimize detection thresholds** - Tune parameters for accuracy
3. **Dashboard polish** - Ensure real-time updates are smooth
4. **Generate events.jsonl** - Verify output format matches requirements
5. **Practice 2-minute demo** - Prepare clear, concise presentation
6. **Document algorithms** - Ensure all detection logic is properly tagged
7. **Create run_demo.py** - Single command to start everything

---

## 📊 Success Metrics

- ✅ All 5 data streams consumed and correlated
- ✅ 9+ event types detected accurately
- ✅ Events output to `events.jsonl` in correct format
- ✅ Real-time dashboard displays events < 1 second delay
- ✅ All algorithms properly tagged with `# @algorithm`
- ✅ System runs end-to-end with single command
- ✅ 2-minute demo ready with clear narrative

Good luck with the hackathon! 🚀
