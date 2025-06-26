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
    'dokuwiki', 'textile', 'rst', 'asciidoc', 'man', 'ms'
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
        'ms': 'ms'
    }
    
    return format_mapping.get(ext, 'markdown')

def convert_file_with_pandoc(input_path, output_path, input_format, output_format, extract_media_dir):
    """Convert file using Pandoc"""
    try:
        # Build pandoc command
        cmd = [
            'pandoc',
            input_path,
            '-f', input_format,
            '-t', output_format,
            '-o', output_path,
            '--extract-media', extract_media_dir
        ]
        
        # Add additional options based on output format
        if output_format == 'gfm':
            cmd.extend(['--wrap=none'])
        elif output_format == 'html':
            cmd.extend(['--standalone', '--self-contained'])
        elif output_format == 'pdf':
            cmd.extend(['--pdf-engine=xelatex'])
        
        # Execute pandoc command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, None
        
    except subprocess.CalledProcessError as e:
        return False, f"Pandoc error: {e.stderr}"
    except FileNotFoundError:
        return False, "Pandoc is not installed or not found in PATH"
    except Exception as e:
        return False, f"Conversion error: {str(e)}"

@app.route('/convert', methods=['POST'])
def convert_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        output_format = request.form.get('output_format', 'gfm')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400
        
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
                success, error = convert_file_with_pandoc(
                    input_path, output_path, input_format, output_format, media_dir
                )
                
                if success:
                    converted_files.append(output_filename)
                else:
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
        output_format = request.form.get('output_format', 'gfm')
        
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected for retry'}), 400
        
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