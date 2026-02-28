import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openrouter import OpenRouterClient
from tie_loader import TIEBookLoader
from tie_rules import TIERuleEnforcer
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:5500", "http://localhost:8000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# FIXED: Correct path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_DIR = "C:/Users/brkra/OneDrive/Desktop/TIE/tie_books"
os.makedirs(BOOKS_DIR, exist_ok=True)  # Create directory if it doesn't exist

print(f"📁 Books directory: {BOOKS_DIR}")
print(f"📁 Directory exists: {os.path.exists(BOOKS_DIR)}")

# Initialize components
try:
    book_loader = TIEBookLoader(BOOKS_DIR)
    print(f"✅ Book loader initialized")
    print(f"📚 Books found: {len(book_loader.list_books())}")
except Exception as e:
    print(f"❌ Error initializing book loader: {e}")
    book_loader = None

rule_enforcer = TIERuleEnforcer()

try:
    openrouter_client = OpenRouterClient()
    print(f"✅ OpenRouter client initialized")
except Exception as e:
    print(f"❌ Error initializing OpenRouter: {e}")
    openrouter_client = None

@app.route('/')
def index():
    """Serve the main page"""
    books_info = {}
    if book_loader:
        books_info = book_loader.get_loaded_subjects()
    
    return jsonify({
        "status": "TIE AI Tutor API is running",
        "version": "1.0.0",
        "curriculum": "Tanzanian Secondary School Curriculum",
        "subjects_loaded": books_info,
        "books_directory": BOOKS_DIR,
        "directory_exists": os.path.exists(BOOKS_DIR),
        "total_books_loaded": len(book_loader.list_books()) if book_loader else 0
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        if not book_loader:
            return jsonify({
                "error": "Book loader not initialized",
                "answer": "System is initializing. Please try again in a moment.",
                "source": {
                    "book": "System",
                    "subject": "Initialization",
                    "topic": "Setup",
                    "page": "N/A",
                    "form": "N/A"
                }
            }), 503
        
        data = request.json
        question = data.get('question', '')
        subject = data.get('subject', 'all')
        form_level = data.get('form_level', 'form1')
        language = data.get('language', 'en')
        
        if not question:
            return jsonify({
                "error": "No question provided",
                "answer": "Please ask a question about Tanzanian curriculum.",
                "source": {
                    "book": "System",
                    "subject": "General",
                    "topic": "Input Error",
                    "page": "N/A",
                    "form": "N/A"
                }
            }), 400
        
        # Check if question is within Tanzanian curriculum
        if not rule_enforcer.is_within_curriculum(question):
            return jsonify({
                "answer": "This question is outside the Tanzanian curriculum. Please ask about subjects in the TIE syllabus.",
                "source": {
                    "book": "TIE Curriculum Guidelines",
                    "subject": "General",
                    "topic": "Scope Limitation",
                    "page": "N/A",
                    "form": "N/A"
                }
            }), 200
        
        # Search for relevant content in TIE books
        relevant_content = book_loader.search_content(question, subject, form_level)
        
        if not relevant_content:
            return jsonify({
                "answer": "This information is not available in the TIE syllabus books. Please refer to your official textbooks.",
                "source": {
                    "book": "TIE Syllabus",
                    "subject": subject.capitalize(),
                    "topic": "Not Covered",
                    "page": "N/A",
                    "form": form_level
                }
            }), 200
        
        # Prepare context for AI
        context = book_loader.prepare_context(relevant_content, question)
        
        # Generate response using OpenRouter
        if openrouter_client and openrouter_client.is_configured():
            response = openrouter_client.generate_response(
                question=question,
                context=context,
                language=language,
                user_type=data.get('user_type', 'student')
            )
        else:
            # Fallback response
            response = f"""MAIN ANSWER: Based on TIE curriculum materials.

{relevant_content[0]['text'][:500]}...

A SIMPLE EXAMPLE: Refer to your TIE textbook for practical examples.

SOURCE:
- Book: {relevant_content[0]['book']}
- Subject: {relevant_content[0]['metadata']['subject'].capitalize()}
- Topic: Extracted from TIE materials
- Page: {relevant_content[0]['page']}"""
        
        # Extract source information
        source_info = book_loader.extract_source_info(relevant_content[0]) if relevant_content else {
            "book": "TIE Reference Material",
            "subject": subject.capitalize(),
            "topic": "General",
            "page": "Multiple",
            "form": form_level
        }
        
        return jsonify({
            "answer": response,
            "source": source_info,
            "confidence": relevant_content[0].get('confidence', 0.8) if relevant_content else 0.5,
            "books_used": [rc['book'] for rc in relevant_content[:3]]
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
            "source": {
                "book": "System Error",
                "subject": "Technical",
                "topic": "Processing Error",
                "page": "N/A",
                "form": "N/A"
            }
        }), 500

@app.route('/api/books', methods=['GET'])
def list_books():
    """List all available TIE books"""
    if not book_loader:
        return jsonify({"error": "Book loader not initialized"}), 503
    
    books = book_loader.list_books()
    return jsonify({
        "books": books,
        "total": len(books),
        "curriculum": "Tanzanian Secondary School (Form 1-6)",
        "books_directory": BOOKS_DIR
    })

@app.route('/api/upload', methods=['POST'])
def upload_book():
    """Upload a new TIE book (PDF)"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith('.pdf'): # type: ignore
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Save the file
        filepath = os.path.join(BOOKS_DIR, file.filename) # type: ignore
        file.save(filepath)
        
        # Index the book
        success = book_loader.index_book(filepath) # type: ignore
        
        if success:
            return jsonify({
                "message": f"Book '{file.filename}' uploaded and indexed successfully",
                "filename": file.filename,
                "total_books": len(book_loader.list_books()) # type: ignore
            }), 201
        else:
            # Clean up failed upload
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": "Failed to index book"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "TIE AI Tutor",
        "books_loaded": len(book_loader.list_books()) if book_loader else 0,
        "api_key_configured": openrouter_client.is_configured() if openrouter_client else False,
        "books_directory": BOOKS_DIR,
        "directory_exists": os.path.exists(BOOKS_DIR),
        "python_version": sys.version
    })

@app.route('/api/setup/check', methods=['GET'])
def setup_check():
    """Check setup status"""
    return jsonify({
        "books_directory": {
            "path": BOOKS_DIR,
            "exists": os.path.exists(BOOKS_DIR),
            "is_directory": os.path.isdir(BOOKS_DIR) if os.path.exists(BOOKS_DIR) else False,
            "files": os.listdir(BOOKS_DIR) if os.path.exists(BOOKS_DIR) else []
        },
        "backend_directory": os.path.dirname(os.path.abspath(__file__)),
        "current_working_directory": os.getcwd(),
        "book_loader_initialized": book_loader is not None,
        "total_books": len(book_loader.list_books()) if book_loader else 0
    })

if __name__ == '__main__':
    print("=" * 60)
    print("TIE AI Tutor - Tanzanian Educational AI System")
    print("=" * 60)
    print(f"📁 Books directory: {BOOKS_DIR}")
    print(f"✅ Directory exists: {os.path.exists(BOOKS_DIR)}")
    
    if os.path.exists(BOOKS_DIR):
        files = os.listdir(BOOKS_DIR)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        print(f"📄 Total files: {len(files)}")
        print(f"📚 PDF files: {len(pdf_files)}")
        for pdf in pdf_files[:5]:  # Show first 5 PDFs
            print(f"   - {pdf}")
        if len(pdf_files) > 5:
            print(f"   ... and {len(pdf_files) - 5} more")
    
    if book_loader:
        print(f"✅ Book loader initialized")
        books = book_loader.list_books()
        print(f"📚 Books loaded: {len(books)}")
        for book in books:
            print(f"   - {book['name']} ({book['subject']}, {book['form']})")
    else:
        print("❌ Book loader failed to initialize")
    
    print("=" * 60)
    print("🌐 Starting server on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, port=5000)