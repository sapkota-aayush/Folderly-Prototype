#!/usr/bin/env python3
"""
Test Smart Execution Strategy
Tests the automatic execution mode selection in core functions
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

from core.core import (
    create_directory, 
    create_multiple_directories,
    delete_single_item,
    delete_multiple_items,
    list_directory_items,
    get_smart_execution_mode,
    copy_multiple_items,
    rename_multiple_items
)

async def test_smart_execution():
    """Test the smart execution mode selection"""
    print("🧪 Testing Smart Execution Strategy")
    print("=" * 50)
    
    # Test 1: Single operations should default to sequential
    print("\n📁 Test 1: Single Operations (Should be Sequential)")
    print("-" * 40)
    
    result1 = await create_directory(Path("TestSingle"), "Desktop")
    print(f"✅ create_directory execution_mode: {result1.get('execution_mode', 'NOT_SET')}")
    
    result2 = await list_directory_items("Desktop")
    print(f"✅ list_directory_items execution_mode: {result2.get('execution_mode', 'NOT_SET')}")
    
    # Test 2: Multiple operations should default to parallel
    print("\n📁 Test 2: Multiple Operations (Should be Parallel)")
    print("-" * 40)
    
    result3 = await create_multiple_directories(["TestMulti1", "TestMulti2", "TestMulti3"], "Desktop")
    print(f"✅ create_multiple_directories execution_mode: {result3.get('execution_mode', 'NOT_SET')}")
    
    # Test 3: Smart execution mode function
    print("\n🧠 Test 3: Smart Execution Mode Function")
    print("-" * 40)
    
    mode1 = get_smart_execution_mode("create_directory", is_multiple=False)
    mode2 = get_smart_execution_mode("create_multiple_directories", is_multiple=True)
    mode3 = get_smart_execution_mode("list_directory_items", is_multiple=False)
    
    print(f"✅ create_directory → {mode1}")
    print(f"✅ create_multiple_directories → {mode2}")
    print(f"✅ list_directory_items → {mode3}")
    
    # Test 4: Cleanup
    print("\n🧹 Test 4: Cleanup")
    print("-" * 40)
    
    cleanup_items = ["TestSingle", "TestMulti1", "TestMulti2", "TestMulti3"]
    result4 = await delete_multiple_items(cleanup_items)
    print(f"✅ Cleanup execution_mode: {result4.get('execution_mode', 'NOT_SET')}")
    print(f"✅ Deleted {result4.get('total_deleted', 0)} items")
    
    print("\n🎯 Smart Execution Strategy Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_smart_execution())
