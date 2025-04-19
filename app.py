# from flask import Flask, render_template, request, session, redirect, url_for, Response, jsonify
# import os
# import threading
# import time
# import uuid
# import tempfile
# from slide_extractor import SlideExtractor

# app = Flask(__name__)
# app.secret_key = os.urandom(24)
# app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# # Store active extractions with status
# active_extractions = {}

# @app.route('/')
# def index():
#     """Main page with the form to extract slides."""
#     return render_template('index.html')

# @app.route('/extract', methods=['POST'])
# def extract():
#     """Handle the form submission to extract slides."""
#     if request.method == 'POST':
#         # Get input values
#         url = request.form.get('youtube_url')
#         interval = int(request.form.get('interval', 2))
#         threshold = float(request.form.get('threshold', 0.7))
        
#         # Validation
#         if not url:
#             return jsonify({'status': 'error', 'message': 'YouTube URL is required'})
        
#         if interval < 1 or interval > 30:
#             return jsonify({'status': 'error', 'message': 'Interval must be between 1 and 30 seconds'})
            
#         if threshold < 0.1 or threshold > 1.0:
#             return jsonify({'status': 'error', 'message': 'Threshold must be between 0.1 and 1.0'})
        
#         # Create a unique extraction ID for tracking
#         extraction_id = str(uuid.uuid4())
#         session['extraction_id'] = extraction_id
        
#         # Initialize status
#         active_extractions[extraction_id] = {
#             'status': 'downloading',
#             'progress': 0,
#             'message': 'Downloading video...',
#             'slides_count': 0,
#             'extractor': None
#         }
        
#         # Start extraction in a background thread
#         threading.Thread(
#             target=process_extraction,
#             args=(extraction_id, url, interval, threshold),
#             daemon=True
#         ).start()
        
#         return jsonify({
#             'status': 'success', 
#             'extraction_id': extraction_id,
#             'redirect': url_for('processing', extraction_id=extraction_id)
#         })

# @app.route('/processing/<extraction_id>')
# def processing(extraction_id):
#     """Show processing status page."""
#     if extraction_id not in active_extractions:
#         return redirect(url_for('index'))
    
#     return render_template('processing.html', extraction_id=extraction_id)

# @app.route('/status/<extraction_id>')
# def status(extraction_id):
#     """Return the current status of an extraction."""
#     if extraction_id not in active_extractions:
#         return jsonify({'status': 'error', 'message': 'Extraction not found'})
    
#     status_data = active_extractions[extraction_id]
#     return jsonify({
#         'status': status_data['status'],
#         'progress': status_data['progress'],
#         'message': status_data['message'],
#         'slides_count': status_data['slides_count']
#     })

# @app.route('/download-pdf/<extraction_id>')
# def download_pdf(extraction_id):
#     """Generate and download PDF for the extraction."""
#     if extraction_id not in active_extractions:
#         return redirect(url_for('index'))
    
#     status_data = active_extractions[extraction_id]
    
#     if status_data['status'] != 'completed':
#         return jsonify({'status': 'error', 'message': 'Extraction not yet completed'})
    
#     extractor = status_data['extractor']
#     if not extractor:
#         return jsonify({'status': 'error', 'message': 'Extractor not found'})
    
#     # Generate PDF in memory
#     pdf_buffer = extractor.generate_pdf_in_memory()
    
#     # Create response with PDF
#     response = Response(
#         pdf_buffer.getvalue(),
#         mimetype='application/pdf',
#         headers={'Content-Disposition': 'attachment;filename=slides.pdf'}
#     )
    
#     # Schedule cleanup in background thread (don't wait for it)
#     threading.Thread(
#         target=cleanup_extraction,
#         args=(extraction_id,),
#         daemon=True
#     ).start()
    
#     return response

# def process_extraction(extraction_id, url, interval, threshold):
#     """Process video extraction in a background thread."""
#     try:
#         # Update status
#         active_extractions[extraction_id]['status'] = 'downloading'
#         active_extractions[extraction_id]['message'] = 'Downloading video...'
        
