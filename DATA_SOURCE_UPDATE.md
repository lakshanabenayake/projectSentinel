# 🔄 Streaming Server Data Source Update

## ✅ What Changed

The streaming server has been updated to use the **NEW dataset** from `data/input/new/` folder.

### Before:

```python
default=Path(__file__).resolve().parent.parent / "input"
```

**Path:** `d:/ProjectSentinel/zebra/data/input/`

### After:

```python
default=Path(__file__).resolve().parent.parent / "input" / "new"
```

**Path:** `d:/ProjectSentinel/zebra/data/input/new/`

---

## 📂 Data Files in NEW Folder

```
d:/ProjectSentinel/zebra/data/input/new/
├── inventory_snapshots.jsonl
├── pos_transactions.jsonl
├── product_recognition.jsonl
├── queue_monitoring.jsonl
└── rfid_readings.jsonl
```

✅ All 5 required data streams are present!

---

## 🚀 How to Run with NEW Data

### Method 1: Use Default (NEW folder - now automatic)

```bash
cd d:/ProjectSentinel/zebra/data/streaming-server
python stream_server.py --port 8765 --speed 10 --loop
```

This will automatically use the **NEW** dataset from `data/input/new/`

### Method 2: Explicitly Specify NEW Folder

```bash
python stream_server.py --data-root ../input/new --port 8765 --speed 10 --loop
```

### Method 3: Use OLD/Original Data (if needed)

```bash
python stream_server.py --data-root ../input --port 8765 --speed 10 --loop
```

---

## 🔍 Verify Data Source

When you start the server, you'll see:

```
2025-10-04 12:30:00,000 [INFO] Loaded N combined events from 5 dataset(s)
```

Check the log output to confirm which data files are being loaded.

### To verify manually:

```bash
cd d:/ProjectSentinel/zebra/data/input/new
ls -la *.jsonl
```

You should see:

```
-rw-r--r-- inventory_snapshots.jsonl
-rw-r--r-- pos_transactions.jsonl
-rw-r--r-- product_recognition.jsonl
-rw-r--r-- queue_monitoring.jsonl
-rw-r--r-- rfid_readings.jsonl
```

---

## 📊 Differences Between OLD and NEW Datasets

### Purpose:

- **`data/input/`** - Initial/training dataset for development
- **`data/input/new/`** - TEST dataset for evaluation (used during hackathon)

### When to Use Each:

| Dataset            | Use Case                                    | Command                                                                      |
| ------------------ | ------------------------------------------- | ---------------------------------------------------------------------------- |
| **NEW** (default)  | Testing, evaluation, generating test output | `python stream_server.py --port 8765 --speed 10 --loop`                      |
| **OLD** (original) | Development, reference                      | `python stream_server.py --data-root ../input --port 8765 --speed 10 --loop` |

---

## ✅ Complete Startup Sequence (Updated)

### Terminal 1: Start Streaming Server with NEW Data

```bash
cd d:/ProjectSentinel/zebra/data/streaming-server
python stream_server.py --port 8765 --speed 10 --loop
```

**Expected Output:**

```
2025-10-04 12:30:00,000 [INFO] Loaded N combined events from 5 dataset(s) (loop=True, speed=10x, cycle=Xs)
2025-10-04 12:30:00,000 [INFO] Starting event stream on 0.0.0.0:8765
2025-10-04 12:30:00,000 [INFO] Server ready. Press Ctrl+C to stop.
```

### Terminal 2: Start Backend (will consume from NEW data)

```bash
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/backend
python app.py
```

**Expected Output:**

```
🚀 Starting Project Sentinel Backend Server...
⚡ Auto-starting streaming client...
🔌 Attempting to connect to 127.0.0.1:8765...
✅ Connected to streaming server at 127.0.0.1:8765
📋 Stream Banner: ['POS_Transactions', 'RFID_data', ...] datasets available
📥 Consumed 10 events from stream...
```

### Terminal 3: Check Output

```bash
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel
tail -f evidence/output/final/events.jsonl
```

---

## 🎯 For Hackathon TEST Dataset

When you receive the TEST dataset during the hackathon:

1. **Place files in:** `d:/ProjectSentinel/zebra/data/input/new/`

   - inventory_snapshots.jsonl
   - pos_transactions.jsonl
   - product_recognition.jsonl
   - queue_monitoring.jsonl
   - rfid_readings.jsonl

2. **Restart streaming server:**

   ```bash
   # Stop current server (Ctrl+C)
   python stream_server.py --port 8765 --speed 10 --loop
   ```

3. **Update backend output path for test:**
   In `sentinel_detector.py`:

   ```python
   self.output_file = "evidence/output/test/events.jsonl"
   ```

4. **Restart backend:**

   ```bash
   python app.py
   ```

5. **Wait for processing to complete**

6. **Verify output:**
   ```bash
   cat evidence/output/test/events.jsonl
   wc -l evidence/output/test/events.jsonl
   ```

---

## 🎯 For Hackathon FINAL Dataset

When you receive the FINAL dataset (10 minutes before end):

1. **Place files in:** `d:/ProjectSentinel/zebra/data/input/new/`

2. **Ensure output path is FINAL:**
   In `sentinel_detector.py`:

   ```python
   self.output_file = "evidence/output/final/events.jsonl"
   ```

3. **Restart everything:**

   ```bash
   # Terminal 1: Streaming Server
   python stream_server.py --port 8765 --speed 50 --loop  # Faster speed!

   # Terminal 2: Backend
   python app.py
   ```

4. **Monitor progress:**

   ```bash
   tail -f evidence/output/final/events.jsonl
   ```

5. **Stop after sufficient events generated**

---

## 🔧 Troubleshooting

### Issue: "Data directory not found"

**Error:** `Data directory not found: .../input/new`

**Solution:**

```bash
# Check if new folder exists
ls -la d:/ProjectSentinel/zebra/data/input/new/

# If missing, create it
mkdir -p d:/ProjectSentinel/zebra/data/input/new/

# Copy data files
cp d:/ProjectSentinel/zebra/data/input/*.jsonl d:/ProjectSentinel/zebra/data/input/new/
```

### Issue: "No dataset files found to stream"

**Error:** `No dataset files found to stream.`

**Solution:**

```bash
# Verify files exist
cd d:/ProjectSentinel/zebra/data/input/new
ls -la *.jsonl

# Should show 5 files
```

### Issue: Want to switch back to OLD data

**Solution:**

```bash
# Use --data-root flag
python stream_server.py --data-root ../input --port 8765 --speed 10 --loop
```

---

## 📋 Quick Reference

**Default Data Source (NEW):**

```
d:/ProjectSentinel/zebra/data/input/new/
```

**Start Command:**

```bash
cd d:/ProjectSentinel/zebra/data/streaming-server
python stream_server.py --port 8765 --speed 10 --loop
```

**Override Data Source:**

```bash
python stream_server.py --data-root ../input --port 8765 --speed 10 --loop
```

**Check What's Being Loaded:**

```bash
# Look for this line in server output:
[INFO] Loaded N combined events from 5 dataset(s)
```

---

## ✅ Summary

✅ Streaming server now uses `data/input/new/` by default  
✅ All 5 data files are present in NEW folder  
✅ No changes needed to your startup commands  
✅ Can still override with `--data-root` flag if needed  
✅ Ready for TEST and FINAL dataset processing

**You're all set!** Just restart your streaming server to use the NEW data. 🚀
