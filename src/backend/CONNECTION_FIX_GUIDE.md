# 🔧 Backend Connection Fix - Action Required

## 🐛 Problem Identified

Your backend was NOT automatically consuming events from the streaming server because:

1. **Streaming client wasn't auto-starting** - It only started when you manually hit the `/api/start_processing` endpoint
2. **No visual feedback** - You couldn't tell if events were being consumed
3. **Silent failures** - Connection errors weren't being logged clearly

## ✅ What I Fixed

### 1. Auto-Start Streaming Client (`app.py`)

**Before:** Streaming client only started if you called `/api/start_processing`

**After:** Streaming client now **automatically starts** when you run `python app.py`

```python
# Now in app.py __main__ block:
streaming_thread = threading.Thread(target=process_streaming_data, daemon=True)
streaming_thread.start()
```

### 2. Enhanced Logging (`app.py` & `streaming_client.py`)

Added comprehensive logging so you can see:

- ✅ When connection is established
- 📥 Event consumption progress (every 10 events)
- 🚨 Detected anomalies in real-time
- ❌ Any errors that occur

### 3. Better Error Handling

Added detailed error messages and traceback printing so you can diagnose issues quickly.

### 4. Created Diagnostic Tools

#### `test_stream_connection.py`

Quick test to verify streaming server is accessible:

```bash
python test_stream_connection.py
```

#### `check_system.py`

Comprehensive system status checker:

```bash
python check_system.py
```

## 🚀 How to Start Everything Correctly

### Step 1: Start Streaming Server (Terminal 1)

```bash
cd d:/ProjectSentinel/zebra/data/streaming-server
python stream_server.py --port 8765 --speed 10 --loop
```

**You should see:**

```
2025-10-04 12:29:10,642 [INFO] Loaded 5 combined events from 5 dataset(s)
2025-10-04 12:29:10,642 [INFO] Starting event stream on 0.0.0.0:8765
2025-10-04 12:29:10,642 [INFO] Server ready. Press Ctrl+C to stop.
```

### Step 2: Test Connection (Optional but Recommended)

```bash
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/backend
python test_stream_connection.py
```

**You should see:**

```
✅ Connected successfully!
📋 Banner:
   Service: project-sentinel-event-stream
   Datasets: ['POS_Transactions', 'RFID_data', ...]
```

### Step 3: Start Backend Server (Terminal 2)

```bash
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/backend
python app.py
```

**You should NOW see:**

```
🚀 Starting Project Sentinel Backend Server...
📊 Dashboard will be available at: http://localhost:3000
🔌 API available at: http://localhost:5000
🌊 Connecting to streaming server at: 127.0.0.1:8765
⚡ Auto-starting streaming client...
🔌 Attempting to connect to 127.0.0.1:8765...
✅ Connected to streaming server at 127.0.0.1:8765
📋 Stream Banner: ['POS_Transactions', 'RFID_data', ...] datasets available
📦 Event #1: Current_inventory_data @ 2025-08-13T16:00:00
📦 Event #2: POS_Transactions @ 2025-08-13T16:00:01
📥 Consumed 10 events from stream...
📥 Consumed 20 events from stream...
🚨 DETECTED: Long Queue Length at 2025-10-04T...
```

### Step 4: Check System Status

```bash
python check_system.py
```

This will show you the status of all components.

### Step 5: Start Frontend (Terminal 3)

```bash
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/frontend
npm run dev
```

## 🔍 Verification Checklist

### ✅ Streaming Server Is Working If:

- [ ] You see `[INFO] Starting loop cycle N` messages cycling through
- [ ] Loops are incrementing (55, 56, 57...)
- [ ] No error messages appear

### ✅ Backend Is Consuming Events If:

- [ ] You see `✅ Connected to streaming server`
- [ ] You see `📥 Consumed N events from stream...` messages
- [ ] Loop cycles in streaming server terminal show completion
- [ ] You see `🚨 DETECTED:` messages when anomalies are found

### ✅ Detection Is Working If:

- [ ] Console shows `🚨 DETECTED: [Event Type]` messages
- [ ] File `evidence/output/final/events.jsonl` is being created/updated
- [ ] Database `sentinel.db` is growing in size

### ✅ Frontend Is Receiving Data If:

