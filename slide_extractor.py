# import os
# import cv2
# import numpy as np
# import tempfile
# import shutil
# from PIL import Image
# import pytesseract
# from datetime import timedelta
# from skimage.metrics import structural_similarity as ssim
# from pytubefix import YouTube
# from pytubefix.cli import on_progress
# from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas

# class SlideExtractor:
#     def __init__(self, video_url, interval=5, similarity_threshold=0.7, ocr_confidence=30):
#         """
#         Initialize the SlideExtractor with the given parameters.
#         """
#         self.video_url = video_url
#         self.interval = interval
#         self.similarity_threshold = similarity_threshold
#         self.ocr_confidence = ocr_confidence
#         # Create a temporary directory for processing
#         self.temp_dir = tempfile.mkdtemp()
#         self.video_path = os.path.join(self.temp_dir, "temp_video.mp4")
#         self.slides_dir = os.path.join(self.temp_dir, "slides")
#         self.previous_text = ""
#         self.extracted_slides = []
        
#         # Ensure temp directory exists
#         os.makedirs(self.slides_dir, exist_ok=True)
    
#     def download_video(self):
#         """Download the YouTube video using pytubefix."""
#         try:
#             # Create a YouTube object with progress callback
#             yt = YouTube(self.video_url, on_progress_callback=on_progress)
            
#             # Get the highest resolution stream with video and audio
#             stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
#             if not stream:
#                 stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
            
#             if stream:
#                 video_file = stream.download(output_path=os.path.dirname(self.video_path),
#                                           filename=os.path.basename(self.video_path))
#                 return True
#             else:
#                 return False
#         except Exception as e:
#             print(f"Error downloading video: {str(e)}")
#             return False
    
#     def extract_slides(self):
#         """Process the video to extract slides."""
#         # Download the video
#         if not self.download_video():
#             return []
        
#         # Open the video file
#         cap = cv2.VideoCapture(self.video_path)
#         if not cap.isOpened():
#             return []
        
#         # Get video properties
#         fps = cap.get(cv2.CAP_PROP_FPS)
#         frame_interval = int(fps * self.interval)
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
#         prev_frame = None
#         slide_count = 0
        
#         # Process frames at regular intervals
#         for frame_num in range(0, total_frames, frame_interval):
#             cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
#             ret, frame = cap.read()
#             if not ret:
#                 continue
            
#             # Calculate timestamp for the current frame
#             current_time = frame_num / fps
#             timestamp = str(timedelta(seconds=current_time)).split(".")[0]
            
#             # First frame is always saved
#             if prev_frame is None:
#                 filename = self._save_slide(frame, timestamp, slide_count)
#                 self.extracted_slides.append(filename)
#                 prev_frame = frame
#                 slide_count += 1
#                 continue
            
#             # Check if current frame is a different slide
#             if self._is_different_slide(prev_frame, frame):
#                 filename = self._save_slide(frame, timestamp, slide_count)
#                 self.extracted_slides.append(filename)
#                 prev_frame = frame
#                 slide_count += 1
        
#         # Release the video capture object
#         cap.release()
#         return self.extracted_slides
    
#     def _is_different_slide(self, frame1, frame2):
#         """Determine if two frames represent different slides."""
#         # Convert frames to grayscale for comparison
#         gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
#         gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
#         # Calculate structural similarity between frames
#         score, _ = ssim(gray1, gray2, full=True)
        
#         # If similarity is below threshold, it's a different slide
#         if score < self.similarity_threshold:
#             return True
        
#         # Additional check using histogram comparison
#         hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
#         hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
#         hist_diff = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
#         if hist_diff < 0.95:
#             return True
        
#         # Additional check using OCR text comparison
#         text1 = self._extract_text(frame1)
#         text2 = self._extract_text(frame2)
        
#         if text1 and text2:
#             # Compare text content between frames
#             words1 = set(text1.split())
#             words2 = set(text2.split())
            
#             if len(words1) > 3 and len(words2) > 3:
#                 common_words = words1.intersection(words2)
#                 # Calculate difference ratio in text content
#                 diff_ratio = 1 - len(common_words) / max(len(words1), len(words2))
#                 # If text differs significantly, it's a different slide
#                 if diff_ratio > 0.3:
#                     return True
        
#         return False
    
#     def _extract_text(self, frame):
#         """Extract text from a frame using OCR."""
#         try:
#             # Convert to grayscale and threshold for better OCR
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             _, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
#             # Save temporary image for OCR processing
#             temp_image_path = os.path.join(self.temp_dir, "temp_ocr.png")
#             cv2.imwrite(temp_image_path, threshold)
            
#             # Extract text using pytesseract
#             text = pytesseract.image_to_string(
#                 Image.open(temp_image_path),
#                 config='--psm 6 --oem 3'
#             )
            
#             # Delete temporary file
#             if os.path.exists(temp_image_path):
#                 os.remove(temp_image_path)
                
#             return text.strip()
#         except Exception as e:
#             print(f"OCR error: {e}")
#             return ""
    
#     def _save_slide(self, frame, timestamp, count):
#         """Save a frame as a slide image."""
#         # Create filename with slide number and timestamp
#         filename = f"slide_{count:03d}_{timestamp.replace(':', '-')}.png"
#         path = os.path.join(self.slides_dir, filename)
        
#         # Convert BGR to RGB for proper color display
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         pil_image = Image.fromarray(rgb_frame)
#         pil_image.save(path)
        
#         return path
    
#     def generate_pdf_in_memory(self):
#         """Generate a PDF from slides in memory."""
#         buffer = BytesIO()
        
#         # Create PDF using reportlab
#         c = canvas.Canvas(buffer, pagesize=letter)
        
#         # Add each slide to the PDF
#         for img_path in self.extracted_slides:
#             if os.path.exists(img_path):
#                 img = Image.open(img_path)
#                 img_width, img_height = img.size
                
#                 # Calculate aspect ratio to fit on letter page
#                 width, height = letter
#                 ratio = min(width / img_width, height / img_height) * 0.9
                
#                 # Center the image on the page
#                 x = (width - img_width * ratio) / 2
#                 y = (height - img_height * ratio) / 2
                
#                 c.drawImage(img_path, x, y, width=img_width * ratio, height=img_height * ratio)
#                 c.showPage()
        
#         c.save()
#         buffer.seek(0)
#         return buffer
    
#     def cleanup(self):
#         """Clean up temporary files."""
#         try:
#             shutil.rmtree(self.temp_dir)
#         except Exception as e:
#             print(f"Error cleaning up temporary files: {str(e)}")


import os
import cv2
import numpy as np
import tempfile
import logging
import time
import shutil
from PIL import Image
import pytesseract
from datetime import timedelta
from skimage.metrics import structural_similarity as ssim
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SlideExtractor')

