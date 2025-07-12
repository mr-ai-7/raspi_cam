# 📷 Raspberry Pi Camera Web Interface

This project provides a **Flask-based web interface** for controlling the Raspberry Pi Camera (using the Picamera2 library) with features like:

- 🔴 **Live Video Streaming**
- 📸 **Photo Capture**
- 🎥 **Video Recording**
- 🖼 **Gallery for Photos**
- 🎞 **Video Management (Download/Delete)**

<br>

## 🌐 Live Demo (Screen Recording)

🎥 **[Watch the Demo Video](https://your-video-link.com)**  
*(Replace with your actual video link, e.g., YouTube or Google Drive)*

<br>

## 🛠 Features

| Feature         | Description |
|----------------|-------------|
| Live View       | Real-time camera feed via MJPEG stream |
| Start/Stop Recording | Capture high-quality videos and convert them to MP4 |
| Capture Photo   | Take and save still images asynchronously |
| Media Gallery   | View, download, or delete saved photos and videos |

<br>

## 📸 Screenshots

### 🔴 Live Camera Stream
<img src="screenshots/live_stream.png" width="600">

### 🖼 Photo Gallery
<img src="screenshots/photo_gallery.png" width="600">

### 🎞 Video Gallery
<img src="screenshots/video_gallery.png" width="600">

> Make sure you create a `screenshots/` directory and place real screenshots with the same names, or update the filenames accordingly.

<br>

## 🚀 Getting Started

### 🔧 Prerequisites

- Raspberry Pi 5 or similar (64-bit OS)
- PiCamera2 installed
- FFmpeg installed (`sudo apt install ffmpeg`)
- Python 3 & Flask installed
- OpenCV (`pip install opencv-python`)
- Threading and Picamera2 dependencies (`libcamera` pre-installed)

### 📦 Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/pi-camera-web-interface.git
cd pi-camera-web-interface

# Install Python dependencies
pip install flask opencv-python

# Run the app
python3 app.py