- [ ] Dashboard loads without errors
- [ ] Events appear in real-time
- [ ] Station status updates
- [ ] No WebSocket connection errors in browser console

## 🐛 Troubleshooting

### Problem: "Connection refused" when starting backend

**Cause:** Streaming server isn't running

**Solution:**

```bash
# Start streaming server first
cd d:/ProjectSentinel/zebra/data/streaming-server
python stream_server.py --port 8765 --speed 10 --loop
```

### Problem: Backend starts but no "Consumed" messages

**Cause:** Streaming client thread may have crashed

**Check:**

1. Look for error messages after "Auto-starting streaming client..."
2. Check if port 8765 is already in use: `netstat -an | grep 8765`
3. Run `python test_stream_connection.py` to verify stream server

**Solution:**

```bash
# Kill any processes using port 8765
# Restart streaming server
# Restart backend
```

### Problem: Loops complete but no events detected

**Cause:** Detection thresholds might be too strict or data might not trigger anomalies

**Check:**

1. Look at `evidence/output/final/events.jsonl` - does it have content?
2. Check database: `sqlite3 sentinel.db "SELECT COUNT(*) FROM stream_data;"`
3. Lower detection thresholds in `anomaly_detector.py`

### Problem: Frontend doesn't show events

**Cause:** WebSocket connection issue

**Check:**

1. Browser console for WebSocket errors
2. Backend logs for "Client connected" messages
3. CORS settings in app.py

## 📊 Expected Output When Working

### Streaming Server Terminal:

```
2025-10-04 12:29:10,642 [INFO] Starting loop cycle 55
2025-10-04 12:29:11,150 [INFO] Completed loop cycle 55, starting next cycle
2025-10-04 12:29:11,150 [INFO] Starting loop cycle 56
2025-10-04 12:29:11,683 [INFO] Completed loop cycle 56, starting next cycle
```

**Note:** When backend is consuming, loops will complete faster!

### Backend Terminal:

```
📥 Consumed 10 events from stream...
📥 Consumed 20 events from stream...
📥 Consumed 30 events from stream...
🚨 DETECTED: Scanner Avoidance at 2025-10-04T...
🚨 DETECTED: Weight Discrepancies at 2025-10-04T...
📥 Consumed 40 events from stream...
```

### Output File Growth:

```bash
# Watch file grow in real-time
tail -f evidence/output/final/events.jsonl
```

## 🎯 Quick Test Commands

```bash
# Test 1: Is streaming server running?
curl -v telnet://127.0.0.1:8765

# Test 2: Is backend API running?
curl http://localhost:5000/api/health

# Test 3: How many events consumed?
curl http://localhost:5000/api/monitoring/consumption

# Test 4: Stream connection health?
curl http://localhost:5000/api/monitoring/stream-health

# Test 5: Check database
sqlite3 sentinel.db "SELECT COUNT(*) FROM stream_data;"
sqlite3 sentinel.db "SELECT COUNT(*) FROM events;"

# Test 6: Check output file
wc -l evidence/output/final/events.jsonl
```

## 📝 What Changed in Code

### Modified Files:

1. ✅ `app.py` - Auto-start streaming client, enhanced logging
2. ✅ `streaming_client.py` - Better connection logging and error handling

### New Files Created:

3. ✅ `test_stream_connection.py` - Quick connection test
4. ✅ `check_system.py` - Comprehensive system status checker

## 🚀 Next Steps

1. **Restart your backend** with the updated code
2. **Verify consumption** by checking the logs
3. **Monitor the output file** to see events being written
4. **Test the frontend** to see real-time updates

## 💡 Pro Tips

1. **Always start streaming server first** - Backend can't connect if server isn't running
2. **Watch both terminals** - You'll see loops complete in sync when working
3. **Use check_system.py** - Quick way to verify all components
4. **Tail the output file** - `tail -f events.jsonl` shows real-time detections
5. **Check database** - `sqlite3 sentinel.db` to verify data is being stored

---

**Ready to test? Run these commands in order:**

```bash
# Terminal 1
cd d:/ProjectSentinel/zebra/data/streaming-server
python stream_server.py --port 8765 --speed 10 --loop

# Terminal 2 (wait 2 seconds)
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/backend
python app.py

# Terminal 3 (check status)
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/backend
python check_system.py
```

**You should see events flowing through! Good luck! 🚀**
