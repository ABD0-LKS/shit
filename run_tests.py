"""
Test runner for LKS POS System
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests"""
    print("🧪 Running LKS POS System Tests")
    print("=" * 50)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    # Run tests
    test_commands = [
        # Run all tests
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        
        # Run with coverage
        [sys.executable, "-m", "pytest", "tests/", "--cov=src/", "--cov-report=term-missing"],
        
        # Generate HTML coverage report
        [sys.executable, "-m", "pytest", "tests/", "--cov=src/", "--cov-report=html"]
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n🔄 Running test command {i}/{len(test_commands)}")
        print(" ".join(cmd))
        print("-" * 30)
        
        try:
            result = subprocess.run(cmd, capture_output=False, text=True)
            if result.returncode == 0:
                print(f"✅ Test command {i} passed!")
            else:
                print(f"❌ Test command {i} failed!")
        except Exception as e:
            print(f"❌ Error running test command {i}: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test run complete!")
    print("📊 Check htmlcov/index.html for detailed coverage report")

if __name__ == "__main__":
    run_tests()
