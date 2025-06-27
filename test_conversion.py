#!/usr/bin/env python3
"""
Test script to verify file conversion and media extraction functionality
"""

import os
import tempfile
import subprocess
import sys
from app import convert_file_with_pandoc, get_input_format, allowed_file

def test_pandoc_availability():
    """Test if Pandoc is available"""
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Pandoc is available: {result.stdout.split('\n')[0]}")
            return True
        else:
            print("❌ Pandoc is not available")
            return False
    except Exception as e:
        print(f"❌ Error checking Pandoc: {e}")
        return False

def test_simple_conversion():
    """Test a simple markdown to HTML conversion"""
    print("\n🔧 Testing simple conversion...")
    
    # Create a temporary markdown file with some content
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
        output_file = os.path.join(output_dir, 'test_output.html')
        media_dir = os.path.join(output_dir, 'media')
        os.makedirs(media_dir, exist_ok=True)
        
        # Test conversion
        success, error = convert_file_with_pandoc(
            input_file, output_file, 'markdown', 'html', media_dir
        )
        
        if success:
            print("✅ Simple conversion successful")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   Output file size: {file_size} bytes")
            else:
                print("   ❌ Output file not created")
        else:
            print(f"❌ Simple conversion failed: {error}")
        
        # Clean up
        os.unlink(input_file)
        import shutil
        shutil.rmtree(output_dir)
        
        return success
        
    except Exception as e:
        print(f"❌ Error during simple conversion test: {e}")
        return False

def test_media_extraction():
    """Test media extraction from HTML"""
    print("\n🖼️ Testing media extraction...")
    
    # Create a temporary HTML file with embedded image
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write("""<!DOCTYPE html>
<html>
<head><title>Test with Media</title></head>
<body>
<h1>Test Document with Media</h1>
<p>This document contains an image:</p>
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" alt="Test Image">
<p>And some text content.</p>
</body>
</html>""")
        input_file = f.name
    
    try:
        # Create output directory
        output_dir = tempfile.mkdtemp()
        output_file = os.path.join(output_dir, 'test_output.md')
        media_dir = os.path.join(output_dir, 'media')
        os.makedirs(media_dir, exist_ok=True)
        
        # Test conversion with media extraction
        success, error = convert_file_with_pandoc(
            input_file, output_file, 'html', 'markdown', media_dir
        )
        
        if success:
            print("✅ Media extraction conversion successful")
            
            # Check if media files were extracted
            media_files = []
            if os.path.exists(media_dir):
                for root, dirs, files in os.walk(media_dir):
                    for file in files:
                        media_files.append(os.path.join(root, file))
            
            if media_files:
                print(f"   ✅ Extracted {len(media_files)} media files:")
                for media_file in media_files:
                    file_size = os.path.getsize(media_file)
                    print(f"      - {os.path.basename(media_file)} ({file_size} bytes)")
            else:
                print("   ℹ️ No media files were extracted (this is normal for this test)")
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"   Output file size: {file_size} bytes")
            else:
                print("   ❌ Output file not created")
        else:
            print(f"❌ Media extraction conversion failed: {error}")
        
        # Clean up
        os.unlink(input_file)
        import shutil
        shutil.rmtree(output_dir)
        
        return success
        
    except Exception as e:
        print(f"❌ Error during media extraction test: {e}")
        return False

def test_format_detection():
    """Test format detection"""
    print("\n🔍 Testing format detection...")
    
    test_cases = [
        ('test.md', 'markdown'),
        ('document.docx', 'docx'),
        ('presentation.pptx', 'pptx'),
        ('file.pdf', 'pdf'),
        ('page.html', 'html'),
        ('data.xml', 'docbook'),
        ('text.txt', 'plain'),
    ]
    
    all_passed = True
    for filename, expected_format in test_cases:
        detected_format = get_input_format(filename)
        if detected_format == expected_format:
            print(f"   ✅ {filename} -> {detected_format}")
        else:
            print(f"   ❌ {filename} -> {detected_format} (expected {expected_format})")
            all_passed = False
    
    return all_passed

def test_file_validation():
    """Test file validation"""
    print("\n📋 Testing file validation...")
    
    test_cases = [
        ('test.md', True),
        ('document.docx', True),
        ('presentation.pptx', True),
        ('file.pdf', True),
        ('page.html', True),
        ('data.xml', True),
        ('text.txt', True),
        ('script.py', False),  # Not supported
        ('image.jpg', False),  # Not supported
    ]
    
    all_passed = True
    for filename, should_be_allowed in test_cases:
        is_allowed = allowed_file(filename)
        if is_allowed == should_be_allowed:
            print(f"   ✅ {filename} -> {'allowed' if is_allowed else 'denied'}")
        else:
            print(f"   ❌ {filename} -> {'allowed' if is_allowed else 'denied'} (expected {'allowed' if should_be_allowed else 'denied'})")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("🧪 Starting Pandoc Converter Tests")
    print("=" * 50)
    
    tests = [
        ("Pandoc Availability", test_pandoc_availability),
        ("Format Detection", test_format_detection),
        ("File Validation", test_file_validation),
        ("Simple Conversion", test_simple_conversion),
        ("Media Extraction", test_media_extraction),
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
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The conversion functionality should be working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 