#!/usr/bin/env python3
"""
View and analyze browser task costs from /tmp/browser-cost.log
"""

import json
import sys
from collections import defaultdict
from datetime import datetime

COST_LOG_FILE = "/tmp/browser-cost.log"


def format_timestamp(iso_timestamp):
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_timestamp


def analyze_costs(session_id=None, verbose=False):
    """Analyze costs from the log file."""
    try:
        with open(COST_LOG_FILE, "r") as f:
            entries = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"❌ Cost log file not found: {COST_LOG_FILE}")
        print("   Run a browser task first to generate cost data.")
        return

    if not entries:
        print(f"📝 No cost data found in {COST_LOG_FILE}")
        return

    # Filter by session if specified
    if session_id:
        entries = [e for e in entries if e.get("session_id") == session_id]
        if not entries:
            print(f"❌ No entries found for session: {session_id}")
            return

    # Group by session
    sessions = defaultdict(list)
    for entry in entries:
        sessions[entry.get("session_id")].append(entry)

    # Print summary
    print(f"\n📊 Browser Cost Analysis")
    print(f"{'=' * 80}\n")

    total_cost = 0
    total_tokens = 0
    total_calls = 0

    for sid, session_entries in sessions.items():
        session_cost = sum(e.get("cost", {}).get("total_cost_usd", 0) for e in session_entries)
        session_tokens = sum(e.get("usage", {}).get("total_tokens", 0) for e in session_entries)
        session_calls = len(session_entries)

        total_cost += session_cost
        total_tokens += session_tokens
        total_calls += session_calls

        # Get session metadata
        first_entry = session_entries[0]
        model = first_entry.get("model", "unknown")
        timestamp = format_timestamp(first_entry.get("timestamp", ""))

        print(f"Session: {sid}")
        print(f"  Time: {timestamp}")
        print(f"  Model: {model}")
        print(f"  API Calls: {session_calls}")
        print(f"  Total Tokens: {session_tokens:,}")
        print(f"  Total Cost: ${session_cost:.6f}")
        print(f"  Avg Cost/Call: ${session_cost/session_calls:.6f}")
        print()

        if verbose:
            print(f"  Individual Calls:")
            for i, entry in enumerate(session_entries, 1):
                usage = entry.get("usage", {})
                cost = entry.get("cost", {})
                latency = entry.get("latency_seconds", 0)
                print(f"    {i}. Tokens: {usage.get('total_tokens', 0):,} | "
                      f"Cost: ${cost.get('total_cost_usd', 0):.6f} | "
                      f"Latency: {latency:.2f}s")
            print()

    # Print grand total
    print(f"{'=' * 80}")
    print(f"📈 Grand Total")
    print(f"  Sessions: {len(sessions)}")
    print(f"  Total API Calls: {total_calls}")
    print(f"  Total Tokens: {total_tokens:,}")
    print(f"  Total Cost: ${total_cost:.6f}")
    print(f"  Avg Cost/Session: ${total_cost/len(sessions):.6f}")
    print(f"  Avg Cost/Call: ${total_cost/total_calls:.6f}")
    print()


def list_sessions():
    """List all sessions in the log."""
    try:
        with open(COST_LOG_FILE, "r") as f:
            entries = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"❌ Cost log file not found: {COST_LOG_FILE}")
        return

    sessions = {}
    for entry in entries:
        sid = entry.get("session_id")
        if sid not in sessions:
            sessions[sid] = {
                "model": entry.get("model"),
                "timestamp": entry.get("timestamp"),
                "calls": 0,
            }
        sessions[sid]["calls"] += 1

    print(f"\n📋 Available Sessions in {COST_LOG_FILE}")
    print(f"{'=' * 80}\n")

    for sid, info in sessions.items():
        timestamp = format_timestamp(info["timestamp"])
        print(f"{sid}")
        print(f"  Time: {timestamp}")
        print(f"  Model: {info['model']}")
        print(f"  Calls: {info['calls']}")
        print()


def clear_log():
    """Clear the cost log file."""
    try:
        with open(COST_LOG_FILE, "w") as f:
            pass
        print(f"✅ Cleared cost log: {COST_LOG_FILE}")
    except Exception as e:
        print(f"❌ Error clearing log: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="View and analyze browser task costs"
    )
    parser.add_argument(
        "--session",
        type=str,
        help="Filter by session ID",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed per-call breakdown",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all available sessions",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the cost log file",
    )

    args = parser.parse_args()

    if args.clear:
        clear_log()
    elif args.list:
        list_sessions()
    else:
        analyze_costs(session_id=args.session, verbose=args.verbose)
