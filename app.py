from flask import Flask, render_template, request, send_from_directory
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
    filename = file.filename
    filepath = os.path.join("uploads", filename)
    file.save(filepath)

    # 텍스트 추출
    text = extract_text_from_pdf(filepath)

    # 텍스트 파일로 저장
    text_filename = filename.rsplit('.', 1)[0] + '.txt'
    text_path = os.path.join("uploads", text_filename)
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text)

    return render_template('result.html',
                           filename=filename,
                           extracted_text=text,
                           text_file=text_filename)

@app.route('/download/<filename>')
def download_text(filename):
    return send_from_directory('uploads', filename, as_attachment=True)


def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page_num, page in enumerate(doc):
        page_text = page.get_text().strip()
        text += f"\n--- Page {page_num + 1} ---\n"
        text += page_text if page_text else "[비어 있음]\n"
    return text


if __name__ == '__main__':
    app.run(debug=True)
