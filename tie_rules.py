import re
from typing import List, Dict, Set

class TIERuleEnforcer:
    def __init__(self):
        # Tanzanian curriculum subjects
        self.tanzanian_subjects = {
            'physics', 'chemistry', 'biology', 'mathematics',
            'kiswahili', 'english', 'geography', 'history',
            'civics', 'commerce', 'bookkeeping', 'accounting',
            'economics', 'agriculture', 'computer studies',
            'technical education', 'fine arts', 'physical education',
            'religious education', 'islamic education', 'christian education'
        }
        
        # Tanzanian forms/classes
        self.tanzanian_forms = {
            'form 1', 'form 2', 'form 3', 'form 4', 'form 5', 'form 6',
            'kidato cha 1', 'kidato cha 2', 'kidato cha 3', 'kidato cha 4',
            'kidato cha 5', 'kidato cha 6'
        }
        
        # Common Tanzanian curriculum topics
        self.tanzanian_topics = {
            # Physics
            'measurement', 'force', 'motion', 'energy', 'heat', 'light',
            'waves', 'electricity', 'magnetism', 'electronics',
            
            # Chemistry
            'matter', 'elements', 'compounds', 'chemical reactions',
            'acids', 'bases', 'salts', 'organic chemistry',
            'periodic table', 'chemical bonding',
            
            # Biology
            'cell', 'nutrition', 'respiration', 'excretion', 'growth',
            'reproduction', 'genetics', 'ecology', 'evolution',
            'classification', 'human body',
            
            # Mathematics
            'algebra', 'geometry', 'trigonometry', 'calculus',
            'statistics', 'probability', 'number', 'set',
            
            # Languages
            'grammar', 'composition', 'comprehension', 'literature',
            'poetry', 'novel', 'play', 'essay',
            
            # Social Sciences
            'map reading', 'climate', 'weather', 'population',
            'agriculture', 'industry', 'transport', 'colonization',
            'independence', 'government', 'constitution'
        }
        
        # Forbidden topics (outside Tanzanian curriculum)
        self.forbidden_topics = {
            # International topics not in Tanzanian syllabus
            'american history', 'european history', 'asian history',
            'calculus ii', 'differential equations', 'quantum physics',
            'organic chemistry ii', 'biochemistry', 'molecular biology',
            # Politics
            'international politics', 'foreign policy',
            # Advanced topics
            'astrophysics', 'nuclear physics', 'genetic engineering',
            # Other countries' curriculum
            'igcse', 'a level', 'ib diploma', 'sat', 'act'
        }
        
    def is_within_curriculum(self, question: str) -> bool:
        """
        Check if a question is within Tanzanian curriculum
        """
        question_lower = question.lower()
        
        # Check for forbidden topics
        for topic in self.forbidden_topics:
            if topic in question_lower:
                return False
        
        # Check if question mentions Tanzanian subjects or forms
        has_tanzanian_subject = any(subject in question_lower for subject in self.tanzanian_subjects)
        has_tanzanian_form = any(form in question_lower for form in self.tanzanian_forms)
        has_tanzanian_topic = any(topic in question_lower for topic in self.tanzanian_topics)
        
        # Common educational keywords that might indicate curriculum question
        educational_keywords = {
            'explain', 'define', 'what is', 'how does', 'why does',
            'calculate', 'solve', 'describe', 'compare', 'contrast',
            'example', 'diagram', 'formula', 'equation', 'experiment'
        }
        
        has_educational_keyword = any(keyword in question_lower for keyword in educational_keywords)
        
        # Question is within curriculum if:
        # 1. It mentions a Tanzanian subject OR form OR topic, AND
        # 2. It has educational keywords OR is clearly a question
        if (has_tanzanian_subject or has_tanzanian_form or has_tanzanian_topic):
            if has_educational_keyword or question_lower.endswith('?'):
                return True
        
        # Special cases: Direct questions about Tanzanian education
        tanzanian_education_keywords = {
            'tie', 'tanzania institute', 'tanzanian curriculum',
            'necta', 'national examination', 'secondary school tanzania'
        }
        
        if any(keyword in question_lower for keyword in tanzanian_education_keywords):
            return True
        
        return False
    
    def extract_subject(self, question: str) -> str:
        """
        Extract subject from question
        """
        question_lower = question.lower()
        
        for subject in self.tanzanian_subjects:
            if subject in question_lower:
                return subject
        
        # Try to infer from keywords
        if any(word in question_lower for word in ['physics', 'force', 'motion', 'energy']):
            return 'physics'
        elif any(word in question_lower for word in ['chemistry', 'chemical', 'acid', 'base']):
            return 'chemistry'
        elif any(word in question_lower for word in ['biology', 'cell', 'plant', 'animal']):
            return 'biology'
        elif any(word in question_lower for word in ['math', 'calculate', 'equation', 'algebra']):
            return 'mathematics'
        elif any(word in question_lower for word in ['kiswahili', 'swahili', 'lugha']):
            return 'kiswahili'
        elif any(word in question_lower for word in ['english', 'grammar', 'composition']):
            return 'english'
        
        return 'general'
    
    def extract_form_level(self, question: str) -> str:
        """
        Extract form level from question
        """
        question_lower = question.lower()
        
        form_mapping = {
            'form 1': 'form1', 'kidato cha 1': 'form1',
            'form 2': 'form2', 'kidato cha 2': 'form2',
            'form 3': 'form3', 'kidato cha 3': 'form3',
            'form 4': 'form4', 'kidato cha 4': 'form4',
            'form 5': 'form5', 'kidato cha 5': 'form5',
            'form 6': 'form6', 'kidato cha 6': 'form6',
        }
        
        for form_str, form_code in form_mapping.items():
            if form_str in question_lower:
                return form_code
        
        # Default to Form 1
        return 'form1'
    
    def validate_answer(self, answer: str, source: Dict) -> bool:
        """
        Validate that answer follows TIE guidelines
        """
        if not answer:
            return False
        
        # Check if answer contains disclaimer for non-TIE content
        disclaimer_phrases = [
            'not in the tie syllabus',
            'not in tanzanian curriculum',
            'outside the syllabus',
            'not covered in tie books'
        ]
        
        answer_lower = answer.lower()
        has_disclaimer = any(phrase in answer_lower for phrase in disclaimer_phrases)
        
        # If answer has disclaimer, it's valid (it's saying it can't answer)
        if has_disclaimer:
            return True
        
        # Check if answer contains source information
        source_indicators = ['book:', 'subject:', 'topic:', 'page:', 'source:']
        has_source_info = any(indicator in answer_lower for indicator in source_indicators)
        
        return has_source_info
    
    def get_curriculum_guidelines(self) -> Dict:
        """
        Get Tanzanian curriculum guidelines
        """
        return {
            "education_system": "Tanzanian Education System",
            "levels": [
                {
                    "level": "Ordinary Level (O-Level)",
                    "forms": ["Form 1", "Form 2", "Form 3", "Form 4"],
                    "subjects": [
                        "Mathematics", "English", "Kiswahili", "Physics",
                        "Chemistry", "Biology", "Geography", "History",
                        "Civics", "Commerce", "Book Keeping", "Bible Knowledge",
                        "Islamic Knowledge", "Home Economics", "Additional Mathematics"
                    ]
                },
                {
                    "level": "Advanced Level (A-Level)",
                    "forms": ["Form 5", "Form 6"],
                    "streams": [
                        {
                            "stream": "Science",
                            "subjects": ["Physics", "Chemistry", "Biology", "Mathematics"]
                        },
                        {
                            "stream": "Arts",
                            "subjects": ["Geography", "History", "Kiswahili", "English", "French"]
                        },
                        {
                            "stream": "Commerce",
                            "subjects": ["Commerce", "Accountancy", "Economics"]
                        }
                    ]
                }
            ],
            "examining_body": "NECTA (National Examinations Council of Tanzania)",
            "curriculum_authority": "TIE (Tanzania Institute of Education)",
            "language_of_instruction": "Kiswahili (Primary), English (Secondary)",
            "school_years": "January to December"
        }