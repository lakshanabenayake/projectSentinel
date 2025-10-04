# Project Sentinel - Implementation Checklist

## ✅ What You Already Have

### Backend (90% Complete)

- ✅ **streaming_client.py** - Connects to stream server via TCP socket
- ✅ **data_processor.py** - Loads products/customer reference data
- ✅ **anomaly_detector.py** - Implements all 9+ detection algorithms
- ✅ **event_generator.py** - Formats and exports events to JSONL
- ✅ **sentinel_detector.py** - Enhanced detection with state management
- ✅ **app.py** - Flask + SocketIO server for real-time communication
- ✅ **SQLite database** - Stores events and stream data for correlation

### Detection Algorithms Implemented

- ✅ Scanner Avoidance (RFID-POS correlation)
- ✅ Barcode Switching (Product Recognition vs POS)
- ✅ Weight Discrepancies (Weight validation)
- ✅ System Crashes (Status monitoring + correlation absence)
- ✅ Long Queue Length (Threshold-based)
- ✅ Long Wait Time (Dwell time analysis)
- ✅ Inventory Discrepancy (Sales-inventory correlation)
- ✅ Staffing Needs (Queue-based recommendations)
- ✅ Session Pattern Analysis (Customer behavior)
- ✅ Temporal Correlation (Time-window grouping)
- ✅ Cross-Stream Correlation (Multi-sensor fusion)

---

## 🔧 What Needs Fine-Tuning

### 1. Output File Paths ⚠️

**Current Issue:** Your generated `events.jsonl` is going to:

```
d:\ProjectSentinel\zebra\submission-structure\Team15_sentinel\zebra\runs\data\output\events.jsonl
```

**Should Be:**

```
d:\ProjectSentinel\zebra\submission-structure\Team15_sentinel\evidence\output\test\events.jsonl
d:\ProjectSentinel\zebra\submission-structure\Team15_sentinel\evidence\output\final\events.jsonl
```

**Fix:** Update `sentinel_detector.py` and `event_generator.py`:

```python
# In sentinel_detector.py line ~20
self.output_file = "evidence/output/final/events.jsonl"

# Change to accept parameter:
def __init__(self, output_path="evidence/output/final/events.jsonl"):
    self.output_file = output_path
```

### 2. Event ID Consistency ⚠️

**Current Issue:** Event IDs restart on each run (E001, E002, ...)

**Fix:** Use timestamps or persist counter:

```python
# Better event ID format
event_id = f"E{self.event_counter:03d}_{int(datetime.now().timestamp())}"
```

### 3. Customer ID Detection 🔍

**Current Issue:** Many events show `"customer_id": "UNKNOWN"`

**Root Cause:** POS transactions don't always have customer_id in the stream

**Fix:** Track by session/station instead:

```python
# Use station-based tracking when customer_id missing
session_key = f"{station_id}_{timestamp_window}"
```

### 4. Real-Time WebSocket Broadcasting 🌐

**Current Issue:** Backend might not be sending events to frontend via WebSocket

**Fix:** In `app.py`, ensure events are emitted:

```python
# After detecting event
def on_data_received(event_data):
    detected_events = anomaly_detector.process_event(event_data)

    for event in detected_events:
        # Save to database
        save_event_to_db(event)

        # Broadcast to frontend via WebSocket
        socketio.emit('new_event', event, namespace='/')

        # Write to JSONL file
        event_generator.add_event(event)
```

### 5. Dataset Name Mapping 🗺️

**Current Issue:** Stream server sends dataset names like `"POS_Transactions"` but your code might expect different names

**Fix:** Ensure consistent mapping:

```python
DATASET_MAPPING = {
    'POS_Transactions': 'pos_transactions',
    'RFID_data': 'rfid_readings',
    'Product_recognism': 'product_recognition',
    'Queue_monitor': 'queue_monitoring',
    'Current_inventory_data': 'inventory_snapshots'
}
```

---

## 🚀 Critical Tasks Before Hackathon Demo

### High Priority (Must Do)

1. ⚠️ **Fix output file paths** - Events must go to `evidence/output/test/` and `evidence/output/final/`
2. ⚠️ **Test with streaming server** - Verify end-to-end flow works
3. ⚠️ **Verify WebSocket events** - Frontend receives real-time updates
4. ⚠️ **Create `run_demo.py`** - Single command to start everything
5. ⚠️ **Test with test dataset** - Generate `evidence/output/test/events.jsonl`
6. ⚠️ **Practice 2-minute demo** - Time yourself presenting the system

