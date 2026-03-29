from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from utils.agent import StrictMedicalAnalyzer

app = Flask(__name__, template_folder='templates', static_folder='static')
print('Flask template_folder:', app.template_folder)
print('Flask static_folder:', app.static_folder)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image_file(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}


def extract_text_from_image(path):
    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError('Pillow is required for image OCR. Install with: pip install pillow pytesseract')

    try:
        import pytesseract
        # Set the tesseract command path
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    except ImportError:
        raise RuntimeError('pytesseract is required for image OCR. Install with: pip install pytesseract')

    image = Image.open(path)
    return pytesseract.image_to_string(image)


@app.route('/', methods=['GET', 'POST'])
def index():
    print("Index route called")
    print('Rendering index.html from', app.template_folder)
    if request.method == 'POST':
        print("POST request received")
        try:
            # Check if the post request has the file part
            if 'file' not in request.files:
                return "No file part", 400
            file = request.files['file']
            # If user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                return "No selected file", 400
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    if is_image_file(filename):
                        medical_report = extract_text_from_image(filepath)
                    else:
                        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                            medical_report = f.read()

                    print(f"Processing file: {filename}")
                    diagnosis = analyze_report(medical_report)
                finally:
                    if os.path.exists(filepath):
                        os.remove(filepath)

                return render_template('result.html', diagnosis=diagnosis)
            else:
                return "Invalid file type", 400
        except Exception as e:
            print(f"Error: {e}")
            return f"Error processing file: {str(e)}", 500
    return render_template('index.html')

def analyze_report(medical_report):
    try:
        import json
        analyzer = StrictMedicalAnalyzer(medical_report)
        response = analyzer.run()
        
        # Parse the JSON response
        try:
            result = json.loads(response)
            # Format the result for display
            medicines_formatted = []
            for med in result.get('medicines', []):
                if isinstance(med, dict):
                    name = med.get('name', 'Unknown')
                    dosage = med.get('dosage', 'Not specified')
                    duration = med.get('duration', 'Not specified')
                    medicines_formatted.append(f"{name} - {dosage} for {duration}")
                else:
                    medicines_formatted.append(str(med))
            
            formatted_result = f"""
Name: {result.get('name', 'Not mentioned')}

Age: {result.get('age', 'Not mentioned')}

Gender: {result.get('gender', 'Not mentioned')}

Diagnosis: {result.get('diagnosis', 'Not mentioned')}

Symptoms: {', '.join(result.get('symptoms', [])) or 'Not mentioned'}

Medicines: {'; '.join(medicines_formatted) or 'Not mentioned'}

Report Advice: {', '.join(result.get('report_advice', [])) or 'Not mentioned'}

AI Advice: {', '.join(result.get('ai_advice', [])) or 'Not mentioned'}

Warnings: {', '.join(result.get('warnings', [])) or 'Not mentioned'}

Summary: {result.get('summary', 'Not mentioned')}
"""
            
            return formatted_result
        except json.JSONDecodeError:
            return f"Error parsing response: {response}"
    except Exception as e:
        return f"Error in analysis: {str(e)}"

@app.route('/test')
def test():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)