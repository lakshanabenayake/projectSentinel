# Project Sentinel Demo - Execution Guide

## 🚀 Quick Start Options

### Option 1: Automated Setup (Recommended)
```bash
# Windows users
setup_and_run.bat

# Linux/Mac users  
python run_demo.py
```

### Option 2: Standalone Version (No Dependencies)
```bash
python run_standalone.py
```

### Option 3: Test Setup First
```bash
python test_setup.py
```

## 📊 What You Get

### Full Version (run_demo.py)
- ✅ Flask backend with advanced anomaly detection
- ✅ Real-time WebSocket streaming
- ✅ React dashboard (if Node.js available)
- ✅ Complete event processing pipeline

### Standalone Version (run_standalone.py)  
- ✅ Python-only backend (no external dependencies)
- ✅ Built-in HTML dashboard
- ✅ Core event detection algorithms
- ✅ REST API endpoints
- ✅ Works even without pip access

## 🌐 Access Points

Once running, you can access:

- **Dashboard**: http://localhost:5000 (or :3000 for React version)
- **API Health**: http://localhost:5000/api/health
- **Metrics**: http://localhost:5000/api/metrics
- **Events**: http://localhost:5000/api/events

## 🔧 Troubleshooting

### Pip Installation Issues
If you see errors like:
```
CRITICAL: Failed to install flask>=2.0.0
```

**Solution**: Use the standalone version:
```bash
python run_standalone.py
```

### Port Already in Use
If port 5000 is busy, the standalone version will try other ports automatically.

### No Node.js/npm
The system will run backend-only mode with a built-in dashboard.

## 📁 Output Files

Both versions generate:
- `evidence/output/final/events.jsonl` - Detected events
- `evidence/output/test/events.jsonl` - Test dataset results

## 🎯 Features Demonstrated

### Event Detection
- Scanner Avoidance Detection
- Barcode Switching Detection  
- Weight Discrepancy Analysis
- Queue Length Monitoring
- System Health Monitoring
- Inventory Discrepancy Tracking

### Dashboard Features
- Real-time metrics display
- Live event feed
- Station status monitoring
- Alert management system
- Auto-refreshing data

## ⚡ Performance Notes

- **Standalone version**: Lightweight, uses only Python standard library
- **Full version**: More features but requires external packages
- Both versions implement the same core detection algorithms from `serve1.py`

## 🔍 Viewing Results

The detected events follow this format:
```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "event_id": "E001", 
  "event_data": {
    "event_name": "Scanner Avoidance",
    "station_id": "SCC1",
    "customer_id": "C001",
    "product_sku": "PRD_F_03"
  },
  "priority": "warning"
}
```

## 🆘 Support

If both versions fail to start:
1. Check Python version: `python --version` (requires 3.7+)
2. Try running from different directory
3. Check firewall/antivirus blocking port 5000
4. Run `python test_setup.py` for detailed diagnostics