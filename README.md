# AI Interview Assistant 🤖

An intelligent interview preparation tool that conducts personalized mock interviews based on your resume and chosen topic. The application uses Groq's LLM API to provide a realistic interview experience with real-time feedback and scoring.

## Features ✨

- **Resume-Based Questions**: Generates relevant interview questions based on your uploaded resume
- **Multiple Topics**: Supports various interview topics:
  - Data Structures & Algorithms (DSA)
  - Database Management (DBMS)
  - Object-Oriented Programming (OOP)
  - System Design
  - Web Development
  - Machine Learning

- **Interactive Interface**:
  - Real-time chat-like interface
  - Voice input/output support
  - Timer for interview duration
  - Live scoring and feedback
  - Progress tracking

- **Accessibility**:
  - Screen reader support
  - Keyboard navigation
  - ARIA labels and roles
  - Responsive design

- **Results & Analysis**:
  - Detailed performance scoring
  - Question-by-question feedback
  - Downloadable interview transcript
  - Performance insights

## Tech Stack 🛠

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: Groq API (LLaMA 4)
- **PDF Processing**: PyMuPDF
- **Document Generation**: FPDF

## Prerequisites 📋

- Python 3.9 or higher
- A Groq API key (get it from [Groq Console](https://console.groq.com/home))
- Specifically designed for chrome browser

## Installation 🚀

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-interview-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage 💡

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. On the homepage:
   - Upload your resume (PDF format, max 16MB)
   - Select an interview topic
   - Enter your Groq API key
   - Click "Start Interview"

4. During the interview:
   - Answer questions naturally
   - Use voice input if desired (click 🎤)
   - Watch your remaining time
   - View real-time feedback and scores
   - End interview when ready

5. After the interview:
   - Review your overall score
   - Read performance feedback
   - Download the interview transcript
   - Start a new interview if desired

## File Structure 📁

```
ai-interview-app/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/
│   ├── style.css      # Application styling
│   ├── script.js      # Client-side scripts
│   └── uploads/       # Temporary file uploads
├── templates/
│   ├── index.html     # Landing page
│   ├── interview.html # Interview interface
│   └── result.html    # Results page
└── README.md          # Documentation
```

## Features in Detail 🔍

### Resume Analysis
- Extracts text from uploaded PDF resumes
- Analyzes content to generate relevant questions
- Maintains context throughout the interview

### Interview Flow
1. **Initial Question**: Generated based on resume content
2. **Follow-up Questions**: Based on your answers and chosen topic
3. **Scoring**: Each answer is rated on a scale of 1-5
4. **Feedback**: Detailed explanation for each score
5. **Timer**: 10-minute interview duration

### Voice Features
- Speech-to-text for answers
- Text-to-speech for questions
- Real-time voice input toggle

### Security
- Secure file handling
- API key protection
- Input sanitization
- File size limits
- Temporary file cleanup

## Error Handling 🚨

The application includes comprehensive error handling for:
- File upload issues
- API connection problems
- Voice recognition errors
- Network interruptions
- Invalid inputs

## Best Practices 💪

1. **Prepare Your Resume**:
   - Use a clear, well-formatted PDF
   - Ensure text is extractable
   - Keep file size under 16MB

2. **During Interview**:
   - Use a quiet environment for voice features
   - Give detailed, structured answers
   - Watch the timer
   - Complete your thoughts before the time ends

3. **For Best Results**:
   - Use Chrome browser
   - Ensure stable internet connection
   - Test microphone before starting
   - Review feedback between sessions

## Contributing 🤝

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License 📄

[MIT License](LICENSE)

## Support 🆘

For support, please open an issue in the repository or contact the maintainers.