#         # Create extractor
#         extractor = SlideExtractor(
#             video_url=url, 
#             interval=interval, 
#             similarity_threshold=threshold
#         )
        
#         # Store extractor in status
#         active_extractions[extraction_id]['extractor'] = extractor
        
#         # Update status
#         active_extractions[extraction_id]['status'] = 'extracting'
#         active_extractions[extraction_id]['message'] = 'Extracting slides...'
        
#         # Extract slides
#         slides = extractor.extract_slides()
        
#         # Update status based on results
#         if slides and len(slides) > 0:
#             active_extractions[extraction_id]['status'] = 'completed'
#             active_extractions[extraction_id]['message'] = f'Extraction complete! {len(slides)} slides found.'
#             active_extractions[extraction_id]['slides_count'] = len(slides)
#         else:
#             active_extractions[extraction_id]['status'] = 'error'
#             active_extractions[extraction_id]['message'] = 'No slides were found. Try adjusting parameters.'
    
#     except Exception as e:
#         active_extractions[extraction_id]['status'] = 'error'
#         active_extractions[extraction_id]['message'] = f'Error: {str(e)}'

# def cleanup_extraction(extraction_id):
#     """Clean up extraction resources."""
#     try:
#         if extraction_id in active_extractions:
#             extractor = active_extractions[extraction_id]['extractor']
#             if extractor:
#                 extractor.cleanup()
            
#             # Keep the status data for a while before removing
#             time.sleep(300)  # Keep for 5 minutes after download
#             if extraction_id in active_extractions:
#                 del active_extractions[extraction_id]
#     except Exception as e:
#         print(f"Error during cleanup: {str(e)}")

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, session, redirect, url_for, Response, jsonify
import os
import threading
import time
import uuid
import tempfile
import logging
from slide_extractor import SlideExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('YTSlideExtractor')

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# In-memory storage for active extractions
active_extractions = {}

@app.route('/')
def index():
    """Main page with the form to extract slides."""
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    """Handle the form submission to extract slides."""
    if request.method == 'POST':
        # Get input values
        url = request.form.get('youtube_url')
        interval = int(request.form.get('interval', 2))
        threshold = float(request.form.get('threshold', 0.6))  # Lower default for cloud environment
        
        # Validation
        if not url:
            return jsonify({'status': 'error', 'message': 'YouTube URL is required'})
        
        if interval < 1 or interval > 30:
            return jsonify({'status': 'error', 'message': 'Interval must be between 1 and 30 seconds'})
            
        if threshold < 0.1 or threshold > 1.0:
            return jsonify({'status': 'error', 'message': 'Threshold must be between 0.1 and 1.0'})
        
        # Create a unique extraction ID for tracking
        extraction_id = str(uuid.uuid4())
        session['extraction_id'] = extraction_id
        
        # Create temp directory for this extraction
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temp directory: {temp_dir} for extraction ID: {extraction_id}")
        
        # Initialize status
        active_extractions[extraction_id] = {
            'status': 'downloading',
            'progress': 0,
            'message': 'Downloading video...',
            'slides_count': 0,
            'temp_dir': temp_dir,
            'extractor': None
        }
        
        # Start extraction in a background thread
        threading.Thread(
            target=process_extraction,
            args=(extraction_id, url, interval, threshold, temp_dir),
            daemon=True
        ).start()
        
        return jsonify({
            'status': 'success', 
            'extraction_id': extraction_id,
            'redirect': url_for('processing', extraction_id=extraction_id)
        })

@app.route('/processing/<extraction_id>')
def processing(extraction_id):
    """Show processing status page."""
    if extraction_id not in active_extractions:
        return redirect(url_for('index'))
    
    return render_template('processing.html', extraction_id=extraction_id)

