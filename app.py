from flask import Flask, render_template, request
import os

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    file = request.files['file']
    file.save(os.path.join("uploads", file.filename))
    return f'업로드 완료: {file.filename}'

if __name__ == '__main__':
    app.run(debug=True)
