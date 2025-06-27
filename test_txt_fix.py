#!/usr/bin/env python3
"""
Test script to verify the txt format conversion fix
"""

import os
import tempfile
import subprocess
import sys
from app import map_output_format, convert_file_with_pandoc

def test_format_mapping():
    """Test the format mapping function"""
    print("🧪 Testing format mapping...")
    
    test_cases = [
        ('txt', 'plain'),
        ('TXT', 'plain'),
        ('text', 'plain'),
        ('plaintext', 'plain'),
        ('pdf', 'pdf'),
        ('html', 'html'),
        ('docx', 'docx'),
        ('unknown', 'unknown'),
    ]
    
    all_passed = True
    for input_format, expected_output in test_cases:
        result = map_output_format(input_format)
        if result == expected_output:
            print(f"   ✅ '{input_format}' -> '{result}'")
        else:
            print(f"   ❌ '{input_format}' -> '{result}' (expected '{expected_output}')")
            all_passed = False
    
    return all_passed

def test_txt_conversion():
    """Test actual txt conversion"""
    print("\n🔧 Testing txt conversion...")
    
    # Create a temporary markdown file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Test Document

This is a test document with some **bold** and *italic* text.

## Section 1

- Item 1
- Item 2
- Item 3

## Section 2

Some more content here.
""")
        input_file = f.name
    
    try:
        # Create output directory
        output_dir = tempfile.mkdtemp()
        output_file = os.path.join(output_dir, 'test_output.txt')
        media_dir = os.path.join(output_dir, 'media')
        os.makedirs(media_dir, exist_ok=True)
        
        # Test conversion to txt (which should be mapped to plain)
        success, error = convert_file_with_pandoc(
            input_file, output_file, 'markdown', 'txt', media_dir
        )
        
        if success:
            print("✅ TXT conversion successful")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   Output file size: {file_size} bytes")
                
                # Read and show first few lines
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read(200)
                    print(f"   First 200 chars: {repr(content)}")
            else:
                print("   ❌ Output file not created")
        else:
            print(f"❌ TXT conversion failed: {error}")
        
        # Clean up
        os.unlink(input_file)
        import shutil
        shutil.rmtree(output_dir)
        
        return success
        
    except Exception as e:
        print(f"❌ Error during txt conversion test: {e}")
        return False

def main():
    """Run the tests"""
    print("🧪 Testing TXT Format Fix")
    print("=" * 40)
    
    tests = [
        ("Format Mapping", test_format_mapping),
        ("TXT Conversion", test_txt_conversion),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📝 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The TXT format fix is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 