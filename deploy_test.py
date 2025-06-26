#!/usr/bin/env python3
"""
Simple test script to verify deployment configuration
"""
import os
import subprocess
import sys

def test_pandoc():
    """Test if pandoc is available"""
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Pandoc is available")
            print(f"   Version: {result.stdout.split('\n')[0]}")
            return True
        else:
            print("❌ Pandoc is not working properly")
            return False
    except FileNotFoundError:
        print("❌ Pandoc is not installed")
        return False

def test_texlive():
    """Test if LaTeX is available for PDF generation"""
    try:
        result = subprocess.run(['xelatex', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ XeLaTeX is available")
            return True
        else:
            print("❌ XeLaTeX is not working properly")
            return False
    except FileNotFoundError:
        print("❌ XeLaTeX is not installed")
        return False

def test_port_config():
    """Test port configuration"""
    port = os.environ.get('PORT', '8080')
    print(f"✅ PORT environment variable: {port}")
    return True

def test_directories():
    """Test if required directories exist"""
    required_dirs = ['uploads', 'output']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory '{dir_name}' exists")
        else:
            print(f"❌ Directory '{dir_name}' does not exist")
            return False
    return True

def main():
    print("🚀 Railway Deployment Test")
    print("=" * 40)
    
    tests = [
        test_pandoc,
        test_texlive,
        test_port_config,
        test_directories
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 