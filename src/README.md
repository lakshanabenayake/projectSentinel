# Project Sentinel - Real-time Store Monitoring Dashboard

A comprehensive retail analytics and anomaly detection system with real-time dashboard capabilities.

## 🚀 Quick Start

Run the complete system with one command:

```bash
cd evidence/executables/
python3 run_demo.py
```

This will:
1. Install all Python and Node.js dependencies
2. Start the data streaming server (port 8765)
3. Launch the Flask backend with integrated event detection (port 5000)
4. Build and serve the React dashboard (port 3000)
5. Generate events.jsonl output files
6. Create dashboard screenshots for evidence

## 🏗️ Architecture

### Backend (Flask + Socket.IO)
- **Real-time Event Detection**: Integrates the anomaly detection logic from `serve1.py`
- **WebSocket Streaming**: Live event broadcasting to dashboard clients
- **REST API**: Configuration and historical data endpoints
- **Multi-threaded Processing**: Concurrent stream processing and client handling

### Frontend (React + TypeScript + Material-UI)
- **Real-time Dashboard**: Live visualization of store metrics and alerts
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Interactive Charts**: Queue analytics, event distribution, and trends
- **Alert Management**: Priority-based alert system with acknowledgments

### Data Flow
```
Raw Data Stream → Event Detection → WebSocket Broadcasting → Dashboard Visualization
     (8765)            (Flask)           (Socket.IO)           (React)
```

## 📊 Key Features

### Anomaly Detection Algorithms
- **Scanner Avoidance Detection**: Identifies items detected by RFID but not scanned
- **Barcode Switching Detection**: Validates scanned vs recognized products
- **Weight Discrepancy Analysis**: Statistical analysis of weight mismatches
- **Queue Optimization**: Customer flow analysis and wait time prediction
- **Inventory Monitoring**: Real-time stock level validation
- **System Health Monitoring**: Crash detection and performance metrics

### Dashboard Components
- **Store Overview**: Real-time metrics and KPIs
- **Station Monitoring**: Individual checkout station status
- **Live Alerts Panel**: Priority-based alert system
- **Event Stream**: Real-time event feed with filtering
- **Analytics Charts**: Queue trends, event distribution
- **Real-time Indicators**: Connection status and live data badges

## 🔧 Technical Details

### Backend Stack
- **Flask 2.3.3**: Web framework
- **Flask-SocketIO 5.3.6**: Real-time WebSocket support
- **Flask-CORS 4.0.0**: Cross-origin resource sharing
- **Python Socket Library**: Data stream consumption
- **Threading**: Concurrent processing

### Frontend Stack
- **React 18.2.0**: UI framework
- **TypeScript**: Type safety
- **Material-UI 5.14.15**: Component library
- **Chart.js + React-ChartJS-2**: Data visualization
- **Socket.IO-Client**: Real-time communication
- **Vite**: Build tool and development server

### Event Detection Integration
The backend integrates the complete event detection logic from `serve1.py`:
- Connects to streaming server on port 8765
- Processes events using the same algorithms
- Maintains state stores for RFID, POS, and inventory data
- Broadcasts detected events via WebSocket in real-time

### Algorithm Documentation
All algorithms are properly tagged with `# @algorithm Name | Purpose` comments:
- **Data Correlation**: Correlates RFID, POS, and product recognition data
- **Scanner Avoidance Detection**: Advanced pattern analysis for theft detection
- **Barcode Switching Detection**: ML-based product recognition validation
- **Weight Validation**: Statistical analysis of weight discrepancies
- **Queue Analysis**: Predictive queue management and optimization
- **Product Recognition Validation**: Computer vision validation algorithms
- **Event Formatting**: Standardizes event structure and metadata

## 📁 Project Structure

