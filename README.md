# TIE AI TUTOR

## Overview
**TIE AI TUTOR** is a full-size educational website designed for secondary school students and teachers in Tanzania.  
Its goal is to provide accurate, curriculum-aligned answers using **ONLY official TIE books**.

This system is:

- A Tanzanian curriculum-focused AI
- A learning aid for students
- A verification tool for teachers
- Strictly restricted to syllabus content

> ⚠️ Questions outside the syllabus will receive the response:  
> “This answer is not in the TIE syllabus”

---

## Key Features

### AI Capabilities
- Uses **OpenRouter API** (example model: `openai/gpt-4o-mini`)
- Reads TIE PDF books
- Fetches answers according to:
  - Book
  - Subject
  - Topic
  - Pages
- Supports **Kiswahili and English**
- Provides examples suitable for student level

### Frontend Features
- Modern, minimalist, clean, and professional UI
- Chat interface similar to ChatGPT
- Question input at the bottom, answers appear at the top
- Smooth animations
- Responsive design (mobile + desktop)
- Theme toggle:
  - 🌙 Dark Mode
  - ☀️ Light Mode

### Backend Features
- Built with **Python** and **Flask**
- Handles AI interactions, PDF reading, and syllabus validation
- Modular structure for easy maintenance

---

## Technology Stack

### Frontend
- HTML
- CSS
- JavaScript (vanilla or lightweight framework)

### Backend
- Python
- Flask

### AI
- OpenRouter API (key required)
- Model example: `openai/gpt-4o-mini`

### Books
- TIE books (PDF format) stored inside `tie_books/`
- System can read, parse, and query PDFs

---

## Project Structure

```plaintext
frontend/
  ├─ index.html
  ├─ login.html
  ├─ style.css
  └─ script.js

backend/
  ├─ app.py
  ├─ openrouter.py
  ├─ tie_loader.py
  ├─ tie_rules.py
  └─ requirements.txt

tie_books/
  ├─ physics_form2.pdf
  ├─ chemistry_form1.pdf
  └─ biology_form3.pdf
