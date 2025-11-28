from textblob import TextBlob
import re
from collections import Counter

class NLPAnalyzer:
    
    @staticmethod
    def analyze_sentiment(text):
        """Analyze sentiment of text"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    @staticmethod
    def extract_themes(text):
        """Extract key themes from text"""
        # Simple keyword extraction
        text_lower = text.lower()
        
        # Define theme keywords
        themes = {
            'healthcare': ['health', 'hospital', 'doctor', 'clinic', 'medicine', 'treatment'],
            'education': ['school', 'education', 'teacher', 'student', 'university', 'learning'],
            'infrastructure': ['road', 'bridge', 'water', 'electricity', 'construction', 'building'],
            'agriculture': ['farm', 'crop', 'agriculture', 'farming', 'harvest', 'land'],
            'security': ['police', 'security', 'crime', 'safety', 'theft'],
            'corruption': ['corruption', 'bribe', 'fraud', 'embezzlement', 'misuse'],
            'employment': ['job', 'employment', 'work', 'unemployment', 'salary']
        }
        
        detected_themes = []
        for theme, keywords in themes.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_themes.append(theme)
        
        return detected_themes if detected_themes else ['general']
    
    @staticmethod
    def categorize_complaint(text):
        """Categorize complaint based on content"""
        text_lower = text.lower()
        
        categories = {
            'Infrastructure': ['road', 'water', 'electricity', 'bridge', 'pothole'],
            'Healthcare': ['hospital', 'health', 'doctor', 'medicine', 'clinic'],
            'Education': ['school', 'teacher', 'education', 'student'],
            'Security': ['police', 'crime', 'theft', 'safety'],
            'Corruption': ['bribe', 'corruption', 'fraud'],
            'Agriculture': ['farm', 'agriculture', 'crop'],
            'Other': []
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'Other'
    
    @staticmethod
    def assess_priority(text):
        """Assess priority level of complaint"""
        text_lower = text.lower()
        
        urgent_keywords = ['urgent', 'emergency', 'critical', 'dying', 'death', 'serious', 'life']
        high_keywords = ['danger', 'risk', 'threat', 'severe', 'major']
        
        if any(keyword in text_lower for keyword in urgent_keywords):
            return 'Urgent'
        elif any(keyword in text_lower for keyword in high_keywords):
            return 'High'
        else:
            return 'Normal'