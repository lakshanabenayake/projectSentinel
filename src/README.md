# Project Sentinel - React + Flask Implementation Guide

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Installation & Setup

1. **Install Backend Dependencies**

```bash
cd src/backend
pip install -r requirements.txt
```

2. **Install Frontend Dependencies**

```bash
cd src/frontend
npm install
```

3. **Start the Demo**

```bash
cd evidence/executables
python3 run_demo.py
```

This will:

- Install all dependencies
- Start Flask backend (port 5000)
- Start React frontend (port 3000)
- Start data streaming simulation
- Generate sample events
- Take dashboard screenshots

### Manual Development

**Backend (Terminal 1)**

```bash
cd src/backend
python app.py
```

**Frontend (Terminal 2)**

```bash
cd src/frontend
npm run dev
```

**Data Streaming (Terminal 3)**

```bash
cd ../../../data/streaming-server
python stream_server.py --port 8765 --speed 10 --loop
```

## 🏗️ Architecture

```
Team15_sentinel/
├── src/
│   ├── backend/           # Flask API + Socket.IO
│   │   ├── app.py         # Main server
│   │   ├── data_processor.py      # @algorithm Data Correlation
│   │   ├── anomaly_detector.py    # @algorithm Scanner Avoidance Detection
│   │   ├── event_generator.py     # @algorithm Event Formatting
│   │   └── streaming_client.py    # Data ingestion
│   └── frontend/          # React + TypeScript
│       ├── src/
│       │   ├── components/        # Dashboard UI
│       │   ├── hooks/            # Socket integration
│       │   └── stores/           # State management
└── evidence/
    ├── executables/run_demo.py   # Automation script
    ├── output/test/              # Test dataset results
    └── output/final/             # Final dataset results
```

## 🔧 Key Features

### Backend Algorithms (@algorithm tagged)

1. **Data Correlation** - Multi-stream sensor data correlation
2. **Scanner Avoidance Detection** - RFID vs POS validation
3. **Barcode Switching Detection** - EPC validation against catalog
4. **Weight Validation** - Product weight anomaly detection
5. **Queue Analysis** - Customer flow optimization
6. **Product Recognition Validation** - ML prediction validation
7. **Event Formatting** - Standardized JSONL output

### Frontend Components

- **Dashboard** - Real-time overview with Material-UI
- **AlertsPanel** - Security alerts and notifications
- **EventsPanel** - Live event feed
- **StationOverview** - Self-checkout status monitoring
- **RealTimeCharts** - Chart.js visualization
- **Socket Integration** - Live WebSocket updates

### Real-time Features

- WebSocket communication via Socket.IO
- Live event detection and alerts
- Real-time chart updates
- Station status monitoring
- Queue length tracking

## 📊 Data Flow

1. **Streaming Server** → Provides sample retail data
2. **Data Processor** → Correlates multi-stream events
3. **Anomaly Detector** → Identifies 7+ security/operational issues
4. **Event Generator** → Outputs standardized events.jsonl
5. **Socket.IO** → Broadcasts live updates to dashboard
6. **React Dashboard** → Visualizes real-time analytics

## 🎯 Event Detection

**Security Events:**

- Scanner Avoidance (RFID without POS)
- Barcode Switching (EPC validation failure)
- Weight Discrepancies (catalog mismatch)

**Operational Events:**

- Long Queue Length (>5 customers)
- Long Wait Time (>120 seconds)
- System Crashes (no activity detected)
- Inventory Discrepancies (stock mismatches)

**Resource Optimization:**

- Staffing Recommendations
- Checkout Station Actions (open/close)

## 🔍 Judging Criteria Alignment

1. **Design & Implementation** ✅

   - Clean modular architecture
   - TypeScript frontend with React
   - Python backend with proper error handling
   - Comprehensive documentation

2. **Algorithm Accuracy** ✅

   - 7 tagged algorithms (@algorithm comments)
   - Multi-stream correlation analysis
   - Statistical anomaly detection
   - Real-time processing pipeline

3. **Dashboard Quality** ✅

   - Professional Material-UI design
   - Real-time charts and visualizations
   - Alert system with priority levels
   - Responsive layout

4. **Solution Presentation** ✅
   - 2-minute demo script ready
   - Automated setup via run_demo.py
   - Clear value proposition
   - Technical depth demonstration

## 🚨 Demo Script (2 minutes)

**[0-15s]** "Project Sentinel - Real-time retail analytics platform"

- Show dashboard overview with live data

**[15-45s]** "Multi-stream anomaly detection"

- Demonstrate scanner avoidance detection
- Show barcode switching alerts
- Weight discrepancy validation

**[45-75s]** "Operational optimization"

- Queue monitoring and staffing recommendations
- Station status overview
- Inventory discrepancy detection

**[75-120s]** "Technical architecture"

- Real-time WebSocket updates
- 7 algorithmic detection methods
- Scalable Flask + React architecture

## 📋 Submission Checklist

- ✅ All algorithms tagged with `@algorithm Name | Purpose`
- ✅ Complete source code in `src/`
- ✅ Working `run_demo.py` automation
- ✅ Events.jsonl output format
- ✅ Dashboard screenshots
- ✅ README documentation

Ready for hackathon deployment! 🎉
