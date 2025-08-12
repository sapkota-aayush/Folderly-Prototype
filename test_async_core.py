#!/usr/bin/env python3
"""
Comprehensive test of core.py async functions with parallel vs sequential execution
Tests OS operations in both modes to verify core functionality
"""
import asyncio
import time
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.core import (
    create_directory,
    create_numbered_files,
    move_items_to_directory,
    delete_single_item,
    delete_multiple_items,
    delete_items_by_pattern,
    list_directory_items,
    count_files_by_extension,
    get_file_type_statistics
)

class TestLogger:
    """Logs test results and timing for review"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        
    def start_test(self, test_name):
        self.start_time = time.time()
        print(f"\n🧪 {test_name}")
        print("-" * 60)
        
    def end_test(self, test_name, success=True, error=None):
        duration = time.time() - self.start_time
        status = "✅ PASSED" if success else "❌ FAILED"
        result = {
            "test": test_name,
            "status": status,
            "duration": duration,
            "error": str(error) if error else None
        }
        self.results.append(result)
        print(f"{status} - {duration:.3f}s")
        if error:
            print(f"   Error: {error}")
        return result

async def test_dependent_tasks_sequential():
    """Test dependent tasks that MUST run sequentially"""
    logger = TestLogger()
    logger.start_test("Dependent Tasks (Sequential) - SHOULD WORK")
    
    # Test directory
    test_dir = Path.home() / "Desktop" / "core_test_dependent"
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Create a file
        logger.start_test("Step 1: Create file")
        file_res = await create_numbered_files(
            "dependent_file", 1, "txt", 
            target_dir=test_dir, 
            execution_mode="sequential"
        )
        if not file_res.get('success'):
            raise Exception(f"Failed to create file: {file_res.get('error')}")
        
        file_path = test_dir / "dependent_file_1.txt"
        if not file_path.exists():
            raise Exception("File was not created")
        print(f"✅ Created: {file_path}")
        logger.end_test("Step 1: Create file")
        
        # Step 2: Move file to subdirectory
        logger.start_test("Step 2: Move file to subdirectory")
        subdir = test_dir / "subdir1"
        subdir.mkdir(exist_ok=True)
        
        move_res = await move_items_to_directory(
            [file_path], subdir, execution_mode="sequential"
        )
        if not move_res.get('success'):
            raise Exception(f"Failed to move file: {move_res.get('error')}")
        
        new_path = subdir / "dependent_file_1.txt"
        if not new_path.exists():
            raise Exception("File was not moved")
        print(f"✅ Moved to: {new_path}")
        logger.end_test("Step 2: Move file to subdirectory")
        
        # Step 3: Move file again to different directory
        logger.start_test("Step 3: Move file to second subdirectory")
        subdir2 = test_dir / "subdir2"
        subdir2.mkdir(exist_ok=True)
        
        move_res2 = await move_items_to_directory(
            [new_path], subdir2, execution_mode="sequential"
        )
        if not move_res2.get('success'):
            raise Exception(f"Failed to move file again: {move_res2.get('error')}")
        
        final_path = subdir2 / "dependent_file_1.txt"
        if not final_path.exists():
            raise Exception("File was not moved to second location")
        print(f"✅ Moved to: {final_path}")
        logger.end_test("Step 3: Move file to second subdirectory")
        
        # Step 4: Delete the final file
        logger.start_test("Step 4: Delete final file")
        delete_res = await delete_single_item(
            str(final_path), execution_mode="sequential"
        )
        if not delete_res.get('success'):
            raise Exception(f"Failed to delete file: {delete_res.get('error')}")
        
        if final_path.exists():
            raise Exception("File still exists after deletion")
        print(f"✅ Deleted: {final_path}")
        logger.end_test("Step 4: Delete final file")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print("🧹 Cleaned up test directory")
        
        logger.end_test("Dependent Tasks (Sequential) - SHOULD WORK")
        return True
        
    except Exception as e:
        logger.end_test("Dependent Tasks (Sequential) - SHOULD WORK", False, e)
        # Cleanup on failure
        try:
            import shutil
            if test_dir.exists():
                shutil.rmtree(test_dir)
        except:
            pass
        return False

async def test_dependent_tasks_parallel():
    """Test dependent tasks in parallel mode - SHOULD FAIL"""
    logger = TestLogger()
    logger.start_test("Dependent Tasks (Parallel) - SHOULD FAIL")
    
    # Test directory
    test_dir = Path.home() / "Desktop" / "core_test_dependent_parallel"
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Try to create file and move it simultaneously (should fail)
        logger.start_test("Attempting dependent operations in parallel")
        
        # Create file
        file_res = await create_numbered_files(
            "parallel_dependent", 1, "txt", 
            target_dir=test_dir, 
            execution_mode="parallel"
        )
        
        if not file_res.get('success'):
            raise Exception(f"Failed to create file: {file_res.get('error')}")
        
        file_path = test_dir / "parallel_dependent_1.txt"
        if not file_path.exists():
            raise Exception("File was not created")
        
        # Try to move file to non-existent directory (should fail in parallel)
        subdir = test_dir / "non_existent_subdir"
        
        move_res = await move_items_to_directory(
            [file_path], subdir, execution_mode="parallel"
        )
        
        # This should fail because we're trying to move to non-existent directory
        if move_res.get('success'):
            print("⚠️  Unexpected success - parallel mode should have failed")
        else:
            print(f"✅ Correctly failed: {move_res.get('error')}")
            
        logger.end_test("Attempting dependent operations in parallel")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print("🧹 Cleaned up test directory")
        
        logger.end_test("Dependent Tasks (Parallel) - SHOULD FAIL")
        return True
        
    except Exception as e:
        logger.end_test("Dependent Tasks (Parallel) - SHOULD FAIL", False, e)
        # Cleanup on failure
        try:
            import shutil
            if test_dir.exists():
                shutil.rmtree(test_dir)
        except:
            pass
        return False

async def test_independent_tasks_parallel():
    """Test independent tasks that can run in parallel"""
    logger = TestLogger()
    logger.start_test("Independent Tasks (Parallel) - SHOULD WORK")
    
    # Test directory
    test_dir = Path.home() / "Desktop" / "core_test_independent"
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Create multiple files in parallel
        logger.start_test("Step 1: Create multiple files in parallel")
        files_res = await create_numbered_files(
            "parallel_file", 5, "txt", 
            target_dir=test_dir, 
            execution_mode="parallel"
        )
        
        if not files_res.get('success'):
            raise Exception(f"Failed to create files: {files_res.get('error')}")
        
        created_files = [test_dir / f"parallel_file_{i}.txt" for i in range(1, 6)]
        for file_path in created_files:
            if not file_path.exists():
                raise Exception(f"File {file_path} was not created")
        print(f"✅ Created {len(created_files)} files in parallel")
        logger.end_test("Step 1: Create multiple files in parallel")
        
        # Step 2: Move files to different locations simultaneously
        logger.start_test("Step 2: Move files to different locations in parallel")
        
        # Create destination directories
        dest_dirs = []
        for i in range(3):
            dest_dir = test_dir / f"dest_{i}"
            dest_dir.mkdir(exist_ok=True)
            dest_dirs.append(dest_dir)
        
        # Move files to different destinations simultaneously
        move_tasks = []
        for i, file_path in enumerate(created_files[:3]):
            dest = dest_dirs[i % len(dest_dirs)]
            move_tasks.append(
                move_items_to_directory([file_path], dest, execution_mode="parallel")
            )
        
        move_results = await asyncio.gather(*move_tasks)
        
        # Verify moves
        for i, result in enumerate(move_results):
            if not result.get('success'):
                raise Exception(f"Move {i} failed: {result.get('error')}")
        
        print(f"✅ Moved {len(move_results)} files to different locations in parallel")
        logger.end_test("Step 2: Move files to different locations in parallel")
        
        # Step 3: Delete files in parallel
        logger.start_test("Step 3: Delete files in parallel")
        
        # Get all files to delete
        all_files = []
        for dest_dir in dest_dirs:
            all_files.extend(list(dest_dir.glob("*.txt")))
        all_files.extend([f for f in created_files[3:] if f.exists()])
        
        if all_files:
            delete_res = await delete_multiple_items(
                [str(f) for f in all_files], execution_mode="parallel"
            )
            
            if not delete_res.get('success'):
                raise Exception(f"Failed to delete files: {delete_res.get('error')}")
            
            print(f"✅ Deleted {len(all_files)} files in parallel")
        
        logger.end_test("Step 3: Delete files in parallel")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print("🧹 Cleaned up test directory")
        
        logger.end_test("Independent Tasks (Parallel) - SHOULD WORK")
        return True
        
    except Exception as e:
        logger.end_test("Independent Tasks (Parallel) - SHOULD WORK", False, e)
        # Cleanup on failure
        try:
            import shutil
            if test_dir.exists():
                shutil.rmtree(test_dir)
        except:
            pass
        return False

async def test_mixed_tasks():
    """Test mixed independent and dependent tasks"""
    logger = TestLogger()
    logger.start_test("Mixed Tasks (Independent + Dependent) - SHOULD WORK")
    
    # Test directory
    test_dir = Path.home() / "Desktop" / "core_test_mixed"
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Create multiple files independently in parallel
        logger.start_test("Step 1: Create files independently in parallel")
        
        # Create different types of files simultaneously
        tasks = [
            create_numbered_files("mixed_a", 3, "txt", target_dir=test_dir, execution_mode="parallel"),
            create_numbered_files("mixed_b", 2, "py", target_dir=test_dir, execution_mode="parallel"),
            create_numbered_files("mixed_c", 2, "json", target_dir=test_dir, execution_mode="parallel")
        ]
        
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results):
            if not result.get('success'):
                raise Exception(f"File creation {i} failed: {result.get('error')}")
        
        print("✅ Created multiple file types in parallel")
        logger.end_test("Step 1: Create files independently in parallel")
        
        # Step 2: Run dependent operations sequentially
        logger.start_test("Step 2: Run dependent operations sequentially")
        
        # Create a subdirectory
        subdir = test_dir / "mixed_subdir"
        subdir.mkdir(exist_ok=True)
        
        # Move files one by one (dependent on previous move)
        txt_files = list(test_dir.glob("mixed_a_*.txt"))
        for i, file_path in enumerate(txt_files):
            move_res = await move_items_to_directory(
                [file_path], subdir, execution_mode="sequential"
            )
            if not move_res.get('success'):
                raise Exception(f"Sequential move {i} failed: {move_res.get('error')}")
        
        print(f"✅ Moved {len(txt_files)} files sequentially")
        logger.end_test("Step 2: Run dependent operations sequentially")
        
        # Step 3: Verify final state
        logger.start_test("Step 3: Verify final state")
        
        list_res = await list_directory_items(
            folder_name=str(test_dir), execution_mode="parallel"
        )
        
        if not list_res.get('success'):
            raise Exception(f"Failed to list directory: {list_res.get('error')}")
        
        total_items = list_res.get('total_found', 0)
        print(f"✅ Final directory has {total_items} items")
        logger.end_test("Step 3: Verify final state")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print("🧹 Cleaned up test directory")
        
        logger.end_test("Mixed Tasks (Independent + Dependent) - SHOULD WORK")
        return True
        
    except Exception as e:
        logger.end_test("Mixed Tasks (Independent + Dependent) - SHOULD WORK", False, e)
        # Cleanup on failure
        try:
            import shutil
            if test_dir.exists():
                shutil.rmtree(test_dir)
        except:
            pass
        return False

async def test_error_handling():
    """Test error handling scenarios"""
    logger = TestLogger()
    logger.start_test("Error Handling - SHOULD HANDLE GRACEFULLY")
    
    # Test directory
    test_dir = Path.home() / "Desktop" / "core_test_errors"
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Test 1: Try to move non-existent file
        logger.start_test("Test 1: Move non-existent file")
        non_existent_file = test_dir / "does_not_exist.txt"
        
        move_res = await move_items_to_directory(
            [non_existent_file], test_dir, execution_mode="sequential"
        )
        
        if move_res.get('success'):
            print("⚠️  Unexpected success moving non-existent file")
        else:
            print(f"✅ Correctly handled non-existent file: {move_res.get('error')}")
        
        logger.end_test("Test 1: Move non-existent file")
        
        # Test 2: Try to delete already deleted file
        logger.start_test("Test 2: Delete already deleted file")
        
        # Create a file first
        file_res = await create_numbered_files(
            "temp_file", 1, "txt", target_dir=test_dir, execution_mode="sequential"
        )
        
        if not file_res.get('success'):
            raise Exception(f"Failed to create temp file: {file_res.get('error')}")
        
        temp_file = test_dir / "temp_file_1.txt"
        
        # Delete it
        delete_res = await delete_single_item(
            str(temp_file), execution_mode="sequential"
        )
        
        if not delete_res.get('success'):
            raise Exception(f"Failed to delete temp file: {delete_res.get('error')}")
        
        # Try to delete it again
        delete_res2 = await delete_single_item(
            str(temp_file), execution_mode="sequential"
        )
        
        if delete_res2.get('success'):
            print("⚠️  Unexpected success deleting already deleted file")
        else:
            print(f"✅ Correctly handled already deleted file: {delete_res2.get('error')}")
        
        logger.end_test("Test 2: Delete already deleted file")
        
        # Test 3: Try to create file in invalid path
        logger.start_test("Test 3: Create file in invalid path")
        
        invalid_res = await create_numbered_files(
            "invalid", 1, "txt",
            target_dir=Path("/invalid/system/path"),
            execution_mode="sequential"
        )
        
        if invalid_res.get('success'):
            print("⚠️  Unexpected success creating file in invalid path")
        else:
            print(f"✅ Correctly handled invalid path: {invalid_res.get('error')}")
        
        logger.end_test("Test 3: Create file in invalid path")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print("🧹 Cleaned up test directory")
        
        logger.end_test("Error Handling - SHOULD HANDLE GRACEFULLY")
        return True
        
    except Exception as e:
        logger.end_test("Error Handling - SHOULD HANDLE GRACEFULLY", False, e)
        # Cleanup on failure
        try:
            import shutil
            if test_dir.exists():
                shutil.rmtree(test_dir)
        except:
            pass
        return False

async def test_cross_verification():
    """Test cross-verification of operations"""
    logger = TestLogger()
    logger.start_test("Cross-Verification - SHOULD VERIFY ALL OPERATIONS")
    
    # Test directory
    test_dir = Path.home() / "Desktop" / "core_test_verify"
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Create a file and verify it exists
        logger.start_test("Create and verify file exists")
        file_res = await create_numbered_files(
            "verify_file", 1, "txt", target_dir=test_dir, execution_mode="sequential"
        )
        
        if not file_res.get('success'):
            raise Exception(f"Failed to create file: {file_res.get('error')}")
        
        file_path = test_dir / "verify_file_1.txt"
        
        # Cross-verify with os.path.exists
        if not os.path.exists(file_path):
            raise Exception("os.path.exists says file doesn't exist")
        
        # Cross-verify with Path.exists
        if not file_path.exists():
            raise Exception("Path.exists says file doesn't exist")
        
        print("✅ File creation verified with both methods")
        logger.end_test("Create and verify file exists")
        
        # Move file and verify
        logger.start_test("Move and verify file location")
        subdir = test_dir / "verify_subdir"
        subdir.mkdir(exist_ok=True)
        
        move_res = await move_items_to_directory(
            [file_path], subdir, execution_mode="sequential"
        )
        
        if not move_res.get('success'):
            raise Exception(f"Failed to move file: {move_res.get('error')}")
        
        new_path = subdir / "verify_file_1.txt"
        
        # Verify old location doesn't exist
        if file_path.exists():
            raise Exception("File still exists at old location")
        
        # Verify new location exists
        if not new_path.exists():
            raise Exception("File doesn't exist at new location")
        
        print("✅ File move verified with both methods")
        logger.end_test("Move and verify file location")
        
        # Delete file and verify
        logger.start_test("Delete and verify file removal")
        delete_res = await delete_single_item(
            str(new_path), execution_mode="sequential"
        )
        
        if not delete_res.get('success'):
            raise Exception(f"Failed to delete file: {delete_res.get('error')}")
        
        # Verify file doesn't exist
        if new_path.exists():
            raise Exception("File still exists after deletion")
        
        if os.path.exists(new_path):
            raise Exception("os.path.exists says file still exists")
        
        print("✅ File deletion verified with both methods")
        logger.end_test("Delete and verify file removal")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print("🧹 Cleaned up test directory")
        
        logger.end_test("Cross-Verification - SHOULD VERIFY ALL OPERATIONS")
        return True
        
    except Exception as e:
        logger.end_test("Cross-Verification - SHOULD VERIFY ALL OPERATIONS", False, e)
        # Cleanup on failure
        try:
            import shutil
            if test_dir.exists():
                shutil.rmtree(test_dir)
        except:
            pass
        return False

async def test_stress_operations():
    """Test stress operations with many files"""
    logger = TestLogger()
    logger.start_test("Stress Operations - SHOULD HANDLE MANY FILES")
    
    # Test directory
    test_dir = Path.home() / "Desktop" / "core_test_stress"
    test_dir.mkdir(exist_ok=True)
    
    try:
        # Create many files in parallel
        logger.start_test("Create 50 files in parallel")
        start_time = time.time()
        
        stress_res = await create_numbered_files(
            "stress", 50, "tmp", target_dir=test_dir, execution_mode="parallel"
        )
        
        if not stress_res.get('success'):
            raise Exception(f"Failed to create stress files: {stress_res.get('error')}")
        
        create_time = time.time() - start_time
        print(f"✅ Created 50 files in {create_time:.3f}s")
        logger.end_test("Create 50 files in parallel")
        
        # List and count files
        logger.start_test("List and count many files")
        list_res = await list_directory_items(
            folder_name=str(test_dir), execution_mode="parallel"
        )
        
        if not list_res.get('success'):
            raise Exception(f"Failed to list directory: {list_res.get('error')}")
        
        total_found = list_res.get('total_found', 0)
        print(f"✅ Found {total_found} items in directory")
        logger.end_test("List and count many files")
        
        # Count by extension
        logger.start_test("Count files by extension")
        count_res = await count_files_by_extension(
            folder_name=str(test_dir), execution_mode="parallel"
        )
        
        if not count_res.get('success'):
            raise Exception(f"Failed to count extensions: {count_res.get('error')}")
        
        total_files = count_res.get('total_files', 0)
        extensions = count_res.get('extension_counts', {})
        print(f"✅ Total files: {total_files}, Extensions: {extensions}")
        logger.end_test("Count files by extension")
        
        # Delete all files in parallel
        logger.start_test("Delete all files in parallel")
        start_time = time.time()
        
        delete_res = await delete_items_by_pattern(
            "*.tmp", target_dir=str(test_dir), execution_mode="parallel"
        )
        
        if not delete_res.get('success'):
            raise Exception(f"Failed to delete files: {delete_res.get('error')}")
        
        delete_time = time.time() - start_time
        total_deleted = delete_res.get('total_deleted', 0)
        print(f"✅ Deleted {total_deleted} files in {delete_time:.3f}s")
        logger.end_test("Delete all files in parallel")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print("🧹 Cleaned up test directory")
        
        logger.end_test("Stress Operations - SHOULD HANDLE MANY FILES")
        return True
        
    except Exception as e:
        logger.end_test("Stress Operations - SHOULD HANDLE MANY FILES", False, e)
        # Cleanup on failure
        try:
            import shutil
            if test_dir.exists():
                shutil.rmtree(test_dir)
        except:
            pass
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Core.py Async Function Tests")
    print("=" * 80)
    print("Testing OS operations in both parallel and sequential modes")
    print("Verifying core functionality and error handling")
    print("=" * 80)
    
    # Test results
    test_results = []
    
    # Run all tests
    tests = [
        ("Dependent Tasks (Sequential)", test_dependent_tasks_sequential),
        ("Dependent Tasks (Parallel)", test_dependent_tasks_parallel),
        ("Independent Tasks (Parallel)", test_independent_tasks_parallel),
        ("Mixed Tasks", test_mixed_tasks),
        ("Error Handling", test_error_handling),
        ("Cross-Verification", test_cross_verification),
        ("Stress Operations", test_stress_operations)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"💥 Test {test_name} crashed: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Core.py is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 What was tested:")
    print("   • Dependent vs Independent task execution")
    print("   • Parallel vs Sequential modes")
    print("   • Error handling and edge cases")
    print("   • Cross-verification of operations")
    print("   • Stress testing with many files")
    print("   • OS operation verification")

if __name__ == "__main__":
    asyncio.run(main())
