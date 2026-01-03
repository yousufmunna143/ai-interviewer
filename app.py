from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
import fitz  # PDF processing
from groq import Groq
from fpdf import FPDF # creating pdf transcript
from datetime import datetime # handling timestamps
import io
import httpx # making http requests

# Initialize Flask application
app = Flask(__name__)

# Configuration settings
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Directory for temporary file uploads
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size: 16MB
ALLOWED_EXTENSIONS = {'pdf'}  # Only allow PDF file uploads

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# In-memory session storage
# Note: In production, use proper session management like Flask-Session
session_data = {
    "resume_text": "",      # Extracted text from the resume
    "topic": "",           # Selected interview topic
    "groq_api_key": "",    # User's Groq API key
    "transcript": [],      # List of QA pairs during interview
    "scores": [],         # List of scores for each answer
    "start_time": None    # Interview start timestamp
}

@app.route('/')
def index():
    #render homepage
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    return render_template("index.html")

@app.route('/start', methods=["POST"])
def start():
    # validate uploaded resume and render interview page
    if 'resume' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['resume']
    topic = request.form.get('topic', '').strip()
    groq_key = request.form.get('groq_api', '').strip()

    # Validate all required fields
    if not file or not topic or not groq_key:
        return "All fields required", 400

    if file.filename == '':
        return "No file selected", 400

    if not allowed_file(file.filename):
        return "Invalid file type. Only PDF files are allowed.", 400

    try:
        # Save and process the resume
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract text from the PDF
        resume_text = extract_text_from_pdf(filepath)

        # Clean up the temporary file
        os.remove(filepath)

        # Initialize session data
        session_data.update({
            "resume_text": resume_text,
            "topic": topic,
            "groq_api_key": groq_key,
            "transcript": [],
            "scores": [],
            "start_time": datetime.utcnow().timestamp()
        })

        return redirect(url_for('interview'))
    except Exception as e:
        return f"Error processing file: {str(e)}", 500

@app.route('/interview')
def interview():
    """Render the main interview interface."""
    return render_template("interview.html")

@app.route('/first_question', methods=["GET"])
def first_question():
    """
    Generate the first interview question based on the resume content.
    Uses Groq API to analyze the resume and create a relevant question.
    """
    try:
        client = Groq(api_key=session_data["groq_api_key"])
        resume_text = session_data.get("resume_text", "")
        prompt = f"Based on this resume, ask a relevant first interview question:\n\n{resume_text}"

        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are a professional software engineer conducting a realistic mock interview. Keep the tone natural and challenging. Ask interview questions one at a time."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            top_p=1,
            stream=False
        )

        question = completion.choices[0].message.content
        session_data['transcript'].append(("AI", question))
        return jsonify({"response": question})

    except Exception as e:
        print(f"Error in first_question: {str(e)}")  # Debug logging
        return jsonify({"response": f"Error generating first question: {str(e)}"}), 500

@app.route('/ask', methods=["POST"])
def ask():
    """
    Handle user responses and generate follow-up questions.
    1. Record user's answer
    2. Generate AI response based on the topic and context
    3. Update transcript
    """
    data = request.json
    user_message = data.get("message")

    session_data["transcript"].append(("User", user_message))

    try:
        client = Groq(api_key=session_data["groq_api_key"])
        topic = session_data["topic"]

        prompt = f"You are an interviewer. Ask or respond about {topic} based on this:\n\n{user_message}"

        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are continuing a realistic technical interview. Ask thoughtful follow-up questions or respond as an interviewer would in a one-on-one interview."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            top_p=1,
            stream=False
        )

        reply = completion.choices[0].message.content
        session_data["transcript"].append(("AI", reply))
        return jsonify({"response": reply})

    except Exception as e:
        print(f"Error in ask: {str(e)}")  # Debug logging
        return jsonify({"response": f"AI error: {str(e)}"}), 500

@app.route('/rate', methods=["POST"])
def rate():
    """
    Rate the user's answer and provide feedback.
    Returns a score (1-5) and explanation for the rating.
    """
    data = request.json
    user_response = data.get("message")

    try:
        client = Groq(api_key=session_data["groq_api_key"])
        prompt = f"Rate this interview answer from 1 to 5 and explain why:\n\n{user_response}"

        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            top_p=1,
            stream=False
        )

        reason = completion.choices[0].message.content
        score = extract_score(reason)
        session_data["scores"].append(score)

        return jsonify({"score": score, "reason": reason})

    except Exception as e:
        print(f"Error in rate: {str(e)}")  # Debug logging
        return jsonify({"score": 0, "reason": f"Scoring error: {str(e)}"}), 500

@app.route('/finish')
def finish():
    """
    Complete the interview and show results.
    Calculates average score and displays final feedback.
    """
    scores = session_data["scores"]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0
    return render_template("result.html", score=avg_score)

@app.route('/download_transcript')
def download_transcript():
    """
    Generate and download a PDF transcript of the interview.
    Includes all questions, answers, and timestamps.
    """
    if not session_data.get("transcript"):
        return "No transcript available", 400

    try:
        # Create PDF document
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Interview Transcript", ln=True, align='C')
        pdf.ln(10)

        # Add each QA pair to the PDF
        for role, text in session_data["transcript"]:
            pdf.multi_cell(0, 10, f"{role}: {text}")
            pdf.ln(1)

        # Generate PDF in memory
        pdf_output = io.BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        pdf_output = io.BytesIO(pdf_bytes)
        pdf_output.seek(0)

        return send_file(
            pdf_output,
            as_attachment=True,
            download_name=f"interview_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"Error generating transcript: {str(e)}", 500

def extract_text_from_pdf(filepath):
    """
    Extract text content from a PDF file.
    
    Args:
        filepath (str): Path to the PDF file
    
    Returns:
        str: Extracted text content
    
    Raises:
        Exception: If text extraction fails
    """
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_score(text):
    """
    Extract a numerical score (1-5) from the AI's rating response.
    
    Args:
        text (str): AI's rating response text
    
    Returns:
        int: Extracted score (defaults to 3 if no score found)
    """
    try:
        for i in range(5, 0, -1):
            if str(i) in text:
                return i
        return 3  # Default score if no number found
    except:
        return 3  # Safe default

# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)
