# Image Handling in Document Converter Backend

## Overview

The backend has been enhanced to properly handle embedded images in documents during format conversion. This ensures that:

1. **Images are extracted** from source documents (DOCX, PPTX, PDF, HTML, etc.)
2. **Images are organized** into an `img/` folder for clean structure
3. **Image paths are corrected** in converted files to use relative paths
4. **All formats are supported** with appropriate image handling

## How It Works

### 1. Image Extraction

The system uses Pandoc's `--extract-media` option to extract embedded images from source documents. This works for:

- **Office documents**: DOCX, PPTX, ODT
- **Web formats**: HTML, EPUB
- **Other formats**: Any format that Pandoc can process with embedded media

### 2. Image Organization

Extracted images are automatically organized into an `img/` folder:

```
converted_files_session_id/
├── converted/
│   ├── document1.html
│   └── document2.md
├── img/
│   ├── image1.jpg
│   ├── image2.png
│   └── image3.gif
└── converted_files_session_id.zip
```

### 3. Path Correction

The system automatically fixes image references in converted files:

#### HTML Files
```html
<!-- Before -->
<img src="media/image1.jpg" alt="Test">

<!-- After -->
<img src="img/image1.jpg" alt="Test">
```

#### Markdown Files
```markdown
<!-- Before -->
![Test](media/image1.jpg)

<!-- After -->
![Test](img/image1.jpg)
```

#### Other Formats
- **reStructuredText**: `.. image:: img/image1.jpg`
- **AsciiDoc**: `image::img/image1.jpg[alt text]`

## Supported Input Formats with Images

| Format | Image Support | Notes |
|--------|---------------|-------|
| DOCX | ✅ Full | Extracts embedded images |
| PPTX | ✅ Full | Extracts slides and images |
| PDF | ✅ Limited | Converts to Markdown first |
| HTML | ✅ Full | Extracts linked images |
| EPUB | ✅ Full | Extracts embedded images |
| ODT | ✅ Full | Extracts embedded images |
| Markdown | ✅ Full | Extracts linked images |

## Supported Output Formats with Image Path Fixing

| Format | Path Fixing | Notes |
|--------|-------------|-------|
| HTML/HTML5/XHTML | ✅ | Fixes `src` attributes |
| Markdown/GitHub Flavored | ✅ | Fixes `![alt](path)` syntax |
| reStructuredText | ✅ | Fixes `.. image::` directives |
| AsciiDoc | ✅ | Fixes `image::` syntax |
| Textile | ✅ | Fixes image syntax |
| MediaWiki | ✅ | Fixes image syntax |
| DocBook | ✅ | Fixes image references |
| JATS | ✅ | Fixes image references |

## Technical Implementation

### Key Functions

1. **`convert_file_with_pandoc()`**: Enhanced to always extract media when possible
2. **`organize_media_files()`**: Moves extracted media to `img/` folder
3. **`fix_image_paths_in_file()`**: Corrects image paths in converted files

### Media Extraction Logic

```python
# Always extract media for formats that support it
media_supporting_formats = [
    'html', 'html5', 'xhtml', 'epub', 'epub2', 'epub3', 
    'docx', 'pptx', 'odt', 'markdown', 'gfm', 'commonmark', 
    'commonmark_x', 'rst', 'asciidoc', 'textile', 'mediawiki', 
    'dokuwiki', 'org', 'opml', 'fb2', 'mobi', 'docbook', 
    'docbook4', 'docbook5', 'jats', 'tei', 'icml'
]

# Also extract if input format might contain images
if output_format in media_supporting_formats or input_format in ['docx', 'pptx', 'odt', 'epub', 'html']:
    cmd.extend(['--extract-media', extract_media_dir])
```

### Path Fixing Patterns

The system uses regex patterns to fix image paths for different formats:

```python
# HTML
content = re.sub(r'src="([^"]*)"', 
                lambda m: f'src="img/{os.path.basename(m.group(1))}"' if m.group(1) else m.group(0), 
                content)

# Markdown
content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', 
                lambda m: f'![{m.group(1)}](img/{os.path.basename(m.group(2))})', 
                content)
```

## Usage Example

When a user uploads a DOCX file with embedded images and converts it to HTML:

1. **Upload**: User uploads `document.docx` with embedded images
2. **Conversion**: System converts DOCX → HTML using Pandoc
3. **Extraction**: Images are extracted to `media/` folder
4. **Organization**: Images are moved to `img/` folder
5. **Path Fixing**: HTML file is updated to reference `img/image1.jpg`
6. **ZIP Creation**: Final ZIP contains:
   - `document.html` (with corrected image paths)
   - `img/image1.jpg`
   - `img/image2.png`

## Error Handling

The system gracefully handles:

- **Missing images**: Continues conversion without failing
- **Duplicate filenames**: Automatically renames with counter suffix
- **Unsupported formats**: Falls back to basic conversion
- **Path errors**: Logs errors but doesn't stop conversion

## Testing

Run the test script to verify functionality:

```bash
cd backend
python test_image_handling.py
```

This will test:
- Image path fixing for HTML and Markdown
- Media file organization
- Error handling scenarios

## Dependencies

Required Python packages:
- `Flask` - Web framework
- `PyMuPDF` - PDF processing (optional)
- `python-pptx` - PPTX processing (optional)
- `lxml` - XML processing

The system works even if optional dependencies are missing, with reduced functionality for PDF/PPTX processing. 