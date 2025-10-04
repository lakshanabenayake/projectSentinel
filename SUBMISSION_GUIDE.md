# Submission Guide

Complete this template before zipping your submission. Keep the file at the
project root.

## Team details

- Team name: Team15 Sentinel Solutions
- Members: [Your Team Member Names Here]
- Primary contact email: [Your Contact Email]

## Judge run command

Judges will `cd evidence/executables/` and run **one command** on Ubuntu 24.04:

```
python3 run_demo.py
```

The script will:

1. Install Python and Node.js dependencies
2. Start Flask backend server (port 5000)
3. Build and serve React frontend (port 3000)
4. Process test and final datasets
5. Generate events.jsonl output files
6. Create dashboard screenshots

## System Overview

### Architecture

- **Backend**: Flask REST API + Socket.IO for real-time streaming
- **Frontend**: React TypeScript dashboard with Material-UI
- **Processing**: Multi-threaded anomaly detection algorithms
- **Database**: SQLite for data storage and correlation
- **Output**: Standardized events.jsonl format

### Key Algorithms Implemented

- Scanner Avoidance Detection (correlation analysis)
- Barcode Switching Detection (product recognition validation)
- Weight Discrepancy Analysis (statistical outlier detection)
- Queue Optimization (customer flow analysis)
- Resource Allocation (predictive staffing algorithms)

## Checklist before zipping and submitting

- Algorithms tagged with `# @algorithm Name | Purpose` comments: ✓ 7 algorithms implemented
  - Data Correlation (data_processor.py)
  - Scanner Avoidance Detection (anomaly_detector.py)
  - Barcode Switching Detection (anomaly_detector.py)
  - Weight Validation (data_processor.py)
  - Queue Analysis (anomaly_detector.py)
  - Product Recognition Validation (anomaly_detector.py)
  - Event Formatting (event_generator.py)
- Evidence artefacts present in `evidence/`: ✓ Screenshots, outputs, executables ready
- Source code complete under `src/`: ✓ Backend (Flask), frontend (React), automation script included