```
src/
├── backend/                    # Flask backend application
│   ├── app.py                 # Main Flask app with integrated detection
│   ├── anomaly_detector.py    # Advanced anomaly detection algorithms
│   ├── data_processor.py      # Data correlation and validation
│   ├── event_generator.py     # Event creation and formatting
│   ├── streaming_client.py    # Robust stream client with reconnection
│   └── requirements.txt       # Python dependencies
└── frontend/                  # React dashboard application
    ├── src/
    │   ├── components/        # React components
    │   │   ├── Dashboard.tsx         # Main metrics overview
    │   │   ├── AlertsPanel.tsx       # Live alerts display
    │   │   ├── EventsPanel.tsx       # Event feed
    │   │   ├── StationOverview.tsx   # Station status grid
    │   │   └── RealTimeCharts.tsx    # Analytics visualizations
    │   ├── hooks/
    │   │   └── useSocket.ts          # WebSocket connection hook
    │   ├── stores/
    │   │   └── dashboardStore.ts     # State management
    │   ├── App.tsx                   # Main application component
    │   └── main.tsx                  # Application entry point
    ├── package.json           # Node.js dependencies
    ├── vite.config.ts         # Build configuration
    └── tsconfig.json          # TypeScript configuration
```

## 🎯 Real-time Features

### Live Event Detection
- Scanner avoidance patterns
- Barcode switching incidents
- Weight discrepancies
- Long queue formations
- System crashes and errors
- Inventory discrepancies
- Staffing recommendations

### Dashboard Analytics
- Active station monitoring
- Customer flow visualization
- Alert priority management
- Queue length trends
- Wait time analysis
- Event distribution charts
- System health metrics

### Performance Optimizations
- Efficient WebSocket broadcasting
- Event batching and throttling
- Client-side data caching
- Automatic reconnection handling
- Real-time chart updates without flickering

## 🚦 System Status Indicators

- **🟢 Connected**: Live data streaming active
- **🔴 LIVE**: Real-time indicator with pulse animation
- **⚠️ Alerts**: Priority-based color coding (Critical/Warning/Info)
- **📊 Metrics**: Auto-updating counters and progress bars

## 📈 Event Types Detected

1. **Security Events** (Critical Priority)
   - Scanner Avoidance
   - Barcode Switching
   - System Crashes

2. **Operational Events** (Warning Priority)
   - Long Queue Length
   - Extended Wait Times
   - Weight Discrepancies
   - Staffing Needs

3. **Inventory Events** (Warning Priority)
   - Stock Discrepancies
   - Inventory Alerts

4. **Success Events** (Info Priority)
   - Normal Operations
   - Successful Transactions

## 🔧 Configuration

### Backend Configuration
- Stream server host/port: Configurable in `app.py`
- WebSocket settings: CORS origins, connection limits
- Event thresholds: Queue length, wait times, weight tolerance
- Alert priorities: Configurable severity levels

### Frontend Configuration
- API endpoints: Backend connection settings
- Chart refresh rates: Visualization update frequencies
- Alert display: Maximum alerts shown, auto-refresh intervals
- Theme customization: Material-UI theme configuration

## 📊 Output Files

The system generates standardized `events.jsonl` files in:
- `evidence/output/test/events.jsonl` - Test dataset results
- `evidence/output/final/events.jsonl` - Final dataset results

Each event follows the format:
```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "event_id": "E001",
  "event_data": {
    "event_name": "Scanner Avoidance",
    "station_id": "SCC1",
    "customer_id": "C001",
    "product_sku": "PRD_F_03"
  }
}
```

## 🐛 Troubleshooting

### Backend Issues
- Check if streaming server is running on port 8765
- Verify Flask dependencies are installed
- Ensure no port conflicts on 5000

### Frontend Issues
- Verify Node.js and npm are installed
- Check if port 3000 is available
- Ensure backend is running before starting frontend

### Connection Issues
- WebSocket connection problems: Check CORS configuration
- Data not updating: Verify streaming server is providing data
- Performance issues: Check event batching and throttling settings

## 🏆 Submission Compliance

This implementation follows all submission guidelines:
- ✅ Single command execution: `python3 run_demo.py`
- ✅ Flask backend on port 5000
- ✅ React frontend on port 3000
- ✅ Algorithm documentation with `# @algorithm` tags
- ✅ Multi-threaded processing
- ✅ SQLite data storage capability
- ✅ Standardized events.jsonl output
- ✅ Evidence artifacts generation

## 📞 Support

For technical support or questions about the implementation, please refer to the algorithm documentation in the source code files.