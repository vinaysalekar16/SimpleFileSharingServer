from flask import Flask, jsonify, request, render_template, redirect, url_for, send_from_directory, flash
import os
import shutil
import socket
from waitress import serve

app = Flask(__name__)

# secret key
app.secret_key = 'fn9VIE8V-fvFlXI90eB-kg'

# Path to the folder to serve
base_folder = os.path.join(os.path.dirname(__file__), 'ServerFolderToUse')  # path to your folder
deleted_folder = os.path.join(os.path.dirname(__file__), 'DeletedFiles')  # path for deleted files folder
images_folder = os.path.join(base_folder, 'images')
music_folder = os.path.join(base_folder, 'music')
videos_folder = os.path.join(base_folder, 'videos')

# Credentials for Admin
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'vinay@123'

def check_admin_auth(username, password):
    """Check if username and password are valid for the admin."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

@app.route('/')
def index():
    ip_address = get_server_ip()
    return render_template('index.html', ip_address=ip_address)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_admin_auth(username, password):
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('admin'))
    return render_template('admin.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    all_files = os.listdir(base_folder)
    image_files = os.listdir(images_folder)
    audio_files = os.listdir(music_folder)
    video_files = os.listdir(videos_folder)
    deleted_files = os.listdir(deleted_folder)
    return render_template('admin_dashboard.html', all_files=all_files, deleted_files=deleted_files, image_files=image_files, audio_files=audio_files, video_files=video_files)

@app.route('/user')
def user():
    ip_address = get_server_ip()
    return render_template('user_login.html', ip_address=ip_address)

@app.route('/welcome')
def welcome():
    ip_address = get_server_ip()
    return render_template('welcome.html', ip_address=ip_address)

@app.route('/user_images')
def user_images():
    images_files = os.listdir(images_folder)
    return render_template('user_images.html', images_files=images_files)

@app.route('/user_music')
def user_music():
    music_files = os.listdir(music_folder)
    return render_template('user_music.html', music_files=music_files)

@app.route('/user_videos')
def user_videos():
    videos_files = os.listdir(videos_folder)
    return render_template('user_videos.html', videos_files=videos_files)

@app.route('/upload_page')
def upload_page():
    return render_template('upload_page.html')

@app.route('/list_files')
def list_files():
    files = os.listdir(base_folder)
    return jsonify(files)

@app.route('/add_file', methods=['POST'])
def add_file():
    data = request.get_json()
    file_name = data['file_name']
    file_content = data['file_content']
    file_path = os.path.join(base_folder, file_name)
    with open(file_path, 'w') as f:
        f.write(file_content)
    return 'File added successfully'

# Function to move file to DeletedFiles folder
@app.route('/delete_file', methods=['POST'])
def delete_file():
    data = request.get_json()
    file_name = data['file_name']
    file_path = os.path.join(base_folder, file_name)
    
    if os.path.exists(file_path):
        move_file_to_deleted(file_path)
        return 'File moved to DeletedFiles folder'
    else:
        return 'File not found'

def move_file_to_deleted(file_path):
    file_name = os.path.basename(file_path)
    deleted_file_path = os.path.join(deleted_folder, file_name)
    os.rename(file_path, deleted_file_path)


if not os.path.exists(deleted_folder):
    os.makedirs(deleted_folder)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    file_path = os.path.join(base_folder, file.filename)
    file.save(file_path)
    return 'File uploaded successfully'

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(base_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(base_folder, filename, as_attachment=True)
    else:
       return 'File not found'

#--------------------------- For video streaming 
@app.route('/stream_video/<path:filename>')
def stream_video(filename):
    file_path = os.path.join(videos_folder, filename)
    if os.path.exists(file_path):
        return render_template('video_stream.html', filename=filename)
    else:
        return 'File not found'

@app.route('/stream_video_content/<path:filename>')
def stream_video_content(filename):
    file_path = os.path.join(videos_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(videos_folder, filename, as_attachment=False)
    else:
        return 'File not found'
#--------------------------- For Img streaming
@app.route('/stream_image/<path:filename>')
def stream_image(filename):
    file_path = os.path.join(images_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(images_folder, filename, as_attachment=False)
    else:
        return 'File not found'
    
@app.route('/download_image/<path:filename>')
def download_image(filename):
    file_path = os.path.join(images_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(images_folder, filename, as_attachment=True)
    else:
        return 'File not found'

#--------------------------- For Audio streaming
@app.route('/stream_audio/<path:filename>')
def stream_audio(filename):
    file_path = os.path.join(music_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(music_folder, filename, as_attachment=False)
    else:
        return 'File not found'

@app.route('/download_audio/<path:filename>')
def download_audio(filename):
    file_path = os.path.join(music_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(music_folder, filename, as_attachment=True)
    else:
        return 'File not found'

#------------------------------ Function to get the server's IP address
def get_server_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

if __name__ == '__main__':
    ip_address = get_server_ip()
    print(f"Server running at: http://{ip_address}:8080")
    serve(app, host='0.0.0.0', port=8080)
