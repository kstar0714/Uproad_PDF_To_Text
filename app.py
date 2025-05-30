from flask import Flask, render_template, request
import os
import fitz  # PyMuPDF

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    file = request.files['file']
    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)

    # PDF에서 텍스트 추출
    text = extract_text_from_pdf(filepath)

    return render_template('result.html', filename=file.filename, extracted_text=text)

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

if __name__ == '__main__':
    app.run(debug=True)
