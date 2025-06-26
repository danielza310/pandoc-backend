#!/usr/bin/env python3
"""
Startup debug script to identify issues during application startup
"""
import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Check environment variables and system state"""
    logger.info("=== Environment Check ===")
    
    # Check PORT environment variable
    port = os.environ.get('PORT', '8080')
    logger.info(f"PORT: {port}")
    
    # Check current working directory
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Check if directories exist
    dirs_to_check = ['uploads', 'output', '.']
    for dir_name in dirs_to_check:
        if os.path.exists(dir_name):
            logger.info(f"Directory '{dir_name}' exists")
        else:
            logger.warning(f"Directory '{dir_name}' does not exist")
    
    # Check file permissions
    try:
        os.makedirs('uploads', exist_ok=True)
        logger.info("Can create uploads directory")
    except Exception as e:
        logger.error(f"Cannot create uploads directory: {e}")
    
    try:
        os.makedirs('output', exist_ok=True)
        logger.info("Can create output directory")
    except Exception as e:
        logger.error(f"Cannot create output directory: {e}")

def check_dependencies():
    """Check if required dependencies are available"""
    logger.info("=== Dependency Check ===")
    
    # Check Python version
    logger.info(f"Python version: {sys.version}")
    
    # Check Pandoc
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            first_line = result.stdout.split('\n')[0]
            logger.info(f"Pandoc available: {first_line}")
        else:
            logger.error(f"Pandoc check failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("Pandoc check timed out")
    except FileNotFoundError:
        logger.error("Pandoc not found")
    except Exception as e:
        logger.error(f"Pandoc check error: {e}")
    
    # Check XeLaTeX
    try:
        result = subprocess.run(['xelatex', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("XeLaTeX available")
        else:
            logger.warning(f"XeLaTeX check failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.warning("XeLaTeX check timed out")
    except FileNotFoundError:
        logger.warning("XeLaTeX not found")
    except Exception as e:
        logger.warning(f"XeLaTeX check error: {e}")

def check_imports():
    """Check if all required Python modules can be imported"""
    logger.info("=== Import Check ===")
    
    modules = [
        'flask',
        'flask_cors', 
        'werkzeug',
        'uuid',
        'zipfile',
        'subprocess',
        'shutil',
        'tempfile'
    ]
    
    for module in modules:
        try:
            __import__(module)
            logger.info(f"Module '{module}' imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import '{module}': {e}")

def main():
    """Run all checks"""
    logger.info("Starting startup debug checks...")
    
    check_environment()
    check_dependencies()
    check_imports()
    
    logger.info("Startup debug checks completed")
    
    # Try to import and initialize the Flask app
    logger.info("=== Flask App Test ===")
    try:
        from app import app
        logger.info("Flask app imported successfully")
        
        # Test basic app functionality
        with app.test_client() as client:
            response = client.get('/')
            logger.info(f"Root endpoint test: {response.status_code}")
            
            response = client.get('/health')
            logger.info(f"Health endpoint test: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Flask app test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    main() 