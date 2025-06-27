import os
import tempfile
import zipfile
import subprocess
import shutil
import logging
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
import fitz  # PyMuPDF for PDF processing
from pptx import Presentation  # python-pptx for PPTX processing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {
    'docx', 'doc', 'odt', 'rtf', 'html', 'htm', 'txt', 'md', 'markdown', 
    'tex', 'latex', 'epub', 'mobi', 'fb2', 'opml', 'org', 'mediawiki', 
    'dokuwiki', 'textile', 'rst', 'asciidoc', 'man', 'ms', 'docbook', 'xml',
    'jats', 'tei', 'ris', 'csljson', 'endnotexml', 'ipynb', 'csv', 'tsv',
    'json', 'native', 'typst', 'djot', 'creole', 'tikiwiki', 'twiki', 'vimwiki',
    'muse', 'pod', 't2t', 'haddock', 'mdoc', 'biblatex', 'bibtex', 'bits',
    'pdf', 'pptx'  # Added PDF and PPTX support
}

# Create directories if they don't exist
try:
    logger.info("Creating uploads directory...")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    logger.info("Creating output directory...")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    logger.info("Directories created successfully")
except Exception as e:
    logger.error(f"Error creating directories: {e}")
    raise

# Check Pandoc availability at startup
# try:
#     logger.info("Checking Pandoc availability...")
#     result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True, timeout=10)
#     if result.returncode == 0:
#         logger.info(f"Pandoc is available: {result.stdout.split('\n')[0]}")
#     else:
#         logger.warning("Pandoc check failed")
# except Exception as e:
#     logger.warning(f"Could not check Pandoc: {e}")

logger.info("Application startup completed")

print("ALL ENV VARS:", dict(os.environ))

print("PORT ENV:", os.environ.get("PORT"))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_input_format(filename):
    """Determine input format based on file extension"""
    ext = filename.rsplit('.', 1)[1].lower()
    
    format_mapping = {
        'docx': 'docx',
        'doc': 'doc',
        'odt': 'odt',
        'rtf': 'rtf',
        'html': 'html',
        'htm': 'html',
        'txt': 'plain',
        'md': 'markdown',
        'markdown': 'markdown',
        'tex': 'latex',
        'latex': 'latex',
        'epub': 'epub',
        'mobi': 'mobi',
        'fb2': 'fb2',
        'opml': 'opml',
        'org': 'org',
        'mediawiki': 'mediawiki',
        'dokuwiki': 'dokuwiki',
        'textile': 'textile',
        'rst': 'rst',
        'asciidoc': 'asciidoc',
        'man': 'man',
        'ms': 'ms',
        'docbook': 'docbook',
        'xml': 'docbook',  # Default XML format
        'jats': 'jats',
        'tei': 'tei',
        'ris': 'ris',
        'csljson': 'csljson',
        'endnotexml': 'endnotexml',
        'ipynb': 'ipynb',
        'csv': 'csv',
        'tsv': 'tsv',
        'json': 'json',
        'native': 'native',
        'typst': 'typst',
        'djot': 'djot',
        'creole': 'creole',
        'tikiwiki': 'tikiwiki',
        'twiki': 'twiki',
        'vimwiki': 'vimwiki',
        'muse': 'muse',
        'pod': 'pod',
        't2t': 't2t',
        'haddock': 'haddock',
        'mdoc': 'mdoc',
        'biblatex': 'biblatex',
        'bibtex': 'bibtex',
        'bits': 'bits',
        'pdf': 'pdf',  # Added PDF support
        'pptx': 'pptx'  # Added PPTX support
    }
    
    return format_mapping.get(ext, 'markdown')

def get_format_suggestions(invalid_format):
    """Get suggestions for similar or common formats when an invalid format is entered"""
    common_formats = {
        'pdf': ['pdf'],
        'word': ['docx'],
        'powerpoint': ['pptx'],
        'html': ['html', 'html5', 'xhtml'],
        'markdown': ['markdown', 'gfm', 'commonmark'],
        'text': ['txt', 'plain'],
        'xml': ['xml', 'docbook', 'jats', 'tei'],
        'latex': ['latex', 'tex'],
        'epub': ['epub', 'epub2', 'epub3'],
        'presentation': ['revealjs', 'beamer', 's5', 'slidy'],
        'documentation': ['docbook', 'jats', 'asciidoc', 'rst']
    }
    
    suggestions = []
    invalid_lower = invalid_format.lower()
    
    for category, formats in common_formats.items():
        if invalid_lower in category or any(invalid_lower in fmt for fmt in formats):
            suggestions.extend(formats)
    
    # Add some common formats if no specific matches
    if not suggestions:
        suggestions = ['pdf', 'docx', 'html', 'markdown', 'txt', 'xml']
    
    return list(set(suggestions))[:5]  # Return up to 5 unique suggestions

def is_format_supported(output_format):
    """Check if the output format is supported by Pandoc - now more permissive"""
    # Allow any format input and let Pandoc handle validation
    # This makes the system more flexible for custom formats
    return True

def validate_output_file(output_path, output_format):
    """Validate that the output file was created correctly for the given format"""
    try:
        # Check if file exists and has content
        if not os.path.exists(output_path):
            return False, "Output file was not created"
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            return False, "Output file is empty"
        
        # Basic validation for any format - just check if file has content
        # This allows maximum flexibility for any output format
        
        # For binary formats, just check file size
        if output_format in ['pdf', 'docx', 'pptx', 'odt', 'epub', 'mobi', 'fb2']:
            if file_size < 50:  # Even small binary files should have some content
                return False, f"Output {output_format} file appears to be corrupted (too small)"
        
        # For text-based formats, check for content
        else:
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read(100)  # Read first 100 chars
                    if not content.strip():
                        return False, f"Output {output_format} file is empty"
            except UnicodeDecodeError:
                # If it's not UTF-8, it might be a binary format we didn't expect
                # Just check if it has reasonable size
                if file_size < 50:
                    return False, f"Output {output_format} file appears to be corrupted (too small)"
        
        # If we get here, the file appears valid
        return True, f"Output {output_format} file validated successfully"
        
    except Exception as e:
        return False, f"Error validating output file: {str(e)}"

