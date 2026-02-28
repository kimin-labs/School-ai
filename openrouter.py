import os
import requests
import json
from typing import Dict, List, Optional

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv('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')
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = os.getenv('OPENROUTER_MODEL', 'nvidia/nemotron-3-nano-30b-a3b:free')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "TIE AI Tutor"
        }
    
    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return self.api_key is not None and self.api_key != ""
    
    def generate_response(self, question: str, context: str, language: str = 'en', user_type: str = 'student') -> str:
        """
        Generate a response using OpenRouter API
        """
        if not self.is_configured():
            return self._get_fallback_response(question, language, user_type)
        
        # Prepare system prompt based on user type and language
        system_prompt = self._create_system_prompt(language, user_type)
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"Context from TIE books:\n{context}\n\nQuestion: {question}"
            }
        ]
        
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,  # Lower temperature for more consistent answers
                "max_tokens": 1000,
                "top_p": 0.9,
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(question, language, user_type)
                
        except Exception as e:
            print(f"Error calling OpenRouter API: {str(e)}")
            return self._get_fallback_response(question, language, user_type)
    
    def _create_system_prompt(self, language: str, user_type: str) -> str:
        """Create system prompt based on language and user type"""
        
        if language == 'sw':  # Kiswahili
            prompt = f"""Wewe ni TIE AI Tutor, Msaidizi wa Kiakili wa Elimu ya Tanzania.

WEWE NI:
- Mwalimu wa Tasnia ya TIE (Taasisi ya Elimu ya Tanzania)
- Mtaalamu wa Mitaala ya Shule za Sekondari Tanzania (Kidato 1-6)
- Msaidizi wa Kitabu rasmi cha TIE pekee

DIRECTIONS KALI:
1. Tumia kitabu cha TIE pekee kwa majibu
2. Usijibu maswali yoyote nje ya mitaala ya Tanzania
3. Usiongeze maarifa yoyote ya nje
4. Usibadilishe maana ya maandishi ya kitabu
5. Kama jibu halipo katika kitabu, sema: "Jibu hili halipo katika mitaala ya TIE"

MUUNDO WA JAWABU:
1. JAWABU KUU (kutoka kwa kitabu)
2. MFANO RAHISI (kulingana na kiwango cha mwanafunzi)
3. CHANZO:
   - Kitabu:
   - Somo:
   - Mada:
   - Ukurasa:

Lugha: Tumia Kiswahili cha kawaida, rahisi kueleweka.

Mtumiaji: { 'Mwanafunzi' if user_type == 'student' else 'Mwalimu' }"""
        
        else:  # English (default)
            prompt = f"""You are TIE AI Tutor, Tanzanian Educational AI Assistant.

YOU ARE:
- TIE Institute AI (Tanzania Institute of Education)
- Tanzanian Secondary School Curriculum Expert (Form 1-6)
- Official TIE Book Assistant ONLY

STRICT DIRECTIONS:
1. Use TIE book only for answers
2. Do not answer any questions outside Tanzanian syllabus
3. Do not add outside knowledge
4. Do not change the meaning of book text
5. If answer not in book, say: "This answer is not in the TIE syllabus"

ANSWER FORMAT:
1. MAIN ANSWER (from the book)
2. A SIMPLE EXAMPLE (according to student's level)
3. SOURCE:
   - Book:
   - Subject:
   - Topic:
   - Page:

Language: Use clear, simple English.

User: {user_type.capitalize()}"""
        
        return prompt
    
    def _get_fallback_response(self, question: str, language: str, user_type: str) -> str:
        """Provide fallback response when API is not available"""
        
        if language == 'sw':
            return f"""JIBU KUU: Ninaomba radhi, mfumo wa TIE AI haupo tayari kwa sasa. Tafadhali rejelea vitabu rasmi vya TIE.

MFANO RAHISI: Angalia kitabu chako cha TIE kwenye mada husika.

CHANZO:
- Kitabu: Mfumo wa TIE AI
- Somo: Huduma ya Kiufundi
- Mada: Usakinishaji
- Ukurasa: N/A"""
        else:
            return f"""MAIN ANSWER: I apologize, the TIE AI system is not fully available at the moment. Please refer to your official TIE books.

A SIMPLE EXAMPLE: Check your TIE book on the relevant topic.

SOURCE:
- Book: TIE AI System
- Subject: Technical Service
- Topic: Setup
- Page: N/A"""

    def check_api_status(self) -> Dict:
        """Check OpenRouter API status"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            return {
                "status": "connected" if response.status_code == 200 else "disconnected",
                "status_code": response.status_code,
                "models_available": len(response.json().get('data', [])) if response.status_code == 200 else 0
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }