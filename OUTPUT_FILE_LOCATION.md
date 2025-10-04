# 📂 Output File Locations Guide

## 🎯 Primary Output File (For Submission)

Your **main output file** that will be judged is located at:

```
d:\ProjectSentinel\zebra\submission-structure\Team15_sentinel\evidence\output\final\events.jsonl
```

### Quick Access Commands:

**Windows Command Prompt:**

```cmd
cd d:\ProjectSentinel\zebra\submission-structure\Team15_sentinel\evidence\output\final
type events.jsonl
```

**PowerShell:**

```powershell
cd d:\ProjectSentinel\zebra\submission-structure\Team15_sentinel\evidence\output\final
Get-Content events.jsonl
```

**Git Bash:**

```bash
cd /d/ProjectSentinel/zebra/submission-structure/Team15_sentinel/evidence/output/final
cat events.jsonl
# Or watch it update in real-time:
tail -f events.jsonl
```

**VS Code:**

- Press `Ctrl+P` to open quick file search
- Type: `events.jsonl`
- Select: `evidence/output/final/events.jsonl`

## 📁 Directory Structure

```
Team15_sentinel/
├── evidence/
│   └── output/
│       ├── test/                    ← Output for TEST dataset
│       │   └── events.jsonl        (Will be created during test run)
│       └── final/                   ← Output for FINAL dataset
│           └── events.jsonl        ✅ YOUR MAIN OUTPUT FILE
```

## 🔧 How the Output File is Generated

### Current Configuration (in `sentinel_detector.py`):

```python
# Line 23
self.output_file = "evidence/output/final/events.json"  # ⚠️ Note: .json not .jsonl
```

### ⚠️ IMPORTANT: File Extension Issue

I noticed the code says `.json` but it should be `.jsonl`. Let me show you what needs to be fixed:

**Current (WRONG):**

```python
self.output_file = "evidence/output/final/events.json"
```

**Should be (CORRECT):**

```python
self.output_file = "evidence/output/final/events.jsonl"
```

The file IS being written in JSONL format (one JSON object per line), but the extension is wrong!

## 📊 How to View/Monitor Your Events

### Method 1: View in VS Code

1. Open the file explorer (Ctrl+Shift+E)
2. Navigate to: `evidence/output/final/events.jsonl`
3. Double-click to open

### Method 2: Real-Time Monitoring (Recommended!)

```bash
# Watch events appear in real-time
tail -f evidence/output/final/events.jsonl

# Or count total events
wc -l evidence/output/final/events.jsonl
```

### Method 3: Check via API

```bash
# Get recent events via backend API
curl http://localhost:5000/api/events?limit=10

# Get event statistics
curl http://localhost:5000/api/dashboard/stats
```

### Method 4: Check Database

```bash
# How many events in database?
sqlite3 src/backend/sentinel.db "SELECT COUNT(*) FROM events;"

# View latest 5 events
sqlite3 src/backend/sentinel.db "SELECT event_name, timestamp FROM events ORDER BY created_at DESC LIMIT 5;"
```

## 🗂️ Multiple Output Locations (Explained)

You might find `events.jsonl` in several places. Here's what each is:

| Location                              | Purpose                                | Keep/Delete                                |
| ------------------------------------- | -------------------------------------- | ------------------------------------------ |
| `evidence/output/final/events.jsonl`  | **MAIN OUTPUT - FOR FINAL SUBMISSION** | ✅ **KEEP - THIS IS WHAT JUDGES EVALUATE** |
| `evidence/output/test/events.jsonl`   | Output from test dataset run           | ✅ Keep - needed for submission            |
| `zebra/runs/data/output/events.jsonl` | Old test runs                          | ❌ Can delete - not for submission         |
| `zebra/data/output/events.jsonl`      | Reference/example file                 | ℹ️ Reference only - don't modify           |

## 🎯 For Hackathon Submission

### You Need TWO Files:

