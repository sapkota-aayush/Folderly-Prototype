#!/usr/bin/env python3
"""
Test script for delete undo functionality
"""

import os
import tempfile
from pathlib import Path
from src.core.core import delete_single_item, delete_multiple_items, delete_items_by_pattern
from undo_manager import undo_last_operation

def test_delete_undo():
    """Test the delete undo functionality"""
    
    # Create a temporary directory for testing
    test_dir = Path(tempfile.mkdtemp())
    print(f"🧪 Testing delete undo functionality in: {test_dir}")
    
    try:
        # Create test files
        test_file1 = test_dir / "test_file1.txt"
        test_file2 = test_dir / "test_file2.txt"
        test_file3 = test_dir / "test_file3.txt"
        
        # Create the test files
        test_file1.write_text("This is test file 1")
        test_file2.write_text("This is test file 2")
        test_file3.write_text("This is test file 3")
        
        print(f"✅ Created test files: {test_file1.name}, {test_file2.name}, {test_file3.name}")
        
        # Test 1: Single file delete with undo
        print("\n🔍 Test 1: Single file delete with undo")
        result = delete_single_item(str(test_file1))
        print(f"Delete result: {result}")
        
        if result["success"]:
            print("✅ File deleted successfully")
            
            # Check if file is gone
            if not test_file1.exists():
                print("✅ File is no longer in original location")
                
                # Test undo
                undo_result = undo_last_operation()
                print(f"Undo result: {undo_result}")
                
                if undo_result["success"]:
                    print("✅ Undo successful")
                    if test_file1.exists():
                        print("✅ File restored to original location")
                        print(f"File content: {test_file1.read_text()}")
                    else:
                        print("❌ File not restored")
                else:
                    print(f"❌ Undo failed: {undo_result['message']}")
            else:
                print("❌ File still exists in original location")
        else:
            print(f"❌ Delete failed: {result['error']}")
        
        # Test 2: Multiple files delete with undo
        print("\n🔍 Test 2: Multiple files delete with undo")
        result = delete_multiple_items([str(test_file2), str(test_file3)])
        print(f"Delete result: {result}")
        
        if result["success"]:
            print("✅ Files deleted successfully")
            
            # Check if files are gone
            if not test_file2.exists() and not test_file3.exists():
                print("✅ Files are no longer in original location")
                
                # Test undo
                undo_result = undo_last_operation()
                print(f"Undo result: {undo_result}")
                
                if undo_result["success"]:
                    print("✅ Undo successful")
                    if test_file2.exists() and test_file3.exists():
                        print("✅ Files restored to original location")
                        print(f"File 2 content: {test_file2.read_text()}")
                        print(f"File 3 content: {test_file3.read_text()}")
                    else:
                        print("❌ Files not restored")
                else:
                    print(f"❌ Undo failed: {undo_result['message']}")
            else:
                print("❌ Files still exist in original location")
        else:
            print(f"❌ Delete failed: {result['error']}")
        
        # Test 3: Pattern delete with undo
        print("\n🔍 Test 3: Pattern delete with undo")
        
        # Create more test files
        test_file4 = test_dir / "temp_file1.txt"
        test_file5 = test_dir / "temp_file2.txt"
        test_file6 = test_dir / "permanent_file.txt"
        
        test_file4.write_text("This is temp file 1")
        test_file5.write_text("This is temp file 2")
        test_file6.write_text("This is permanent file")
        
        print(f"✅ Created additional test files: {test_file4.name}, {test_file5.name}, {test_file6.name}")
        
        # Delete files matching pattern
        result = delete_items_by_pattern("temp*", str(test_dir))
        print(f"Delete result: {result}")
        
        if result["success"]:
            print("✅ Pattern delete successful")
            
            # Check if temp files are gone but permanent file remains
            if not test_file4.exists() and not test_file5.exists() and test_file6.exists():
                print("✅ Temp files deleted, permanent file remains")
                
                # Test undo
                undo_result = undo_last_operation()
                print(f"Undo result: {undo_result}")
                
                if undo_result["success"]:
                    print("✅ Undo successful")
                    if test_file4.exists() and test_file5.exists() and test_file6.exists():
                        print("✅ All files restored correctly")
                        print(f"Temp file 1 content: {test_file4.read_text()}")
                        print(f"Temp file 2 content: {test_file5.read_text()}")
                        print(f"Permanent file content: {test_file6.read_text()}")
                    else:
                        print("❌ Files not restored correctly")
                else:
                    print(f"❌ Undo failed: {undo_result['message']}")
            else:
                print("❌ Pattern delete didn't work as expected")
        else:
            print(f"❌ Pattern delete failed: {result['error']}")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    finally:
        # Clean up test directory
        import shutil
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory: {test_dir}")

if __name__ == "__main__":
    test_delete_undo() 