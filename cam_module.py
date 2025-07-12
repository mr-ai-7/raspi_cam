import os
import time
from flask import Flask, Response, render_template_string, redirect, url_for, send_file, request
from threading import Thread
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
import cv2

app = Flask(__name__)

# Directories
video_dir = os.path.expanduser("~/videos")
photo_dir = os.path.expanduser("~/pictures")
os.makedirs(video_dir, exist_ok=True)
os.makedirs(photo_dir, exist_ok=True)

# Camera setup
picam2 = Picamera2()
picam2.start_preview()
picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720)}))
picam2.start()

recording = False
video_filename = ""

@app.route('/')
def index():
    return render_template_string('''
        <h2>📷 Pi Camera Live Stream</h2>
        <img src="{{ url_for('video_feed') }}" style="width: 640px; border: 2px solid #000;"><br><br>

        <form action="/start_recording" method="get" style="display: inline;">
            <button style="margin: 5px;">🔴 Start Recording</button>
        </form>
        <form action="/stop_recording" method="get" style="display: inline;">
            <button style="margin: 5px;">⏹ Stop Recording</button>
        </form>
        <form action="/capture_photo" method="get" style="display: inline;">
            <button style="margin: 5px;">📸 Capture Photo</button>
        </form>
        <form action="/photos" method="get" style="display: inline;">
            <button style="margin: 5px;">🖼 View Photos</button>
        </form>
        <form action="/videos" method="get" style="display: inline;">
            <button style="margin: 5px;">🎞 View Videos</button>
        </form>
    ''')

def generate_frames():
    while True:
        frame = picam2.capture_array("main")
        _, buffer = cv2.imencode('.jpg', frame)
        jpg = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/live')
def live_view():
    return render_template_string('''
        <h2>📺 Live Camera Stream</h2>
        <img src="{{ url_for('video_feed') }}" style="width: 100%; max-width: 800px; border: 3px solid #333;">
        <br><br>
        <a href="{{ url_for('index') }}"><button>🔙 Back to Home</button></a>
    ''')

@app.route('/start_recording')
def start_recording():
    global recording, video_filename
    if not recording:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        h264_path = os.path.join(video_dir, f"video_{timestamp}.h264")
        encoder = H264Encoder()
        output = FileOutput(h264_path)
        encoder.output = output
        picam2.start_recording(encoder, output)
        video_filename = h264_path
        recording = True
    return redirect(url_for('index'))

@app.route('/stop_recording')
def stop_recording():
    global recording, video_filename
    if recording:
        picam2.stop_recording()
        recording = False
        mp4_file = video_filename.replace(".h264", ".mp4")
        os.system(f"ffmpeg -y -framerate 30 -i {video_filename} -c copy {mp4_file}")
        os.remove(video_filename)
        video_filename = mp4_file
    return redirect(url_for('index'))

def save_photo_async(filename):
    try:
        frame = picam2.capture_array("main")
        cv2.imwrite(filename, frame)
        print(f"[✔] Photo saved at {filename}")
    except Exception as e:
        print(f"[❌] Failed to save photo: {e}")

@app.route('/capture_photo')
def capture_photo():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    photo_path = os.path.join(photo_dir, f"photo_{timestamp}.jpg")
    print(f"[INFO] Launching background capture at {timestamp}")
    Thread(target=save_photo_async, args=(photo_path,)).start()
    return redirect(url_for('photos'))

@app.route('/photos')
def photos():
    files = os.listdir(photo_dir)
    jpg_files = sorted([f for f in files if f.endswith('.jpg')])
    return render_template_string('''
        <h2>🖼 Captured Photos</h2>
        <div style="display: flex; flex-wrap: wrap;">
            {% for file in files %}
                <div style="margin: 10px;">
                    <img src="{{ url_for('photo_file', filename=file) }}" style="width: 200px; border: 1px solid #ccc;"><br>
                    <p style="text-align: center;">{{ file }}</p>
                    <a href="{{ url_for('delete_photo', filename=file) }}"><button style="color: red;">🗑 Delete</button></a>
                </div>
            {% endfor %}
        </div>
        <a href="{{ url_for('index') }}"><button>🔙 Back to Home</button></a>
    ''', files=jpg_files)

@app.route('/photo/<filename>')
def photo_file(filename):
    file_path = os.path.join(photo_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/jpeg')
    else:
        return "<h3>Photo not found.</h3>"

@app.route('/delete_photo/<filename>')
def delete_photo(filename):
    file_path = os.path.join(photo_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('photos'))

@app.route('/videos')
def videos():
    files = os.listdir(video_dir)
    mp4_files = sorted([f for f in files if f.endswith('.mp4')])
    return render_template_string('''
        <h2>🎞 Recorded Videos</h2>
        <ul style="list-style: none; padding: 0;">
        {% for file in files %}
            <li style="margin-bottom: 10px;">
                <strong>{{ file }}</strong>
                <a href="{{ url_for('download_file', filename=file) }}"><button>⬇️ Download</button></a>
                <a href="{{ url_for('delete_file', filename=file) }}"><button style="color: red;">🗑 Delete</button></a>
            </li>
        {% endfor %}
        </ul>
        <a href="{{ url_for('index') }}"><button>🔙 Back to Home</button></a>
    ''', files=mp4_files)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(video_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='video/mp4', as_attachment=True)
    else:
        return "<h3>File not found.</h3>"

@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(video_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('videos'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