1. **Test Dataset Output:**

   ```
   evidence/output/test/events.jsonl
   ```

   Generated when you process the TEST dataset

2. **Final Dataset Output:**
   ```
   evidence/output/final/events.jsonl
   ```
   Generated when you process the FINAL dataset (given 10 min before end)

### How to Generate Them:

#### For Test Dataset:

```bash
# Modify sentinel_detector.py to output to test folder
# Then run with test dataset
python app.py
```

#### For Final Dataset:

```bash
# Use final folder (default)
python app.py
```

## 🔍 Quick Verification Commands

```bash
# Navigate to project root
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel

# Check if output files exist
ls -la evidence/output/final/events.jsonl
ls -la evidence/output/test/events.jsonl

# Count events in each file
wc -l evidence/output/final/events.jsonl
wc -l evidence/output/test/events.jsonl

# View first 5 events
head -n 5 evidence/output/final/events.jsonl

# View last 5 events
tail -n 5 evidence/output/final/events.jsonl

# Verify JSON format
cat evidence/output/final/events.jsonl | jq '.' | head -n 20
```

## 📝 Expected Output Format

Each line should look like this:

```json
{
  "timestamp": "2025-10-04T06:59:20.506181",
  "event_id": "E147",
  "event_data": {
    "event_name": "Weight Discrepancies",
    "station_id": "SCC1",
    "customer_id": "UNKNOWN",
    "product_sku": "PRD_F_14",
    "expected_weight": 540.0,
    "actual_weight": 400.0
  }
}
```

**Key Requirements:**

- ✅ One JSON object per line (JSONL format)
- ✅ Each has: `timestamp`, `event_id`, `event_data`
- ✅ Event IDs are sequential: E001, E002, E003...
- ✅ Timestamps are ISO 8601 format
- ✅ Event data includes `event_name` and relevant fields

## 🚨 Common Issues

### Issue 1: File Not Found

**Symptom:** Can't find `events.jsonl`

**Solution:**

```bash
# Check current directory
pwd

# Navigate to correct location
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel

# List output directory
ls -la evidence/output/final/
```

### Issue 2: File is Empty

**Symptom:** File exists but has 0 bytes

**Solution:**

- Backend might not be running
- No events detected yet (need to run longer)
- Check if streaming server is connected
- Check backend logs for errors

### Issue 3: Wrong File Extension

**Symptom:** File is `events.json` instead of `events.jsonl`

**Solution:**
Fix in `sentinel_detector.py` line 23:

```python
self.output_file = "evidence/output/final/events.jsonl"  # Change .json to .jsonl
```

### Issue 4: Events Not Appearing

**Symptom:** Backend running but file not updating

**Solution:**

```bash
# Check if sentinel_detector is writing events
grep "write_event" src/backend/app.py

# Check if output directory is writable
touch evidence/output/final/test.txt
rm evidence/output/final/test.txt

# Check backend logs for write errors
```

## 🎓 Quick Reference

**Primary Output Location (Relative Path):**

```
evidence/output/final/events.jsonl
```

**Absolute Path:**

```
d:\ProjectSentinel\zebra\submission-structure\Team15_sentinel\evidence\output\final\events.jsonl
```

**From Backend Directory:**

```
cd src/backend
ls -la ../../evidence/output/final/events.jsonl
```

**Watch Live Updates:**

```bash
tail -f evidence/output/final/events.jsonl
```

**Count Total Events:**

```bash
wc -l evidence/output/final/events.jsonl
```

---

## ✅ Action Items

1. **Navigate to output directory:**

   ```bash
   cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/evidence/output/final
   ```

2. **Check if file exists:**

   ```bash
   ls -la events.jsonl
   ```

3. **View contents:**

   ```bash
   cat events.jsonl
   # Or in VS Code: Ctrl+P → type "events.jsonl"
   ```

4. **Watch real-time updates:**
   ```bash
   tail -f events.jsonl
   ```

That's it! Your output file is at:
**`evidence/output/final/events.jsonl`** ✨
