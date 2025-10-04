# 🔧 Customer ID "UNKNOWN" Issue - Fixed

## ❓ Problem

You were getting `customer_id: "UNKNOWN"` in many of your output events, especially for:

- Weight Discrepancies
- Scanner Avoidance
- Other detection events

## 🔍 Root Cause

The issue was in `sentinel_detector.py` line 65. The code was looking for `customer_id` at the wrong level in the data structure.

### Data Structure (from streaming server):

```json
{
  "dataset": "POS_Transactions",
  "sequence": 1,
  "timestamp": "2025-08-13T16:08:40",
  "event": {
    "timestamp": "2025-08-13T16:08:40",
    "station_id": "SCC1",
    "status": "Active",
    "data": {
      "customer_id": "C056",  ← customer_id is HERE!
      "sku": "PRD_F_14",
      "product_name": "Nestomalt (400g)",
      "barcode": "4792024011348",
      "price": 540.0,
      "weight_g": 400.0
    }
  }
}
```

### What Was Wrong:

```python
# BEFORE (WRONG):
ev = streaming_event.get("event", {})
cust = ev.get("customer_id", "UNKNOWN")  # Looking at wrong level!
```

This was looking for `customer_id` directly in `event`, but it's actually inside `event.data`!

### What Was Fixed:

```python
# AFTER (CORRECT):
ev = streaming_event.get("event", {})
data = ev.get("data", {})
cust = data.get("customer_id") or ev.get("customer_id", "UNKNOWN")
```

Now it:

1. First checks `event.data.customer_id` (for POS transactions)
2. Falls back to `event.customer_id` (for other datasets)
3. Only uses "UNKNOWN" if neither exists

---

## ✅ Expected Behavior After Fix

### Before Fix:

```json
{
  "timestamp": "2025-10-04T08:04:00.613189",
  "event_id": "E001",
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

### After Fix:

```json
{
  "timestamp": "2025-10-04T08:04:00.613189",
  "event_id": "E001",
  "event_data": {
    "event_name": "Weight Discrepancies",
    "station_id": "SCC1",
    "customer_id": "C056",
    "product_sku": "PRD_F_14",
    "expected_weight": 540.0,
    "actual_weight": 400.0
  }
}
```

✅ Now shows `"customer_id": "C056"` instead of `"UNKNOWN"`!

---

## 🧪 How to Test the Fix

### Step 1: Clean Old Output

```bash
cd d:/ProjectSentinel/zebra/submission-structure/Team15_sentinel/src/backend
rm evidence/output/final/events.json
```

### Step 2: Restart Backend

```bash
python app.py
```

### Step 3: Check New Events

```bash
# Watch new events being generated
tail -f evidence/output/final/events.json

# Or grep for customer IDs
grep -o '"customer_id":"[^"]*"' evidence/output/final/events.json | sort | uniq -c
```

### Step 4: Verify Customer IDs

You should now see actual customer IDs like:

- `"customer_id": "C056"`
- `"customer_id": "C048"`
- `"customer_id": "C044"`
- `"customer_id": "C006"`

Instead of all being `"UNKNOWN"`

---

## 📊 When You'll Still See "UNKNOWN"

You might still see `"UNKNOWN"` in some cases, which is **EXPECTED**:

### Case 1: Events Without Customer Context

Some events don't have an associated customer:

```json
// Queue Length - no specific customer
{"event_name": "Long Queue Length", "station_id": "SCC1", "num_of_customers": 6}

// System Crash - affects station, not customer
{"event_name": "Unexpected Systems Crash", "station_id": "SCC1", "duration_seconds": 180}

// Inventory Discrepancy - system-level issue
{"event_name": "Inventory Discrepancy", "SKU": "PRD_F_03", "Expected_Inventory": 150, "Actual_Inventory": 120}
```

For these, `"UNKNOWN"` or no customer_id is **correct**!

### Case 2: RFID Data Without Customer

RFID readings often don't have customer IDs in the raw data:

```json
// RFID reading
{
  "timestamp": "2025-08-13T16:00:00",
  "station_id": "SCC1",
  "status": "Active",
  "data": { "epc": null, "location": null, "sku": null }
}
```

For RFID-based detections without POS correlation, you might still see "UNKNOWN" - this is normal!

---

## 🎯 Verification Checklist

Run these checks after restarting:

### Check 1: Count Customer IDs

```bash
grep -o '"customer_id":"[^"]*"' evidence/output/final/events.json | wc -l
```

Should show many customer IDs

### Check 2: See Actual Customer IDs

```bash
grep -o '"customer_id":"C[0-9]*"' evidence/output/final/events.json | head -20
```

Should show: `"customer_id":"C056"`, `"customer_id":"C048"`, etc.

### Check 3: Count UNKNOWNs

```bash
grep -c '"customer_id":"UNKNOWN"' evidence/output/final/events.json
```

Should be much lower (only for events without customer context)

### Check 4: Compare Event Types

```bash
# Events WITH customer IDs (should be POS-related)
grep '"customer_id":"C[0-9]*"' evidence/output/final/events.json | grep -o '"event_name":"[^"]*"' | sort | uniq -c

# Events WITHOUT customer IDs (system/queue events)
grep '"customer_id":"UNKNOWN"' evidence/output/final/events.json | grep -o '"event_name":"[^"]*"' | sort | uniq -c
```

---

## 🔍 Why This Matters

### For Judging:

- ✅ Shows your system properly correlates POS transactions with customers
- ✅ Demonstrates data extraction accuracy
- ✅ Enables customer behavior pattern analysis
- ✅ Allows tracking fraud by specific customers

### For Analysis:

With proper customer IDs, you can now:

- Track which customers trigger most anomalies
- Identify repeat offenders
- Analyze customer shopping patterns
- Generate customer-specific reports

---

## 📝 Data Structure Reference

### POS Transactions (has customer_id):

```json
{
  "event": {
    "station_id": "SCC1",
    "status": "Active",
    "data": {
      "customer_id": "C056",  ← HERE
      "sku": "PRD_F_14",
      "weight_g": 400.0
    }
  }
}
```

### RFID Readings (usually no customer_id):

```json
{
  "event": {
    "station_id": "SCC1",
    "status": "Active",
    "data": {
      "epc": "E280116060000000000004486",
      "location": "IN_SCAN_AREA",
      "sku": "PRD_T_03"
      // No customer_id!
    }
  }
}
```

### Queue Monitoring (no customer_id):

```json
{
  "event": {
    "station_id": "SCC1",
    "status": "Active",
    "data": {
      "customer_count": 1,
      "average_dwell_time": 44.1
      // No customer_id!
    }
  }
}
```

---

## ✅ Summary

**Problem:** `customer_id` was always "UNKNOWN" because code looked at wrong data level

**Fix:** Updated `sentinel_detector.py` line 65 to check `event.data.customer_id` first

**Result:** Now correctly extracts customer IDs from POS transactions

**Action:** Restart backend to generate new events with proper customer IDs

---

## 🚀 Next Steps

1. **Stop your backend** (Ctrl+C)
2. **Delete old output:**
   ```bash
   rm src/backend/evidence/output/final/events.json
   ```
3. **Restart backend:**
   ```bash
   cd src/backend
   python app.py
   ```
4. **Verify new events have customer IDs:**
   ```bash
   tail -f evidence/output/final/events.json
   ```

**You should now see real customer IDs like C056, C048, etc.!** 🎉