def convert_file_with_pandoc(input_path, output_path, input_format, output_format, extract_media_dir):
    """Convert file using Pandoc with precise format-specific options"""
    try:
        # Build base pandoc command
        cmd = [
            'pandoc',
            input_path,
            '-f', input_format,
            '-t', output_format,
            '-o', output_path,
            '--extract-media', extract_media_dir
        ]
        
        # Add format-specific options for precise conversion
        if output_format == 'gfm':
            cmd.extend(['--wrap=none', '--markdown-headings=atx'])
        elif output_format == 'markdown':
            cmd.extend(['--wrap=none'])
        elif output_format == 'html':
            cmd.extend(['--standalone', '--self-contained'])
        elif output_format == 'html5':
            cmd.extend(['--standalone', '--self-contained', '--to=html5'])
        elif output_format == 'xhtml':
            cmd.extend(['--standalone', '--self-contained', '--to=xhtml'])
        elif output_format == 'pdf':
            cmd.extend(['--pdf-engine=xelatex'])
        elif output_format == 'latex':
            cmd.extend(['--standalone'])
        elif output_format == 'docx':
            cmd.extend(['--reference-doc='])  # Use default template
        elif output_format == 'pptx':
            cmd.extend(['--reference-doc='])  # Use default template
        elif output_format == 'odt':
            cmd.extend(['--reference-doc='])  # Use default template
        elif output_format == 'rtf':
            cmd.extend([])  # No special options needed
        elif output_format == 'epub':
            cmd.extend(['--epub-cover-image='])  # No cover image
        elif output_format == 'epub2':
            cmd.extend(['--to=epub2'])
        elif output_format == 'epub3':
            cmd.extend(['--to=epub3'])
        elif output_format == 'txt':
            cmd.extend(['--wrap=none'])
        elif output_format == 'xml':
            cmd.extend(['--standalone'])
        elif output_format == 'docbook':
            cmd.extend(['--standalone', '--to=docbook5'])
        elif output_format == 'docbook5':
            cmd.extend(['--standalone', '--to=docbook5'])
        elif output_format == 'docbook4':
            cmd.extend(['--standalone', '--to=docbook4'])
        elif output_format == 'jats':
            cmd.extend(['--standalone', '--to=jats'])
        elif output_format == 'jats_archiving':
            cmd.extend(['--standalone', '--to=jats_archiving'])
        elif output_format == 'jats_publishing':
            cmd.extend(['--standalone', '--to=jats_publishing'])
        elif output_format == 'jats_articleauthoring':
            cmd.extend(['--standalone', '--to=jats_articleauthoring'])
        elif output_format == 'revealjs':
            cmd.extend(['--standalone', '--to=revealjs'])
        elif output_format == 'beamer':
            cmd.extend(['--pdf-engine=xelatex', '--to=beamer'])
        elif output_format == 's5':
            cmd.extend(['--standalone', '--to=s5'])
        elif output_format == 'slideous':
            cmd.extend(['--standalone', '--to=slideous'])
        elif output_format == 'dzslides':
            cmd.extend(['--standalone', '--to=dzslides'])
        elif output_format == 'slidy':
            cmd.extend(['--standalone', '--to=slidy'])
        elif output_format == 'asciidoc':
            cmd.extend(['--wrap=none'])
        elif output_format == 'rst':
            cmd.extend(['--wrap=none'])
        elif output_format == 'org':
            cmd.extend(['--wrap=none'])
        elif output_format == 'textile':
            cmd.extend(['--wrap=none'])
        elif output_format == 'mediawiki':
            cmd.extend(['--wrap=none'])
        elif output_format == 'dokuwiki':
            cmd.extend(['--wrap=none'])
        elif output_format == 'haddock':
            cmd.extend(['--wrap=none'])
        elif output_format == 'man':
            cmd.extend([])
        elif output_format == 'ms':
            cmd.extend([])
        elif output_format == 'opml':
            cmd.extend(['--standalone'])
        elif output_format == 'fb2':
            cmd.extend(['--standalone'])
        elif output_format == 'mobi':
            cmd.extend(['--standalone'])
        elif output_format == 'icml':
            cmd.extend(['--standalone'])
        elif output_format == 'tei':
            cmd.extend(['--standalone'])
        elif output_format == 'native':
            cmd.extend([])
        elif output_format == 'json':
            cmd.extend(['--to=json'])
        elif output_format == 'commonmark':
            cmd.extend(['--wrap=none', '--to=commonmark'])
        elif output_format == 'commonmark_x':
            cmd.extend(['--wrap=none', '--to=commonmark_x'])
        elif output_format == 'markua':
            cmd.extend(['--wrap=none', '--to=markua'])
        elif output_format == 'spip':
            cmd.extend(['--wrap=none'])
        elif output_format == 'texinfo':
            cmd.extend(['--standalone'])
        elif output_format == 'opendocument':
            cmd.extend(['--to=opendocument'])
        else:
            # For any other format, try direct conversion without special options
            # This allows maximum flexibility for custom formats
            cmd.extend([])
        
        # Execute pandoc command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Validate the output file
        validation_success, validation_message = validate_output_file(output_path, output_format)
        if not validation_success:
            return False, f"Conversion completed but validation failed: {validation_message}"
        
        return True, None
        
    except subprocess.CalledProcessError as e:
        return False, f"Pandoc error: {e.stderr}"
    except FileNotFoundError:
        return False, "Pandoc is not installed or not found in PATH"
    except Exception as e:
        return False, f"Conversion error: {str(e)}"

