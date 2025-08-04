#!/usr/bin/env python3
"""
Test script to debug watchdog activity tracking
"""

import time
import os
from pathlib import Path
from folderly.activity_tracker import start_activity_monitoring, FolderlyActivityTracker

def test_activity_tracking():
    """Test if activity tracking is working"""
    print("🔍 Testing activity tracking...")
    
    # Test 1: Create tracker
    try:
        tracker = FolderlyActivityTracker()
        print(f"✅ Tracker created successfully")
        print(f"📁 Monitoring path: {tracker.desktop_path}")
        print(f"📄 Log file: {tracker.log_file}")
        print(f"📊 Current activities: {len(tracker.activities)}")
    except Exception as e:
        print(f"❌ Failed to create tracker: {e}")
        return
    
    # Test 2: Start monitoring
    try:
        tracker, observer = start_activity_monitoring()
        print(f"✅ Monitoring started")
        print(f"🔍 Observer alive: {observer.is_alive()}")
        
        # Keep it running for a bit
        print("⏳ Monitoring for 10 seconds... (try creating/deleting files on Desktop)")
        time.sleep(10)
        
        # Check if any activities were recorded
        print(f"📊 Activities recorded: {len(tracker.activities)}")
        if tracker.activities:
            print("📝 Recent activities:")
            for activity in tracker.activities[-5:]:
                print(f"  - {activity['action']}: {activity['details']['filename']}")
        
        observer.stop()
        observer.join()
        print("✅ Monitoring stopped")
        
    except Exception as e:
        print(f"❌ Failed to start monitoring: {e}")

if __name__ == "__main__":
    test_activity_tracking() 