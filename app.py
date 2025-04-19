from flask import Flask, render_template, request, session, redirect, url_for, Response, jsonify
import os
import threading
import time
import uuid
import tempfile
import shutil
from slide_extractor import SlideExtractor

# Initialize Flask application
app = Flask(__name__)
# Use environment variable for secret key with fallback
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Store active extractions with status (in-memory storage)
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
        threshold = float(request.form.get('threshold', 0.7))
        
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
    extractor.convert_slides_to_pdf(pdf_path)
    
    # Create response with PDF
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

def process_extraction(extraction_id, url, interval, threshold, temp_dir):
    """Process video extraction in a background thread."""
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
            active_extractions[extraction_id]['message'] = 'No slides were found. Try adjusting parameters.'
    
    except Exception as e:
        active_extractions[extraction_id]['status'] = 'error'
        active_extractions[extraction_id]['message'] = f'Error: {str(e)}'

def cleanup_extraction(extraction_id):
    """Clean up extraction temporary files."""
    try:
        if extraction_id in active_extractions:
            # Wait a bit to ensure download completes
            time.sleep(5)
            
            # Delete temporary directory after some time
            # We keep it briefly so the PDF can be downloaded
            time.sleep(300)  # Keep for 5 minutes after processing
            
            # Delete temporary directory
            temp_dir = active_extractions[extraction_id]['temp_dir']
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            # Remove from active extractions
            if extraction_id in active_extractions:
                del active_extractions[extraction_id]
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

# For proper deployment - this allows running with gunicorn
# Use environment variables for port configuration
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # For production, set debug to False
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
