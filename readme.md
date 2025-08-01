# PDF Summarizer and Voice Translator

A web application that summarizes PDF documents, translates the summary into Indian languages, and converts it into audio—all powered by cutting-edge AI.

## Overview

**PDF Summarizer and Voice Translator** is a web-based tool designed to make document analysis fast and accessible. Upload a text-based PDF, and receive a concise summary in English, a translation in your chosen Indian language, and a natural-sounding voice-over.

### Key Features

- **PDF Text Extraction**  
  Upload any text-based PDF to extract its full content.

- **AI-Powered Summarization**  
  Uses **Google Gemini 1.5 Flash** to generate short, accurate English summaries.

- **Multi-Language Translation**  
  Translates the summary into major Indian languages using **Sarvam AI**.

- **Voice Synthesis**  
  Converts the translated summary into audio using Sarvam AI’s **Text-to-Speech (TTS)** engine.

- **Clean Web Interface**  
  Upload PDFs and access summaries, translations, and audio files directly in your browser.

- **Free Hosting Guide**  
  Comes with a deployment guide for **Render** (free hosting platform).


## Tech Stack

### Backend
- Python 3.10.12
- Flask
- PyPDF2
- google-generativeai
- sarvamai
- requests

### Frontend
- HTML5
- Tailwind CSS

### AI Services
- **Google Gemini API** – Summarization  
- **Sarvam AI API** – Translation & TTS

### Deployment
- Gunicorn
- Render

Local Setup and Installation

Follow these steps to run the project on your local machine.

1. Clone the Repository

git clone https://github.com/sprnjt/pdf_translator.git

cd pdf_translator


2. Create and Activate a Virtual Environment

For macOS/Linux:

python3 -m venv venv

source venv/bin/activate


For Windows:

python -m venv venv

.\venv\Scripts\activate


3. Install Dependencies

pip install -r requirements.txt


4. Configure Environment Variables

You need to provide your API keys. It is recommended to set them as environment variables.

For macOS/Linux:

export GEMINI_API_KEY="YOUR_GOOGLE_API_KEY_HERE"

export SARVAM_API_KEY="YOUR_SARVAM_API_KEY_HERE"


For Windows Command Prompt:

set GEMINI_API_KEY="YOUR_GOOGLE_API_KEY_HERE"

set SARVAM_API_KEY="YOUR_SARVAM_API_KEY_HERE"


Note: Alternatively, you can temporarily hardcode the keys in app.py for local testing, but do not commit them to version control.

5. Run the Application

flask run


The application will be available at http://127.0.0.1:5000.

##Contact

For any issue, feel free to connect with Suparnojit on X/Twitter: suparnojit26