### Medium Priority (Should Do)

7. 📊 **Dashboard polish** - Ensure visualizations are clear
8. 📝 **Fill SUBMISSION_GUIDE.md** - Complete all required fields
9. 🔍 **Verify algorithm tags** - Run `grep -R "@algorithm" src/`
10. 📸 **Take screenshots** - Save to `evidence/screenshots/`
11. 🧪 **Edge case testing** - Test with missing data, system crashes
12. 📈 **Performance optimization** - Ensure handles high-speed streams

### Low Priority (Nice to Have)

13. 📚 **Code documentation** - Add docstrings where missing
14. 🎨 **UI improvements** - Polish dashboard aesthetics
15. 🔔 **Alert sounds** - Add audio notifications for critical events
16. 📊 **Statistics dashboard** - Add summary metrics view
17. 🔐 **Error handling** - Graceful degradation on failures

---

## 🎯 Quick Start Guide

### Step 1: Test Data Flow (5 minutes)

```bash
# Terminal 1: Start streaming server
cd d:/ProjectSentinel/zebra/data/streaming-server
python stream_server.py --port 8765 --speed 10 --loop

# Terminal 2: Test client connection
cd d:/ProjectSentinel/zebra/data/streaming-clients
python client_example.py --limit 10

# Verify: You should see events streaming
```

### Step 2: Test Backend Detection (10 minutes)

```bash
# Terminal 3: Start backend server
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/backend
python app.py

# Check:
# - Flask server starts on port 5000
# - Connects to streaming server
# - Prints detected events to console
# - Creates events.jsonl file
```

### Step 3: Test Frontend Dashboard (10 minutes)

```bash
# Terminal 4: Start frontend
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/frontend
npm install  # Only first time
npm run dev

# Open browser: http://localhost:5173
# Check:
# - Dashboard loads
# - Real-time events appear
# - No console errors
```

### Step 4: Verify Output Files (5 minutes)

```bash
# Check generated events
cat evidence/output/final/events.jsonl

# Should see format:
# {"timestamp": "...", "event_id": "E001", "event_data": {...}}
```

### Step 5: Run Algorithm Verification (2 minutes)

```bash
# Verify all algorithms are tagged
grep -R "@algorithm" src/backend/

# Should find 10+ tagged algorithms
```

---

## 🐛 Common Issues & Fixes

### Issue 1: "Connection Refused" Error

**Symptom:** Backend can't connect to streaming server

```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Fix:**

1. Verify streaming server is running: `netstat -an | grep 8765`
2. Check firewall settings
3. Try `127.0.0.1` instead of `0.0.0.0`

### Issue 2: Events Not Appearing on Dashboard

**Symptom:** Backend detects events but frontend doesn't show them

**Fix:**

1. Check browser console for WebSocket errors
2. Verify CORS settings in `app.py`
3. Check SocketIO connection: `socketio.on('connect', () => console.log('Connected!'))`
4. Ensure `socketio.emit()` is called after detection

### Issue 3: Duplicate Events

**Symptom:** Same event detected multiple times

**Fix:**

1. Add deduplication logic:

```python
recent_events = set()

def deduplicate(event):
    event_hash = f"{event['event_data']['event_name']}_{event['timestamp']}"
    if event_hash in recent_events:
        return False
    recent_events.add(event_hash)
    return True
```

### Issue 4: No Scanner Avoidance Detected

**Symptom:** RFID events present but no Scanner Avoidance events

**Fix:**

1. Check correlation window size (try increasing to 60 seconds)
2. Verify RFID `location` field is `"IN_SCAN_AREA"`
3. Add debug logging:

```python
print(f"RFID SKUs: {rfid_skus}")
print(f"POS SKUs: {pos_skus}")
print(f"Unscanned: {set(rfid_skus) - set(pos_skus)}")
```

### Issue 5: Customer ID Always "UNKNOWN"

**Symptom:** All events show `customer_id: "UNKNOWN"`

**Explanation:** This is often expected! Many POS events in test data don't have customer_id.

**Options:**

1. Use station-based tracking (acceptable)
2. Generate synthetic customer IDs based on session timing
3. Leave as "UNKNOWN" (judges understand this)

---

## 📋 Pre-Submission Checklist

### Code Quality

- [ ] All Python files have proper imports
- [ ] No syntax errors: `python -m py_compile *.py`
- [ ] All algorithms tagged with `# @algorithm`
- [ ] Code follows consistent style

