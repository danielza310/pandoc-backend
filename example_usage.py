#!/usr/bin/env python3
"""
Example usage of the improved image handling functionality
"""

import os
import tempfile
import shutil
from app import convert_file_with_pandoc, organize_media_files, fix_image_paths_in_file

def create_sample_docx_with_images():
    """Create a sample DOCX file with embedded images for testing"""
    # This is a simplified example - in practice, you'd use python-docx
    # to create a real DOCX file with embedded images
    print("Note: This is a demonstration. In practice, you'd need a real DOCX file with images.")
    return None

def demonstrate_image_handling():
    """Demonstrate the image handling functionality"""
    print("=== Document Converter Image Handling Demo ===\n")
    
    # Create a temporary directory for the demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Working directory: {temp_dir}")
        
        # Create sample HTML content with image references
        sample_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sample Document with Images</title>
        </head>
        <body>
            <h1>Sample Document</h1>
            <p>This document contains several images:</p>
            
            <h2>Image 1</h2>
            <img src="media/sample1.jpg" alt="Sample Image 1" width="300">
            
            <h2>Image 2</h2>
            <img src="media/subfolder/sample2.png" alt="Sample Image 2" width="300">
            
            <h2>Image 3</h2>
            <img src="media/sample3.gif" alt="Sample Image 3" width="300">
            
            <p>End of document.</p>
        </body>
        </html>
        '''
        
        # Create sample markdown content
        sample_markdown = '''
        # Sample Markdown Document

        This document contains several images:

        ## Image 1
        ![Sample Image 1](media/sample1.jpg)

        ## Image 2
        ![Sample Image 2](media/subfolder/sample2.png)

        ## Image 3
        ![Sample Image 3](media/sample3.gif)

        End of document.
        '''
        
        # Write sample files
        html_file = os.path.join(temp_dir, 'sample.html')
        md_file = os.path.join(temp_dir, 'sample.md')
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(sample_html)
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(sample_markdown)
        
        print("✓ Created sample HTML and Markdown files with image references")
        
        # Create mock media directory with sample images
        media_dir = os.path.join(temp_dir, 'media')
        os.makedirs(media_dir, exist_ok=True)
        os.makedirs(os.path.join(media_dir, 'subfolder'), exist_ok=True)
        
        # Create mock image files
        mock_images = [
            'sample1.jpg',
            'subfolder/sample2.png',
            'sample3.gif'
        ]
        
        for img_path in mock_images:
            full_path = os.path.join(media_dir, img_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(f"Mock image content for {img_path}")
        
        print("✓ Created mock media files")
        
        # Demonstrate media organization
        print("\n--- Step 1: Organizing Media Files ---")
        img_dir = os.path.join(temp_dir, 'img')
        moved_files = organize_media_files(media_dir, img_dir)
        
        print(f"✓ Organized {len(moved_files)} media files into img/ folder")
        if os.path.exists(img_dir):
            img_files = os.listdir(img_dir)
            print(f"  Files in img/: {img_files}")
        
        # Demonstrate path fixing for HTML
        print("\n--- Step 2: Fixing Image Paths in HTML ---")
        print("Before fixing:")
        with open(html_file, 'r', encoding='utf-8') as f:
            print(f.read())
        
        fix_image_paths_in_file(html_file, img_dir, 'html')
        
        print("\nAfter fixing:")
        with open(html_file, 'r', encoding='utf-8') as f:
            print(f.read())
        
        # Demonstrate path fixing for Markdown
        print("\n--- Step 3: Fixing Image Paths in Markdown ---")
        print("Before fixing:")
        with open(md_file, 'r', encoding='utf-8') as f:
            print(f.read())
        
        fix_image_paths_in_file(md_file, img_dir, 'markdown')
        
        print("\nAfter fixing:")
        with open(md_file, 'r', encoding='utf-8') as f:
            print(f.read())
        
        print("\n=== Demo Complete ===")
        print("The system successfully:")
        print("1. Organized media files into img/ folder")
        print("2. Fixed image paths in HTML files")
        print("3. Fixed image paths in Markdown files")
        print("4. Maintained proper relative paths")

def show_supported_formats():
    """Show supported formats for image handling"""
    print("\n=== Supported Formats for Image Handling ===\n")
    
    input_formats = {
        'DOCX': 'Extracts embedded images from Word documents',
        'PPTX': 'Extracts images from PowerPoint presentations',
        'PDF': 'Limited support - converts to Markdown first',
        'HTML': 'Extracts linked images from web pages',
        'EPUB': 'Extracts embedded images from e-books',
        'ODT': 'Extracts embedded images from OpenDocument files',
        'Markdown': 'Extracts linked images from markdown files'
    }
    
    output_formats = {
        'HTML/HTML5/XHTML': 'Fixes src attributes in img tags',
        'Markdown/GitHub Flavored': 'Fixes ![alt](path) syntax',
        'reStructuredText': 'Fixes .. image:: directives',
        'AsciiDoc': 'Fixes image:: syntax',
        'Textile': 'Fixes image syntax',
        'MediaWiki': 'Fixes image syntax',
        'DocBook': 'Fixes image references',
        'JATS': 'Fixes image references'
    }
    
    print("Input Formats with Image Support:")
    for fmt, desc in input_formats.items():
        print(f"  ✓ {fmt}: {desc}")
    
    print("\nOutput Formats with Path Fixing:")
    for fmt, desc in output_formats.items():
        print(f"  ✓ {fmt}: {desc}")

if __name__ == "__main__":
    print("Document Converter - Image Handling Example\n")
    
    try:
        demonstrate_image_handling()
        show_supported_formats()
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc() 