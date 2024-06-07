from flask import Flask, jsonify, request, render_template, redirect, url_for, send_from_directory, flash
import os
import shutil

app = Flask(__name__)

#secret key
app.secret_key = 'fn9VIE8V-fvFlXI90eB-kg'


# Path to the folder to serve
base_folder = os.path.join(os.path.dirname(__file__), 'ServerFolderToUse') # path to your folder
deleted_folder = os.path.join(os.path.dirname(__file__), 'DeletedFiles') # path for deleted files folder

# Dummy credentials for demonstration purposes
USERNAME = 'admin'
PASSWORD = 'vinay@123'

def check_auth(username, password):
    """Check if username and password are valid."""
    return username == USERNAME and password == PASSWORD

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_auth(username, password):
            return redirect(url_for('welcome'))
        else:
            flash('Invalid username or password')  # Store custom error message in session
            return redirect(url_for('login'))  # Redirect back to login page
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    ip_address = get_server_ip()
    files = os.listdir(base_folder)  # Get a list of files in the base folder
    return render_template('welcome.html', ip_address=ip_address, files=files)

@app.route('/list_files')
def list_files():
    files = os.listdir(base_folder)
    return jsonify(files)

@app.route('/add_file', methods=['POST'])
def add_file():
    data = request.get_json()
    file_name = data['file_name']
    file_content = data['file_content']
    with open(os.path.join(base_folder, file_name), 'w') as file:
        file.write(file_content)
    return 'File added successfully'

@app.route('/delete_file', methods=['POST'])
def delete_file():
    data = request.get_json()
    file_name = data['file_name']
    # Construct paths for the original file and the new location
    original_path = os.path.join(base_folder, file_name)
    deleted_path = os.path.join(deleted_folder, file_name)
    # Move the file to the "DeletedFiles" folder
    shutil.move(original_path, deleted_path)
    return 'File deleted successfully'

if not os.path.exists(deleted_folder):
    os.makedirs(deleted_folder)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return 'No selected file', 400
    uploaded_file.save(os.path.join(base_folder, uploaded_file.filename))
    return 'File uploaded successfully', 200

# Function to get the server's IP address
def get_server_ip():
    return request.host.split(":")[0]  # Get the IP address from the request host

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(base_folder, filename)

# You can add more routes for other file operations like moving, copying, etc.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

