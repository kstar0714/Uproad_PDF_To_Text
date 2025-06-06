from flask import Flask, render_template, request, send_from_directory
from pdf2image import convert_from_path
from PIL import Image
import requests
import base64
import os

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

CLOVA_OCR_SECRET = os.getenv("CLOVA_OCR_SECRET")  # Render에 설정한 값

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    file = request.files['file']
    filename = file.filename
    filepath = os.path.join("uploads", filename)
    file.save(filepath)

    # PDF → 이미지 → CLOVA OCR
    text = extract_text_via_clova(filepath)

    # 텍스트 저장
    text_filename = filename.rsplit('.', 1)[0] + '_ocr.txt'
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

def extract_text_via_clova(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)
    full_text = ""

    for i, image in enumerate(images):
        img_path = f"uploads/page_{i}.jpg"
        image.save(img_path, 'JPEG')

        with open(img_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()

        headers = {
            "X-OCR-SECRET": CLOVA_OCR_SECRET,
            "Content-Type": "application/json"
        }

        payload = {
            "version": "v1",
            "requestId": "ocr-request",
            "timestamp": 0,
            "images": [{
                "format": "jpg",
                "name": f"page_{i}",
                "data": image_data
            }]
        }

        res = requests.post(
            "https://clovaocr-api-kr.ncloud.com/external/v1/42531/f410ff7be7e71427f17d4e592c5b6c85f805fe333b409f969fba2b367d0dfe8b",
            headers=headers,
            json=payload
        )

        print("📦 OCR 응답 상태코드:", res.status_code)

        try:
            result = res.json()
            print("📜 OCR 응답 본문:", result)
        except Exception as e:
            print("❌ JSON 파싱 실패:", e)
            return "[OCR 응답 JSON 파싱 오류]"

        if 'images' not in result:
            return f"[OCR 실패] CLOVA 응답 오류:\n{result}"

        for field in result['images'][0].get('fields', []):
            full_text += field['inferText'] + '\n'

    return full_text
