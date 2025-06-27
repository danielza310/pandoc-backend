#!/usr/bin/env python3
"""
Test script for the format API endpoints
"""

import requests
import json
import os
from io import BytesIO

def test_all_formats_endpoint():
    """Test the /all-formats endpoint"""
    print("Testing /all-formats endpoint...")
    
    try:
        response = requests.get('http://localhost:5000/all-formats')
        
        if response.status_code == 200:
            data = response.json()
            print("✓ /all-formats endpoint working")
            print(f"  Input formats: {len(data['input_formats'])}")
            print(f"  Output formats: {len(data['output_formats'])}")
            print(f"  Organized categories: {len(data['organized_output_formats'])}")
            
            # Show some examples
            print("\n  Sample input formats:")
            for fmt in data['input_formats'][:10]:
                print(f"    - {fmt}")
            
            print("\n  Sample output format categories:")
            for category, formats in data['organized_output_formats'].items():
                if formats:
                    print(f"    {category}: {len(formats)} formats")
            
            return True
        else:
            print(f"✗ /all-formats endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing /all-formats: {e}")
        return False

def test_supported_formats_endpoint():
    """Test the /supported-formats endpoint with sample files"""
    print("\nTesting /supported-formats endpoint...")
    
    try:
        # Create a mock file for testing
        files = {
            'files': (BytesIO(b"test content"), 'test.docx')
        }
        
        response = requests.post('http://localhost:5000/supported-formats', files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ /supported-formats endpoint working")
            print(f"  Input formats detected: {data['input_formats']}")
            print(f"  Supported output formats: {len(data['supported_output_formats'])}")
            print(f"  Message: {data['message']}")
            
            # Show some supported formats
            print("\n  Sample supported output formats:")
            for fmt in data['supported_output_formats'][:15]:
                print(f"    - {fmt}")
            
            return True
        else:
            print(f"✗ /supported-formats endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing /supported-formats: {e}")
        return False

def test_multiple_file_formats():
    """Test with multiple file types"""
    print("\nTesting with multiple file types...")
    
    try:
        # Create multiple mock files
        files = [
            ('files', (BytesIO(b"test content"), 'document.docx')),
            ('files', (BytesIO(b"test content"), 'presentation.pptx')),
            ('files', (BytesIO(b"test content"), 'webpage.html'))
        ]
        
        response = requests.post('http://localhost:5000/supported-formats', files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Multiple file types test working")
            print(f"  Input formats detected: {data['input_formats']}")
            print(f"  Supported output formats: {len(data['supported_output_formats'])}")
            
            # Show intersection of supported formats
            print("\n  Common supported output formats:")
            for fmt in data['supported_output_formats'][:10]:
                print(f"    - {fmt}")
            
            return True
        else:
            print(f"✗ Multiple file types test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing multiple file types: {e}")
        return False

def test_format_compatibility():
    """Test format compatibility for different input types"""
    print("\nTesting format compatibility...")
    
    test_cases = [
        ('document.docx', 'Word Document'),
        ('presentation.pptx', 'PowerPoint Presentation'),
        ('webpage.html', 'HTML Web Page'),
        ('document.pdf', 'PDF Document'),
        ('readme.md', 'Markdown File'),
        ('document.epub', 'E-book File')
    ]
    
    for filename, description in test_cases:
        try:
            files = {
                'files': (BytesIO(b"test content"), filename)
            }
            
            response = requests.post('http://localhost:5000/supported-formats', files=files)
            
            if response.status_code == 200:
                data = response.json()
                input_format = data['input_formats'][0] if data['input_formats'] else 'unknown'
                output_count = len(data['supported_output_formats'])
                print(f"  ✓ {description} ({input_format}): {output_count} output formats")
            else:
                print(f"  ✗ {description}: Failed")
                
        except Exception as e:
            print(f"  ✗ {description}: Error - {e}")

def main():
    """Run all tests"""
    print("=== Format API Testing ===\n")
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code != 200:
            print("✗ Backend server is not running on localhost:5000")
            print("  Please start the backend server first:")
            print("  cd backend && python app.py")
            return
    except:
        print("✗ Cannot connect to backend server on localhost:5000")
        print("  Please start the backend server first:")
        print("  cd backend && python app.py")
        return
    
    print("✓ Backend server is running\n")
    
    # Run tests
    test_all_formats_endpoint()
    test_supported_formats_endpoint()
    test_multiple_file_formats()
    test_format_compatibility()
    
    print("\n=== Testing Complete ===")

if __name__ == "__main__":
    main() 