### Outputs

- [ ] `evidence/output/test/events.jsonl` exists and has content
- [ ] `evidence/output/final/events.jsonl` exists and has content
- [ ] Events have correct format (timestamp, event_id, event_data)
- [ ] Event IDs are sequential

### Documentation

- [ ] `SUBMISSION_GUIDE.md` completed
- [ ] `README.md` has setup instructions
- [ ] `evidence/screenshots/` has dashboard images
- [ ] Algorithm documentation clear

### Demo

- [ ] `run_demo.py` works with one command
- [ ] Dashboard loads in < 10 seconds
- [ ] Real-time events appear
- [ ] Can explain system in 2 minutes
- [ ] Practiced demo at least 3 times

### Testing

- [ ] Tested with initial dataset
- [ ] Tested with test dataset
- [ ] Tested with final dataset (when provided)
- [ ] No crashes during 10-minute run
- [ ] Memory usage stays stable

---

## 🎬 2-Minute Demo Script

### Slide 1: Problem (20 seconds)

"Retail stores lose millions annually due to self-checkout fraud, inventory shrinkage, and operational inefficiencies. Project Sentinel is our solution."

### Slide 2: Architecture (30 seconds)

"Our system ingests 5 real-time data streams - POS transactions, RFID readings, queue monitoring, product recognition, and inventory snapshots. We correlate events across streams using time-window analysis and session tracking to detect 9 types of anomalies."

### Slide 3: Live Demo (60 seconds)

"Let me show you the dashboard. [Open browser]

- Real-time events appear as they're detected
- Here's a Scanner Avoidance - RFID detected a product that wasn't scanned
- Weight Discrepancy - customer tried to pay for 400g item as 540g
- Long queue triggered - system recommends opening another checkout
- All events are logged to JSONL for compliance and analysis"

### Slide 4: Impact (10 seconds)

"Our solution reduces shrinkage, improves customer experience, and optimizes staffing - delivering measurable ROI within weeks."

**Total: 2 minutes ⏱️**

---

## 🚨 Emergency Fixes (Day-Of Hackathon)

### If Backend Won't Start

```bash
# Quick diagnostic
python -c "import flask, flask_socketio, pandas, numpy; print('✅ All imports OK')"

# If missing dependencies
pip install flask flask-socketio flask-cors pandas numpy

# Nuclear option: Use sentinel_detector.py standalone
python sentinel_detector.py
```

### If Frontend Won't Build

```bash
# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run dev

# If still fails, use simple HTML dashboard
# Copy from evidence/screenshots/ and show static version
```

### If Streaming Server Won't Run

```bash
# Check port availability
netstat -an | grep 8765

# Try different port
python stream_server.py --port 8766

# Update backend to connect to 8766
```

### If No Events Detected

```bash
# Lower thresholds for testing
# In anomaly_detector.py:
detection_thresholds = {
    'weight_tolerance': 0.5,     # More lenient (50%)
    'queue_length_threshold': 2, # Lower threshold
    'correlation_window': 60,    # Larger window
}
```

---

## 🎓 Key Takeaways

1. **Your core system is 90% complete** - Focus on testing and polish
2. **Event correlation is your secret weapon** - Highlight this in demo
3. **Algorithm tagging is mandatory** - Verify with grep before submission
4. **Output format must be exact** - Double-check JSONL structure
5. **Practice your demo** - 2 minutes goes fast!
6. **Have fallback plans** - Things break during demos

---

## 📞 Quick Reference

### Important File Paths

```
Backend:     src/backend/app.py
Frontend:    src/frontend/src/
Output:      evidence/output/final/events.jsonl
Screenshots: evidence/screenshots/
Demo Script: evidence/executables/run_demo.py
```

### Important Commands

```bash
# Start everything
./run_demo.py  # (create this!)

# Check logs
tail -f evidence/output/final/events.jsonl

# Verify algorithms
grep -R "@algorithm" src/
```

### Important URLs

```
Dashboard:   http://localhost:5173
Backend API: http://localhost:5000/api/events
Stream:      tcp://127.0.0.1:8765
```

---

**You've got this! Good luck with the hackathon! 🚀🎯**
