# Smart Medical Report Analyzer

A Flask-based web application that uses AI agents powered by LangChain and Groq API to analyze medical reports and provide consolidated diagnoses.

## Features

- Upload medical reports in .txt, .jpg, .jpeg, .png, .bmp, or .tiff format
- Multi-agent analysis using specialized AI agents:
  - Cardiologist: Focuses on cardiac issues
  - Psychologist: Focuses on mental health and anxiety
  - Pulmonologist: Focuses on respiratory signs
- Consolidated diagnosis from a multi-disciplinary team
- Concurrent processing for faster results

## Installation

1. Clone or download the project files
2. Install Tesseract OCR engine (required for image processing):
   - Download from: https://github.com/UB-Mannheim/tesseract/releases
   - Install the Windows setup executable
   - Ensure it's added to your system PATH or note the installation path
3. Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Flask application:

```bash
python app.py
```

2. Open your web browser and navigate to `http://127.0.0.1:5000`

3. Upload a medical report in .txt, .jpg, .jpeg, .png, .bmp, or .tiff format

4. View the comprehensive analysis and consolidated diagnosis

## Project Structure

```
hakonit/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html         # Upload form
│   └── result.html        # Results display
├── utils/
│   ├── __init__.py
│   ├── agent.py           # AI agent classes
│   └── main.py            # Command-line version
├── uploads/               # Temporary upload directory (created automatically)
└── medical_report.txt     # Sample medical report
```

## Dependencies

- Flask: Web framework
- LangChain Core: For prompt templates
- LangChain Groq: For Groq API integration

## Security Notes

- The application accepts only .txt files
- Maximum file size is limited to 16MB
- Uploaded files are processed and immediately deleted after analysis
- Uses secure filename handling

## API Key

The application uses a Groq API key hardcoded in `utils/agent.py`. In a production environment, consider using environment variables for API keys.

## Sample Usage

Upload a medical report text file containing patient symptoms, test results, and medical history. The AI agents will analyze the report from their respective specialties and provide a comprehensive diagnosis.