def convert_pdf_to_markdown(pdf_path, output_path):
    """Convert PDF to Markdown using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        markdown_content = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # Clean up the text
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # Try to detect headers (simple heuristic)
                    if len(line) < 100 and line.isupper():
                        cleaned_lines.append(f"# {line.title()}")
                    else:
                        cleaned_lines.append(line)
            
            if cleaned_lines:
                markdown_content.extend(cleaned_lines)
                markdown_content.append('')  # Add blank line between pages
        
        doc.close()
        
        # Write to markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))
        
        return True, None
        
    except Exception as e:
        return False, f"PDF conversion error: {str(e)}"

def convert_pptx_to_markdown(pptx_path, output_path):
    """Convert PPTX to Markdown using python-pptx"""
    try:
        prs = Presentation(pptx_path)
        markdown_content = []
        
        for slide_num, slide in enumerate(prs.slides, 1):
            # Add slide header
            markdown_content.append(f"# Slide {slide_num}")
            markdown_content.append('')
            
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    text = shape.text.strip()
                    
                    # Try to detect if it's a title or content
                    if len(text) < 100 and text.isupper():
                        markdown_content.append(f"## {text.title()}")
                    else:
                        # Split into paragraphs
                        paragraphs = text.split('\n')
                        for para in paragraphs:
                            if para.strip():
                                markdown_content.append(para.strip())
                                markdown_content.append('')
            
            markdown_content.append('---')  # Slide separator
            markdown_content.append('')
        
        # Write to markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))
        
        return True, None
        
    except Exception as e:
        return False, f"PPTX conversion error: {str(e)}"

def preprocess_special_formats(input_path, input_format, temp_dir):
    """Preprocess special formats (PDF, PPTX) to convert them to Pandoc-supported formats"""
    try:
        if input_format == 'pdf':
            # Convert PDF to Markdown first
            temp_md_path = os.path.join(temp_dir, 'temp_converted.md')
            success, error = convert_pdf_to_markdown(input_path, temp_md_path)
            if success:
                return temp_md_path, 'markdown'
            else:
                return None, error
                
        elif input_format == 'pptx':
            # Convert PPTX to Markdown first
            temp_md_path = os.path.join(temp_dir, 'temp_converted.md')
            success, error = convert_pptx_to_markdown(input_path, temp_md_path)
            if success:
                return temp_md_path, 'markdown'
            else:
                return None, error
                
        else:
            # No preprocessing needed for other formats
            return input_path, input_format
            
    except Exception as e:
        return None, f"Preprocessing error: {str(e)}"

@app.route('/convert', methods=['POST'])
def convert_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        output_format = request.form.get('output_format', 'pdf')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Validate output format
        if not output_format or output_format.strip() == '':
            return jsonify({'error': 'Output format is required'}), 400
        
        # Clean the output format
        output_format = output_format.strip().lower()
        
        # Create unique session directory
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(OUTPUT_FOLDER, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Create subdirectories
        uploads_dir = os.path.join(session_dir, 'uploads')
        converted_dir = os.path.join(session_dir, 'converted')
        media_dir = os.path.join(session_dir, 'media')
        
        os.makedirs(uploads_dir, exist_ok=True)
        os.makedirs(converted_dir, exist_ok=True)
        os.makedirs(media_dir, exist_ok=True)
        
        conversion_errors = []
        converted_files = []
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                # Save uploaded file
                filename = secure_filename(file.filename)
                input_path = os.path.join(uploads_dir, filename)
                file.save(input_path)
                
                # Determine input format
                input_format = get_input_format(filename)
                
                # Preprocess special formats (PDF, PPTX) if needed
                processed_input_path, processed_input_format = preprocess_special_formats(
                    input_path, input_format, uploads_dir
                )
                
                if processed_input_path is None:
                    logger.error(f"Failed to preprocess {filename}: {processed_input_format}")
                    conversion_errors.append(f"{filename}: {processed_input_format}")
                    continue
                
                # Generate output filename
                base_name = os.path.splitext(filename)[0]
                
                # Define common format extensions
                format_extensions = {
                    'gfm': 'md',
                    'markdown': 'md',
                    'html': 'html',
                    'latex': 'tex',
                    'pdf': 'pdf',
                    'docx': 'docx',
                    'odt': 'odt',
                    'rtf': 'rtf',
                    'epub': 'epub',
                    'pptx': 'pptx',
                    'xml': 'xml',
                    'txt': 'txt',
                    'docbook': 'xml',
                    'jats': 'xml',
                    'opendocument': 'odt',
                    'revealjs': 'html',
                    'beamer': 'pdf',
                    's5': 'html',
                    'slideous': 'html',
                    'dzslides': 'html',
                    'slidy': 'html',
                    'asciidoc': 'adoc',
                    'rst': 'rst',
                    'org': 'org',
                    'textile': 'textile',
                    'mediawiki': 'wiki',
                    'dokuwiki': 'txt',
                    'haddock': 'hs',
                    'man': 'man',
                    'ms': 'ms',
                    'opml': 'opml',
                    'fb2': 'fb2',
                    'mobi': 'mobi',
                    'icml': 'icml',
                    'tei': 'xml',
                    'native': 'native',
                    'json': 'json',
                    'docbook5': 'xml',
                    'docbook4': 'xml',
                    'jats_archiving': 'xml',
                    'jats_publishing': 'xml',
                    'jats_articleauthoring': 'xml',
                    'html5': 'html',
                    'html4': 'html',
                    'xhtml': 'xhtml',
                    'xhtml5': 'xhtml',
                    'xhtml4': 'xhtml',
                    'markdown_github': 'md',
                    'markdown_mmd': 'md',
                    'markdown_phpextra': 'md',
                    'markdown_strict': 'md',
                    'markdown_texinfo': 'texi',
                    'commonmark': 'md',
                    'commonmark_x': 'md',
                    'gfm': 'md',
                    'markua': 'md',
                    'spip': 'txt',
                    'epub2': 'epub',
                    'epub3': 'epub',
                    'docbook4': 'xml',
                    'docbook5': 'xml',
                    'man': 'man',
                    'ms': 'ms',
                    'texinfo': 'texi',
                    'textile': 'textile',
                    'org': 'org',
                    'asciidoc': 'adoc',
                    'rst': 'rst',
                    'mediawiki': 'wiki',
                    'dokuwiki': 'txt',
                    'haddock': 'hs',
                    'opml': 'opml',
                    'fb2': 'fb2',
                    'mobi': 'mobi',
                    'icml': 'icml',
                    'tei': 'xml',
                    'native': 'native',
                    'json': 'json',
                    'jats_archiving': 'xml',
                    'jats_publishing': 'xml',
                    'jats_articleauthoring': 'xml',
                    'html5': 'html',
                    'html4': 'html',
                    'xhtml': 'xhtml',
                    'xhtml5': 'xhtml',
                    'xhtml4': 'xhtml',
                    'markdown_github': 'md',
                    'markdown_mmd': 'md',
                    'markdown_phpextra': 'md',
                    'markdown_strict': 'md',
                    'markdown_texinfo': 'texi',
                    'commonmark': 'md',
                    'commonmark_x': 'md',
                    'gfm': 'md',
                    'markua': 'md',
                    'spip': 'txt',
                    'epub2': 'epub',
                    'epub3': 'epub',
                    'texinfo': 'texi'
                }
                
                # Get extension for the output format
                extension = format_extensions.get(output_format, output_format)
                output_filename = f"{base_name}.{extension}"
                
                output_path = os.path.join(converted_dir, output_filename)
                
                # Convert file
                logger.info(f"Converting {filename} from {input_format} to {output_format}")
                success, error = convert_file_with_pandoc(
                    processed_input_path, output_path, processed_input_format, output_format, media_dir
                )
                
                if success:
                    logger.info(f"Successfully converted {filename} to {output_filename} and validated output")
                    converted_files.append(output_filename)
                else:
                    logger.error(f"Failed to convert {filename}: {error}")
                    conversion_errors.append(f"{filename}: {error}")
            else:
                conversion_errors.append(f"Invalid file type: {file.filename}")
        
        if not converted_files:
            error_msg = "No files were successfully converted."
            if conversion_errors:
                error_msg += " Errors: " + "; ".join(conversion_errors)
            return jsonify({'error': error_msg}), 400
        
        # Create ZIP file
        zip_filename = f"converted_files_{session_id}.zip"
        zip_path = os.path.join(session_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add converted files
            for filename in os.listdir(converted_dir):
                file_path = os.path.join(converted_dir, filename)
                zipf.write(file_path, filename)
            
            # Add media files if they exist
            if os.path.exists(media_dir) and os.listdir(media_dir):
                for root, dirs, files in os.walk(media_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Preserve directory structure in ZIP
                        arcname = os.path.relpath(file_path, session_dir)
                        zipf.write(file_path, arcname)
        
        # Clean up uploaded files (keep converted and zip for download)
        shutil.rmtree(uploads_dir, ignore_errors=True)
        
        # Return ZIP file
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

@app.route('/retry', methods=['POST'])
def retry_conversion():
    """Retry a failed conversion with the same parameters"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided for retry'}), 400
        
        files = request.files.getlist('files')
        output_format = request.form.get('output_format', 'pdf')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected for retry'}), 400
        
        # Validate output format
        if not output_format or output_format.strip() == '':
            return jsonify({'error': 'Output format is required for retry'}), 400
        
        # Clean the output format
        output_format = output_format.strip().lower()
        
        # Log retry attempt
        logger.info(f"Retry conversion requested for {len(files)} files to {output_format}")
        
        # Use the same conversion logic as /convert
        return convert_files()
        
    except Exception as e:
        logger.error(f"Retry conversion error: {str(e)}")
        return jsonify({'error': f'Retry failed: {str(e)}'}), 500

@app.route('/')
def index():
    return "Backend server is running. Use /convert, /retry, or /health endpoints."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(use_reloader=False, debug=False, host='0.0.0.0', port=port)