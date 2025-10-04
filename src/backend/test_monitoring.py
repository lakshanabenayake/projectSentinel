#!/usr/bin/env python3
"""
Test script to check event consumption monitoring
"""
import requests
import json

def test_consumption_endpoint():
    try:
        response = requests.get('http://127.0.0.1:5000/api/monitoring/consumption')
        if response.status_code == 200:
            print("✅ Consumption Monitoring:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_stream_health_endpoint():
    try:
        response = requests.get('http://127.0.0.1:5000/api/monitoring/stream-health')
        if response.status_code == 200:
            print("\n✅ Stream Health Monitoring:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_basic_health():
    try:
        response = requests.get('http://127.0.0.1:5000/api/health')
        if response.status_code == 200:
            print("✅ Basic Health Check:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    print("=== Project Sentinel Backend Monitoring Test ===\n")
    test_basic_health()
    test_consumption_endpoint()
    test_stream_health_endpoint()