# YouTube Slide Extractor 📚🎞️

> Extract slides from educational YouTube videos and download them as PDFs with just a few clicks!



## 🌟 Features

- **🎬 YouTube Integration**: Extract slides directly from any YouTube educational video URL
- **⚙️ Customizable Parameters**: Adjust frame interval and similarity threshold for more accurate slide detection
- **🧠 Intelligent Detection**: Uses image comparison and text recognition to identify unique slides
- **📄 PDF Generation**: Download all extracted slides as a single, organized PDF document
- **🔒 Privacy-Focused**: No permanent data storage - all files are deleted after processing
- **🎨 Modern UI**: Clean, responsive user interface that works on desktop and mobile devices
- **⚡ Background Processing**: Extraction happens in the background with real-time status updates

## 📋 How It Works

1. **Input YouTube URL**: Paste any educational YouTube video URL
2. **Set Parameters**: 
   - Frame Interval (seconds): How often to check for new slides (2-5 seconds recommended)
   - Similarity Threshold (0.1-1.0): Lower values detect more changes (0.7 recommended)
3. **Process Video**: The application:
   - Downloads the YouTube video temporarily
   - Analyzes frames at specified intervals
   - Compares consecutive frames using image similarity and text recognition
   - Identifies unique slides based on your parameters
4. **Generate Results**: All detected slides are compiled into a downloadable PDF

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- Tesseract OCR engine

### Step 1: Clone the repository

```bash
git clone https://github.com/ocean-master0/youtube-slide-extractor.git
cd youtube-slide-extractor
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the application

```bash
python app.py
```

The application will start at `http://127.0.0.1:5000/`

## 💻 Usage Examples

### Basic Extraction

1. Enter a YouTube URL (e.g., a lecture or presentation)
2. Keep default settings (2 second interval, 0.7 threshold)
3. Click "Extract Slides"
4. Wait for processing to complete
5. Download your PDF containing all slides

### Fine-Tuned Extraction

For videos with rapid slide changes:
- Set interval to 1 second
- Set threshold to 0.6
- This will catch more subtle changes between slides

For videos with slower content:
- Set interval to 5 seconds (saves processing time)
- Set threshold to 0.8 (reduces duplicate slides)

## 🧰 Technical Details

### Dependencies

- **Flask**: Web framework for the interface
- **pytubefix**: For downloading YouTube videos
- **OpenCV**: For image processing and comparison
- **Pytesseract**: For optical character recognition (OCR)
- **scikit-image**: For structural similarity calculation
- **ReportLab**: For PDF generation

### File Structure

```
youtube-slide-extractor/
├── app.py                 # Main Flask application
├── slide_extractor.py     # Core slide extraction logic
├── static/
│   ├── css/
│   │   └── style.css      # Custom styling
│   ├── js/
│   │   └── main.js        # Frontend functionality
│   └── img/
│       └── logo.png       # App logo
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Main page
│   └── processing.html    # Processing status page
└── requirements.txt       # Project dependencies
```

### Algorithm Overview

1. **Video Download**: Secure YouTube video downloading via pytubefix
2. **Frame Extraction**: Capture frames at specified intervals
3. **Similarity Detection**: Multiple detection methods:
   - Structural Similarity Index (SSIM) comparison
   - Histogram comparison
   - OCR text difference analysis
4. **In-Memory Processing**: All operations performed in memory with temporary storage
5. **PDF Generation**: ReportLab for high-quality PDF creation with preserved aspect ratios

## 📷 Screenshots

*Screenshots coming soon!*

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**[Your Name]**

- GitHub: [ocean-master0](https://github.com/ocean-master0)
- Website: [your-website.com](https://your-website.com)

## 🔗 Hosted Version

You can try the online hosted version here: **[Live Demo](#)** *(Coming Soon!)*

---

⭐ If you find this project useful, consider giving it a star on GitHub!

📧 For issues and feature requests, please open an issue on the GitHub repository.

![Screenshot 1](https://github.com/ocean-master0/youtube-slide-extractor/blob/main/screenshots/Screenshot%202025-04-19%20203213.png?raw=true)

![Screenshot 2](https://github.com/ocean-master0/youtube-slide-extractor/blob/main/screenshots/Screenshot%202025-04-19%20203658.png?raw=true)

