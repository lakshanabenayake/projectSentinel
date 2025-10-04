#!/usr/bin/env python3
"""
Project Sentinel - Run Demo
Consumes event stream, detects all events, writes to events.jsonl, prints to console
"""

import argparse
import json
import socket
import os
from datetime import datetime
from typing import Iterator, Dict, Any

OUTPUT_FILE = "data/output/events.jsonl"
EVENT_COUNTER = 0

# --- State Stores ---
seen_rfids = {}            # customer_id -> set of SKUs detected by RFID
scanned_items = {}         # customer_id -> set of SKUs scanned at POS
expected_weights = {}      # customer_id -> total expected weight
inventory_snapshot = {}    # SKU -> expected inventory

# --- Utilities ---
def read_events(host: str, port: int) -> Iterator[dict]:
    """Generator that yields JSON events from stream server"""
    with socket.create_connection((host, port)) as conn:
        with conn.makefile("r", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                yield json.loads(line)


def write_event(event_name: str, data: Dict[str, Any]):
    """Write event to events.jsonl and print"""
    global EVENT_COUNTER
    EVENT_COUNTER += 1
    event_id = f"E{EVENT_COUNTER:03d}"
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_id": event_id,
        "event_data": {"event_name": event_name, **data}
    }
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    # print to console
    print(json.dumps(event, indent=2))


# --- Detection Logic ---
def detect(event: dict):
    dataset = event.get("dataset", "")
    ev = event.get("event", {})
    status = ev.get("status")
    station = ev.get("station_id", "UNKNOWN")
    cust = ev.get("customer_id", "UNKNOWN")

    # 1. RFID data
    if dataset.lower() == "rfid_data" and status == "Active":
        sku = ev["data"].get("sku")
        if sku:
            seen_rfids.setdefault(cust, set()).add(sku)

    # 2. POS transactions
    if dataset.lower() == "pos_transactions":
        sku = ev["data"].get("sku")
        scanned_items.setdefault(cust, set()).add(sku)
        weight = ev["data"].get("weight_g", 0)
        expected_weights[cust] = expected_weights.get(cust, 0) + weight

        # Check for system crash
        if status == "System Crash":
            write_event("Unexpected Systems Crash", {
                "station_id": station,
                "duration_seconds": 180
            })

        # If POS scan matches RFID, mark as Success
        if sku in seen_rfids.get(cust, set()):
            write_event("Succes Operation", {
                "station_id": station,
                "customer_id": cust,
                "product_sku": sku
            })
            seen_rfids[cust].discard(sku)

    # 3. Product recognition -> Barcode Switching
    if dataset.lower() == "product_recognition" and status == "Active":
        predicted_sku = ev["data"].get("predicted_product")
        last_scanned = list(scanned_items.get(cust, []))[-1] if scanned_items.get(cust) else None
        if predicted_sku and last_scanned and predicted_sku != last_scanned:
            write_event("Barcode Switching", {
                "station_id": station,
                "customer_id": cust,
                "actual_sku": predicted_sku,
                "scanned_sku": last_scanned
            })

    # 4. Weight discrepancies
    if dataset.lower() == "pos_transactions":
        actual_weight = ev["data"].get("weight_g")
        last_sku = list(scanned_items.get(cust, []))[-1] if scanned_items.get(cust) else None
        expected_weight = ev["data"].get("price")  # optionally could map SKU -> expected weight
        if actual_weight and expected_weight and abs(actual_weight - expected_weight) > 50:
            write_event("Weight Discrepancies", {
                "station_id": station,
                "customer_id": cust,
                "product_sku": last_sku,
                "expected_weight": expected_weight,
                "actual_weight": actual_weight
            })

    # 5. Queue monitoring -> Long Queue or Wait Time
    if dataset.lower() == "queue_monitor" and status == "Active":
        customer_count = ev["data"].get("customer_count", 0)
        dwell = ev["data"].get("average_dwell_time", 0)
        if customer_count >= 6:
            write_event("Long Queue Length", {
                "station_id": station,
                "num_of_customers": customer_count
            })
        if dwell >= 300:
            write_event("Long Wait Time", {
                "station_id": station,
                "customer_id": cust,
                "wait_time_seconds": dwell
            })

    # 6. Inventory discrepancies
    if dataset.lower() == "inventory_snapshots" and status == "Active":
        for sku, qty in ev.get("data", {}).items():
            if sku in inventory_snapshot and qty != inventory_snapshot[sku]:
                write_event("Inventory Discrepancy", {
                    "SKU": sku,
                    "Expected_Inventory": inventory_snapshot[sku],
                    "Actual_Inventory": qty
                })
            inventory_snapshot[sku] = qty

    # 7. Staffing Needs / Checkout Station Action
    if dataset.lower() == "staffing" and status == "Active":
        write_event("Staffing Needs", {
            "station_id": station,
            "Staff_type": ev.get("data", {}).get("Staff_type", "UNKNOWN")
        })
    if dataset.lower() == "checkout_action" and status == "Active":
        write_event("Checkout Station Action", {
            "station_id": station,
            "Action": ev.get("data", {}).get("Action", "Open")
        })

    # 8. Scanner avoidance
    for cust_id, rfids in list(seen_rfids.items()):
        scanned = scanned_items.get(cust_id, set())
        missing = rfids - scanned
        if missing:
            for sku in missing:
                write_event("Scanner Avoidance", {
                    "station_id": station,
                    "customer_id": cust_id,
                    "product_sku": sku
                })
            seen_rfids[cust_id].clear()


# --- Main ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    print("Connecting to event stream...")
    for idx, event in enumerate(read_events(args.host, args.port), start=1):
        detect(event)
        if args.limit and idx >= args.limit:
            break


if __name__ == "__main__":
    main()