class SlideExtractor:
    def __init__(self, video_url, output_dir=None, interval=2, similarity_threshold=0.6, ocr_confidence=30):
        """
        Initialize the SlideExtractor with the given parameters.
        """
        self.video_url = video_url
        # Use provided output dir or create a temporary one
        self.output_dir = output_dir or tempfile.mkdtemp()
        self.interval = interval
        self.similarity_threshold = similarity_threshold
        self.ocr_confidence = ocr_confidence
        self.video_path = os.path.join(self.output_dir, "temp_video.mp4")
        self.previous_text = ""
        self.extracted_slides = []
        
        # Ensure output directory exists with proper permissions
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Initialized SlideExtractor with output_dir: {self.output_dir}")
        
        # Check if directory is writable
        if not os.access(self.output_dir, os.W_OK):
            raise PermissionError(f"Output directory {self.output_dir} is not writable")
    
    def download_video(self):
        """Download the YouTube video using pytubefix with retries."""
        logger.info(f"Attempting to download video: {self.video_url}")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Import here to avoid issues if not installed
                from pytubefix import YouTube
                from pytubefix.cli import on_progress
                
                # Create a YouTube object with progress callback
                yt = YouTube(self.video_url, on_progress_callback=on_progress)
                
                # Get video information
                logger.info(f"Video title: {yt.title}")
                logger.info(f"Video length: {yt.length} seconds")
                
                # Get the highest resolution stream with video and audio
                logger.info("Finding best stream...")
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                
                if not stream:
                    # If no combined stream is available, get the highest resolution video stream
                    stream = yt.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
                
                if stream:
                    # Start download
                    logger.info(f"Downloading {stream.resolution} stream...")
                    video_file = stream.download(output_path=os.path.dirname(self.video_path),
                                              filename=os.path.basename(self.video_path))
                    logger.info(f"Download complete! Video saved to: {self.video_path}")
                    
                    # Verify the file exists and has content
                    if os.path.exists(self.video_path) and os.path.getsize(self.video_path) > 0:
                        return True
                    else:
                        logger.error(f"Downloaded file is empty or doesn't exist")
                else:
                    logger.error(f"Attempt {attempt+1}: No suitable stream found")
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed: {str(e)}")
                # Wait before retrying
                time.sleep(2)
                
                # If on the last attempt, try alternative download method
                if attempt == max_retries - 1:
                    try:
                        logger.info("Trying alternative download method with youtube-dl")
                        import subprocess
                        
                        # Check if youtube-dl or yt-dlp is available
                        ytdl_cmd = 'yt-dlp' if shutil.which('yt-dlp') else 'youtube-dl'
                        
                        # Use youtube-dl/yt-dlp as fallback
                        subprocess.run([
                            ytdl_cmd, 
                            '-f', 'mp4', 
                            '-o', self.video_path, 
                            self.video_url
                        ], check=True)
                        
                        if os.path.exists(self.video_path) and os.path.getsize(self.video_path) > 0:
                            logger.info(f"Alternative download successful: {self.video_path}")
                            return True
                    except Exception as alt_e:
                        logger.error(f"Alternative download failed: {str(alt_e)}")
        
        return False
    
    def extract_slides(self):
        """Process the video to extract slides."""
        logger.info("Starting slide extraction process")
        
        # Download the video if it doesn't exist
        if not os.path.exists(self.video_path) or os.path.getsize(self.video_path) == 0:
            logger.info(f"Video file doesn't exist or is empty, downloading...")
            if not self.download_video():
                logger.error("Failed to download video")
                return []
        
        # Check if file exists and has content before opening
        if not os.path.exists(self.video_path):
            logger.error(f"Video file does not exist: {self.video_path}")
            return []
            
        if os.path.getsize(self.video_path) == 0:
            logger.error(f"Video file is empty: {self.video_path}")
            return []
        
        # Open the video file
        logger.info(f"Opening video file: {self.video_path}")
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            logger.error(f"Could not open video file {self.video_path}")
            # Try with alternative method
            logger.info("Trying alternative video opening method")
            try:
                import subprocess
                output_file = os.path.join(self.output_dir, "converted_video.mp4")
                subprocess.run([
                    'ffmpeg', 
                    '-i', self.video_path, 
                    '-c:v', 'libx264', 
                    '-crf', '23', 
                    '-preset', 'medium', 
                    output_file
                ], check=True)
                
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    self.video_path = output_file
                    cap = cv2.VideoCapture(self.video_path)
                    if not cap.isOpened():
                        logger.error("Still could not open video file after conversion")
                        return []
                else:
                    logger.error("Video conversion failed")
                    return []
            except Exception as e:
                logger.error(f"Error during video conversion: {str(e)}")
                return []
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            logger.error(f"Invalid FPS value: {fps}")
            fps = 25  # Default to a common value
            
        frame_interval = max(1, int(fps * self.interval))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= 0:
            logger.error(f"Invalid total frames value: {total_frames}")
            return []
            
        duration = total_frames / fps
        
        logger.info(f"Video duration: {timedelta(seconds=duration)}")
        logger.info(f"FPS: {fps}, Processing frames every {self.interval} seconds ({frame_interval} frames)")
        
        prev_frame = None
        slide_count = 0
        self.extracted_slides = []
        
        # Process frames at regular intervals
        for frame_num in range(0, total_frames, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Could not read frame {frame_num}")
                continue
            
            # Calculate timestamp for the current frame
            current_time = frame_num / fps
            timestamp = str(timedelta(seconds=current_time)).split(".")[0]
            
            # First frame is always saved
            if prev_frame is None:
                filename = self._save_slide(frame, timestamp, slide_count)
                self.extracted_slides.append(filename)
                prev_frame = frame.copy()  # Make a copy to avoid reference issues
                slide_count += 1
                continue
            
            # Check if current frame is a different slide
            if self._is_different_slide(prev_frame, frame):
                filename = self._save_slide(frame, timestamp, slide_count)
                self.extracted_slides.append(filename)
                prev_frame = frame.copy()  # Make a copy to avoid reference issues
                slide_count += 1
        
        # Release the video capture object
        cap.release()
        
        logger.info(f"Extracted {slide_count} slides to {self.output_dir}")
        return self.extracted_slides
    
    def _is_different_slide(self, frame1, frame2):
        """Determine if two frames represent different slides."""
        try:
            # Convert frames to grayscale for comparison
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            
            # Ensure both frames have the same dimensions for comparison
            if gray1.shape != gray2.shape:
                logger.warning("Frames have different dimensions, resizing for comparison")
                gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
            
            # Calculate structural similarity between frames
            score, _ = ssim(gray1, gray2, full=True)
            
            logger.debug(f"Similarity score: {score}")
            
            # If similarity is below threshold, it's a different slide
            if score < self.similarity_threshold:
                return True
            
            # Additional check using histogram comparison
            hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
            hist_diff = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            logger.debug(f"Histogram difference: {hist_diff}")
            
            if hist_diff < 0.95:
                return True
            
            # Additional check using OCR text comparison
            try:
                text1 = self._extract_text(frame1)
                text2 = self._extract_text(frame2)
                
                if text1 and text2:
                    # Compare text content between frames
                    words1 = set(text1.split())
                    words2 = set(text2.split())
                    
                    if len(words1) > 3 and len(words2) > 3:
                        common_words = words1.intersection(words2)
                        # Calculate difference ratio in text content
                        diff_ratio = 1 - len(common_words) / max(len(words1), len(words2))
                        
                        logger.debug(f"Text difference ratio: {diff_ratio}")
                        
                        # If text differs significantly, it's a different slide
                        if diff_ratio > 0.3:
                            return True
            except Exception as e:
                logger.warning(f"Error during OCR comparison: {str(e)}")
                # Continue with other methods if OCR fails
                pass
            
            return False
        except Exception as e:
            logger.error(f"Error during frame comparison: {str(e)}")
            # If comparison fails, assume frames are different to be safe
            return True
    
    def _extract_text(self, frame):
        """Extract text from a frame using OCR with fallback."""
        try:
            # Check if tesseract is available
            if shutil.which('tesseract') is None:
                logger.warning("Tesseract OCR not found, skipping text extraction")
                return ""
                
            # Convert to grayscale and threshold for better OCR
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # Save temporary image for OCR processing
            temp_image_path = os.path.join(self.output_dir, f"temp_ocr_{time.time()}.png")
            cv2.imwrite(temp_image_path, threshold)
            
            # Extract text using pytesseract
            text = pytesseract.image_to_string(
                Image.open(temp_image_path),
                config='--psm 6 --oem 3'
            )
            
            # Delete temporary file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
                
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR error: {str(e)}")
            return ""
    
    def _save_slide(self, frame, timestamp, count):
        """Save a frame as a slide image."""
        try:
            # Create filename with slide number and timestamp
            filename = f"slide_{count:03d}_{timestamp.replace(':', '-')}.png"
            path = os.path.join(self.output_dir, filename)
            
            # Convert BGR to RGB for proper color display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            pil_image.save(path)
            
            logger.info(f"Saved slide: {filename}")
            return path
        except Exception as e:
            logger.error(f"Error saving slide: {str(e)}")
            return None
    
    def convert_slides_to_pdf(self, pdf_path=None):
        """Convert all extracted slides to a single PDF file."""
        if pdf_path is None:
            pdf_path = os.path.join(self.output_dir, "slides_output.pdf")
            
        logger.info(f"Generating PDF at: {pdf_path}")
        
        try:
            # Create PDF using reportlab
            c = canvas.Canvas(pdf_path, pagesize=letter)
            
            # Add each slide to the PDF
            for img_path in self.extracted_slides:
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img_width, img_height = img.size
                    
                    # Calculate aspect ratio to fit on letter page
                    width, height = letter
                    ratio = min(width / img_width, height / img_height) * 0.9
                    
                    # Center the image on the page
                    x = (width - img_width * ratio) / 2
                    y = (height - img_height * ratio) / 2
                    
                    c.drawImage(img_path, x, y, width=img_width * ratio, height=img_height * ratio)
                    c.showPage()
            
            c.save()
            logger.info(f"PDF created successfully at: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
                logger.info(f"Cleaned up temporary directory: {self.output_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up: {str(e)}")
