from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from utils.agent import StrictMedicalAnalyzer
from gtts import gTTS

app = Flask(__name__, template_folder='templates', static_folder='static')
print('Flask template_folder:', app.template_folder)
print('Flask static_folder:', app.static_folder)

# Configuration
UPLOAD_FOLDER = 'uploads'
STATIC_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'txt', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image_file(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}


def speak_text(text):
    """
    Convert text to speech using gTTS and save as MP3 file.
    Args:
        text (str): The text to convert to speech
    Returns:
        str: Path to the generated audio file, or None if error occurs
    """
    try:
        audio_path = os.path.join(STATIC_FOLDER, 'output.mp3')
        # Create gTTS object with the text
        tts = gTTS(text=text, lang='en', slow=False)
        # Save the audio file
        tts.save(audio_path)
        print(f"Audio file saved successfully at: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"Error generating speech: {str(e)}")
        return None


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
                    
                    # Generate text-to-speech for the diagnosis
                    speak_text(diagnosis)
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
            
            # Helper function to safely get values and show "Not mentioned" for empty data
            def get_value(key, default='Not mentioned'):
                value = result.get(key, '')
                if value is None or (isinstance(value, str) and not value.strip()):
                    return default
                if isinstance(value, str):
                    return value.strip() if value.strip() else default
                return value if value else default
            
            def get_list(key, default='Not mentioned'):
                items = result.get(key, [])
                if not items or (isinstance(items, list) and len(items) == 0):
                    return default
                # Filter out None, empty strings, and whitespace-only items
                filtered = [str(item).strip() for item in items if item and str(item).strip()]
                # Return default if no valid items remain after filtering
                return ', '.join(filtered) if filtered else default
            
            # Format medicines with proper handling
            medicines_formatted = []
            medicines_list = result.get('medicines', [])
            
            if medicines_list:
                for med in medicines_list:
                    if isinstance(med, dict):
                        name = med.get('name', '').strip() or 'Unknown'
                        dosage = med.get('dosage', '').strip() or 'Not specified'
                        duration = med.get('duration', '').strip() or 'Not specified'
                        medicines_formatted.append(f"{name} - {dosage} for {duration}")
                    elif isinstance(med, str) and med.strip():
                        medicines_formatted.append(med.strip())
            
            medicines_text = '; '.join(medicines_formatted) if medicines_formatted else 'Not mentioned'
            
            # Format all sections with consistent "Not mentioned" display
            formatted_result = f"""
Name: {get_value('name')}

Age: {get_value('age')}

Gender: {get_value('gender')}

Diagnosis: {get_value('diagnosis')}

Symptoms: {get_list('symptoms')}

Medicines: {medicines_text}

Report Advice: {get_list('report_advice')}

AI Advice: {get_list('ai_advice')}

Warnings: {get_list('warnings')}

Summary: {get_value('summary')}
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