# website_app.py
from flask import Flask, render_template, request, send_from_directory # type: ignore
import mysql.connector # type: ignore
import face_recognition # type: ignore
import pickle
from pathlib import Path

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",  # Replace with your DB host
    "user": "your_username",  # Replace with your DB username
    "password": "your_password",  # Replace with your DB password
    "database": "event_photos"
}

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_face_encodings(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    return encodings[0] if encodings else None

def find_matching_photos(encoding):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT photo_id, url, face_encodings FROM photos WHERE face_encodings IS NOT NULL")
    
    matches = []
    for photo_id, url, encodings_blob in cursor.fetchall():
        stored_encodings = pickle.loads(encodings_blob)
        for stored_encoding in stored_encodings:
            if face_recognition.compare_faces([stored_encoding], encoding, tolerance=0.6)[0]:
                matches.append(url)
                break
    conn.close()
    return matches

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    if 'photo' not in request.files:
        return "No file uploaded", 400
    file = request.files['photo']
    if file.filename == '':
        return "No file selected", 400
    
    file_path = app.config['UPLOAD_FOLDER'] / file.filename
    file.save(file_path)
    
    encoding = get_face_encodings(file_path)
    if not encoding:
        file_path.unlink()
        return render_template('search_results.html', photos=[], error="No face detected in uploaded photo")
    
    photos = find_matching_photos(encoding)
    file_path.unlink()  # Clean up
    return render_template('search_results.html', photos=photos)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)