@app.route('/status/<extraction_id>')
def status(extraction_id):
    """Return the current status of an extraction."""
    if extraction_id not in active_extractions:
        return jsonify({'status': 'error', 'message': 'Extraction not found'})
    
    status_data = active_extractions[extraction_id]
    return jsonify({
        'status': status_data['status'],
        'progress': status_data['progress'],
        'message': status_data['message'],
        'slides_count': status_data['slides_count']
    })

@app.route('/download-pdf/<extraction_id>')
def download_pdf(extraction_id):
    """Generate and download PDF for the extraction."""
    if extraction_id not in active_extractions:
        return redirect(url_for('index'))
    
    status_data = active_extractions[extraction_id]
    
    if status_data['status'] != 'completed':
        return jsonify({'status': 'error', 'message': 'Extraction not yet completed'})
    
    extractor = status_data['extractor']
    if not extractor:
        return jsonify({'status': 'error', 'message': 'Extractor not found'})
    
    # PDF path
    pdf_path = os.path.join(status_data['temp_dir'], 'slides.pdf')
    
    # Generate PDF
    pdf_path = extractor.convert_slides_to_pdf(pdf_path)
    
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'status': 'error', 'message': 'Failed to generate PDF'})
    
    # Create response with PDF
    try:
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        response = Response(
            pdf_data,
            mimetype='application/pdf',
            headers={'Content-Disposition': 'attachment;filename=slides.pdf'}
        )
        
        # Schedule cleanup in background thread (don't wait for it)
        threading.Thread(
            target=cleanup_extraction,
            args=(extraction_id,),
            daemon=True
        ).start()
        
        return response
    except Exception as e:
        logger.error(f"Error sending PDF: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error downloading PDF: {str(e)}'})

def process_extraction(extraction_id, url, interval, threshold, temp_dir):
    """Process video extraction in a background thread."""
    logger.info(f"Starting extraction process for ID: {extraction_id}")
    
    try:
        # Update status
        active_extractions[extraction_id]['status'] = 'downloading'
        active_extractions[extraction_id]['message'] = 'Downloading video...'
        
        # Create extractor with temp directory
        extractor = SlideExtractor(
            video_url=url, 
            output_dir=temp_dir,
            interval=interval, 
            similarity_threshold=threshold
        )
        
        # Store extractor in status
        active_extractions[extraction_id]['extractor'] = extractor
        
        # Update status
        active_extractions[extraction_id]['status'] = 'extracting'
        active_extractions[extraction_id]['message'] = 'Extracting slides...'
        
        # Extract slides
        slides = extractor.extract_slides()
        
        # Update status based on results
        if slides and len(slides) > 0:
            active_extractions[extraction_id]['status'] = 'completed'
            active_extractions[extraction_id]['message'] = f'Extraction complete! {len(slides)} slides found.'
            active_extractions[extraction_id]['slides_count'] = len(slides)
        else:
            active_extractions[extraction_id]['status'] = 'error'
            active_extractions[extraction_id]['message'] = 'No slides were found. Try adjusting parameters to lower values like interval=1 and threshold=0.5.'
    
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")
        active_extractions[extraction_id]['status'] = 'error'
        active_extractions[extraction_id]['message'] = f'Error: {str(e)}'

def cleanup_extraction(extraction_id):
    """Clean up extraction temporary files."""
    try:
        if extraction_id in active_extractions:
            # Wait a bit to ensure PDF download completes
            time.sleep(5)
            
            logger.info(f"Starting cleanup for extraction ID: {extraction_id}")
            
            # Keep data for 5 minutes after processing
            time.sleep(300)
            
            # Get extractor and temp directory
            extractor = active_extractions[extraction_id].get('extractor')
            temp_dir = active_extractions[extraction_id].get('temp_dir')
            
            # Clean up extractor resources
            if extractor:
                extractor.cleanup()
            
            # Remove from active extractions
            if extraction_id in active_extractions:
                del active_extractions[extraction_id]
                
            logger.info(f"Completed cleanup for extraction ID: {extraction_id}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

# For deployment - use environment variable for port or default to 5000
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
