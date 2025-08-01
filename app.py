import os
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2
import time
import base64 # Added for handling audio data
import google.api_core.exceptions
from flask import Flask, request, render_template, send_from_directory
from sarvamai import SarvamAI

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Get API keys from environment variables
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
SARVAM_API_KEY = os.getenv('SARVAM_API_KEY')

# Check if API keys are available
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
if not SARVAM_API_KEY:
    raise ValueError("SARVAM_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)

# --- Flask App Initialization ---
app = Flask(__name__)

# Create directories if they don't exist
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'static/audio'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

# --- Helper Functions ---

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def summarize_with_gemini(text):
    """Uses Gemini to summarize text in English with a retry mechanism."""
    model = genai.GenerativeModel('gemini-2.5-pro')
    prompt = f"""
    Summarize the following document in only 1 paragraph in less than 1200 characters strictly.
    Provide ONLY the English summary. Do not add any other introductory text or formatting.
    
    Document:
    {text}
    """
    
    retries = 5
    delay = 2
    for i in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except google.api_core.exceptions.ResourceExhausted as e:
            print(f"Gemini API rate limit exceeded. Retrying in {delay} seconds... (Attempt {i+1}/{retries})")
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            print(f"An unexpected error occurred with the Gemini API: {e}")
            return None
            
    print("Gemini API call failed after multiple retries due to rate limiting.")
    return None

def translate_with_sarvam(text, language_code):
    """Translates text using the Sarvam AI SDK, based on the latest user-provided docs."""
    try:
        # Initialize client with api_subscription_key as per the new docs
        client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
        response = client.text.translate(
            input=text,
            source_language_code="auto", # Use 'auto' as per the new docs
            target_language_code=f"{language_code}-IN"
        )
        if hasattr(response, 'translated_text'):
            return response.translated_text
        return str(response)
    except Exception as e:
        print(f"Error calling Sarvam Translate API: {e}")
        return None

def generate_audio_with_sarvam(text, language_code, audio_filename):
    """Generates audio using the .convert method and handles Base64 response."""
    try:
        # Initialize client with api_subscription_key as per the new docs
        client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
        
        # Use the .convert method as specified in the new docs
        audio_response = client.text_to_speech.convert(
            text=text,
            target_language_code=f"{language_code}-IN"
        )

        # Process the Base64 response as shown in user's example
        if hasattr(audio_response, 'audios') and audio_response.audios:
            combined_audio = "".join(audio_response.audios)
            decoded_audio = base64.b64decode(combined_audio)

            audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
            with open(audio_path, "wb") as f:
                f.write(decoded_audio)
            return audio_filename
        else:
            print("Sarvam TTS API did not return valid audio data.")
            return None
    except Exception as e:
        print(f"Error calling Sarvam AI SDK for TTS: {e}")
        return None

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "No file part in the request.", 400
        file = request.files['pdf_file']
        if file.filename == '':
            return "No file selected.", 400
        
        language_code = request.form.get('language_code', 'hi')

        if file and file.filename.endswith('.pdf'):
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(pdf_path)

            document_text = extract_text_from_pdf(pdf_path)
            if not document_text:
                return "Could not extract text from the PDF. It might be empty or scanned.", 400

            english_summary = summarize_with_gemini(document_text)
            if not english_summary:
                return "Error: Could not generate summary from Gemini. The API may be temporarily unavailable or rate limited.", 500

            translated_summary = translate_with_sarvam(english_summary, language_code)
            if not translated_summary:
                return "Error: Could not translate summary using Sarvam AI.", 500
            
            # The output from Sarvam is often WAV, but we can save as MP3 for better web compatibility
            audio_filename = f"summary_{language_code}.mp3" 
            audio_file = generate_audio_with_sarvam(translated_summary, language_code, audio_filename)
            
            os.remove(pdf_path)

            if audio_file:
                 return render_template('result.html', summary=translated_summary, audio_url=audio_file)
            else:
                return "Could not generate audio file. Check your server logs for errors from the Sarvam AI API.", 500

    return render_template('index.html')

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
