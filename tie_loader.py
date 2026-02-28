import os
import PyPDF2 # type: ignore
import pdfplumber # pyright: ignore[reportMissingImports]
import pytesseract # type: ignore
from PIL import Image # pyright: ignore[reportMissingImports]
import re
from typing import Dict, List, Optional, Tuple
import json
from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import numpy as np # pyright: ignore[reportMissingImports]

# debug: attempt to list books directory relative to this file
try:
    debug_dir = os.path.join(os.path.dirname(__file__), "..", "tie_books")
    print("FILES FOUND:", os.listdir(debug_dir))
except Exception as e:
    print(f"Could not list tie_books directory: {e}")

class TIEBookLoader:
    def __init__(self, books_dir: str):
        self.books_dir = books_dir
        self.books_index = {}
        self.text_chunks = []
        self.metadata = []
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.tfidf_matrix = None
        
        # Load existing books
        self._load_books()
    
    def _load_books(self):
        """Load all PDF books from the directory"""
        if not os.path.exists(self.books_dir):
            print(f"Books directory does not exist: {self.books_dir}")
            return
        
        pdf_files = [f for f in os.listdir(self.books_dir) if f.lower().endswith('.pdf')]
        
        for pdf_file in pdf_files:
            try:
                self.index_book(os.path.join(self.books_dir, pdf_file))
            except Exception as e:
                print(f"Error loading book {pdf_file}: {str(e)}")
    
    def index_book(self, filepath: str) -> bool:
        """Index a single book"""
        try:
            book_name = os.path.basename(filepath)
            
            # Extract metadata from filename
            metadata = self._extract_metadata_from_filename(book_name)
            
            # Extract text from PDF
            text_chunks, pages = self._extract_text_from_pdf(filepath)
            
            if not text_chunks:
                print(f"No text extracted from {book_name}")
                return False
            
            # Store in index
            self.books_index[book_name] = {
                'path': filepath,
                'metadata': metadata,
                'text_chunks': text_chunks,
                'pages': pages,
                'total_pages': len(pages)
            }
            
            # Add to text chunks for search
            for i, (chunk, page) in enumerate(zip(text_chunks, pages)):
                self.text_chunks.append({
                    'book': book_name,
                    'text': chunk,
                    'page': page,
                    'metadata': metadata,
                    'chunk_id': f"{book_name}_{i}"
                })
            
            # Rebuild TF-IDF matrix
            if self.text_chunks:
                self._build_search_index()
            
            print(f"Successfully indexed: {book_name}")
            return True
            
        except Exception as e:
            print(f"Error indexing book {filepath}: {str(e)}")
            return False
    
    def _extract_metadata_from_filename(self, filename: str) -> Dict:
        """Extract subject and form from filename"""
        filename_lower = filename.lower()
        
        # Map subjects
        subject_map = {
            'physics': 'physics',
            'chemistry': 'chemistry',
            'biology': 'biology',
            'math': 'mathematics',
            'kiswahili': 'kiswahili',
            'english': 'english',
            'geography': 'geography',
            'history': 'history',
            'civics': 'civics'
        }
        
        # Extract subject
        subject = 'general'
        for key, value in subject_map.items():
            if key in filename_lower:
                subject = value
                break
        
        # Extract form
        form_match = re.search(r'form[_\s]*(\d)', filename_lower, re.IGNORECASE)
        form = form_match.group(1) if form_match else '1'
        
        # Extract Swahili form
        if not form_match:
            kidato_match = re.search(r'kidato[_\s]*(\d)', filename_lower, re.IGNORECASE)
            form = kidato_match.group(1) if kidato_match else '1'
        
        return {
            'subject': subject,
            'form': f'form{form}',
            'filename': filename,
            'language': 'sw' if 'kiswahili' in filename_lower or 'kidato' in filename_lower else 'en'
        }
    
    def _extract_text_from_pdf(self, filepath: str) -> Tuple[List[str], List[int]]:
        """Extract text from PDF file"""
        text_chunks = []
        pages = []
        
        try:
            # Try pdfplumber first for better text extraction
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    # if text is missing or too short, attempt OCR
                    if not text or len(text.strip()) <= 50:
                        try:
                            # generate PIL image for OCR (higher resolution helps)
                            pil_image = page.to_image(resolution=300).original
                            ocr_text = pytesseract.image_to_string(pil_image)
                            if ocr_text and len(ocr_text.strip()) > len(text or ""):
                                text = ocr_text
                                print(f"[OCR] extracted on page {page_num}")
                        except Exception as ocr_e:
                            print(f"OCR error on page {page_num}: {ocr_e}")
                    if text and len(text.strip()) > 50:  # Only add meaningful chunks
                        # Split into smaller chunks if text is too long
                        chunk_size = 1000
                        for i in range(0, len(text), chunk_size):
                            chunk = text[i:i + chunk_size]
                            if len(chunk.strip()) > 50:
                                text_chunks.append(chunk)
                                pages.append(page_num)
            
            # Fallback to PyPDF2 if pdfplumber (and OCR) fails
            if not text_chunks:
                with open(filepath, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        if not text or len(text.strip()) <= 50:
                            # try OCR using page image if available
                            try:
                                pil_image = pdfplumber.open(filepath).pages[page_num].to_image(resolution=300).original
                                ocr_text = pytesseract.image_to_string(pil_image)
                                if ocr_text and len(ocr_text.strip()) > len(text or ""):
                                    text = ocr_text
                                    print(f"[OCR] extracted in PyPDF2 fallback on page {page_num+1}")
                            except Exception:
                                pass
                        if text and len(text.strip()) > 50:
                            chunk_size = 1000
                            for i in range(0, len(text), chunk_size):
                                chunk = text[i:i + chunk_size]
                                if len(chunk.strip()) > 50:
                                    text_chunks.append(chunk)
                                    pages.append(page_num + 1)
        
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
        
        return text_chunks, pages
    
    def _build_search_index(self):
        """Build TF-IDF search index"""
        if not self.text_chunks:
            return
        
        texts = [chunk['text'] for chunk in self.text_chunks]
        
        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        except Exception as e:
            print(f"Error building search index: {str(e)}")
    
    def search_content(self, query: str, subject: str = 'all', form_level: str = '') -> List[Dict]:
        """Search for relevant content in books"""
        if not self.text_chunks or self.tfidf_matrix is None:
            return []
        
        try:
            # Transform query to TF-IDF
            query_vec = self.vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Get top results
            top_indices = similarities.argsort()[-10:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    chunk = self.text_chunks[idx]
                    
                    # Filter by subject if specified
                    if subject != 'all' and chunk['metadata']['subject'] != subject:
                        continue
                    
                    # Filter by form level if specified
                    if form_level and chunk['metadata']['form'] != form_level:
                        continue
                    
                    results.append({
                        'text': chunk['text'],
                        'book': chunk['book'],
                        'page': chunk['page'],
                        'metadata': chunk['metadata'],
                        'confidence': float(similarities[idx]),
                        'chunk_id': chunk['chunk_id']
                    })
            
            return results
            
        except Exception as e:
            print(f"Error searching content: {str(e)}")
            return []
    
    def prepare_context(self, relevant_content: List[Dict], question: str) -> str:
        """Prepare context from relevant content for AI"""
        if not relevant_content:
            return "No relevant content found in TIE books."
        
        context_parts = []
        
        # Add the most relevant chunks
        for i, content in enumerate(relevant_content[:3]):  # Use top 3 chunks
            context_parts.append(
                f"[Source: {content['book']}, Page: {content['page']}, Subject: {content['metadata']['subject'].capitalize()}]\n"
                f"{content['text']}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Add instructions
        context += f"\n\nQuestion: {question}\n\n"
        context += "IMPORTANT: Answer ONLY using the information from the TIE books above. "
        context += "Do not add any external knowledge. If the answer is not in the text, "
        context += "say 'This answer is not in the TIE syllabus'."
        
        return context
    
    def extract_source_info(self, content: Dict) -> Dict:
        """Extract source information from content"""
        if not content:
            return {
                "book": "TIE Reference Material",
                "subject": "General",
                "topic": "Unknown",
                "page": "N/A",
                "form": "N/A"
            }
        
        # Try to extract topic from text
        text = content['text']
        topic = self._extract_topic_from_text(text)
        
        return {
            "book": content['book'].replace('.pdf', '').replace('_', ' ').title(),
            "subject": content['metadata']['subject'].capitalize(),
            "topic": topic,
            "page": str(content['page']),
            "form": content['metadata']['form'].replace('form', 'Form ').capitalize()
        }
    
    def _extract_topic_from_text(self, text: str) -> str:
        """Extract topic from text (simple heuristic)"""
        # Look for common topic indicators
        lines = text.split('\n')
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if len(line) > 10 and len(line) < 100:  # Reasonable length for a topic
                if line.isupper() or line.endswith(':') or any(word in line.lower() for word in ['chapter', 'topic', 'unit', 'lesson']):
                    return line
        
        # Fallback: Use first sentence
        sentences = re.split(r'[.!?]', text)
        if sentences and len(sentences[0]) > 10:
            return sentences[0][:50] + "..." if len(sentences[0]) > 50 else sentences[0]
        
        return "General Topic"
    
    def list_books(self) -> List[Dict]:
        """List all loaded books"""
        books = []
        for book_name, book_info in self.books_index.items():
            books.append({
                'name': book_name,
                'subject': book_info['metadata']['subject'],
                'form': book_info['metadata']['form'],
                'language': book_info['metadata']['language'],
                'pages': book_info['total_pages'],
                'chunks': len(book_info['text_chunks'])
            })
        return books
    
    def get_subjects(self) -> List[str]:
        """Get list of available subjects"""
        subjects = set()
        for book_info in self.books_index.values():
            subjects.add(book_info['metadata']['subject'])
        return sorted(list(subjects))
    
    def get_loaded_subjects(self) -> Dict:
        """Get loaded subjects count"""
        subject_count = {}
        for book_info in self.books_index.values():
            subject = book_info['metadata']['subject']
            subject_count[subject] = subject_count.get(subject, 0) + 1
        return subject_count