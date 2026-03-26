from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.agent import Cardiologist, Psychologist, Pulmonologist, MultiDisciplinaryTeam

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
        # Initialize the Specialized Agents
        agents = {
            "Cardiologist": Cardiologist(medical_report),
            "Psychologist": Psychologist(medical_report),
            "Pulmonologist": Pulmonologist(medical_report)
        }

        # Helper function to get response from an agent
        def get_response(name, agent):
            try:
                response = agent.run()
                return name, response
            except Exception as e:
                return name, f"Error from {name}: {str(e)}"

        # Run agents concurrently to save time
        responses = {}
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(get_response, name, agent) for name, agent in agents.items()]
            for future in as_completed(futures):
                name, response = future.result()
                responses[name] = response

        # Pass individual reports to the Multi-Disciplinary Team for final review
        team_agent = MultiDisciplinaryTeam(
            cardio_report=responses.get("Cardiologist"),
            psych_report=responses.get("Psychologist"),
            pulm_report=responses.get("Pulmonologist")
        )

        final_diagnosis = team_agent.run()
        return final_diagnosis
    except Exception as e:
        return f"Error in analysis: {str(e)}"

@app.route('/test')
def test():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)