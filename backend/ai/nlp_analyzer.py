from textblob import TextBlob
import re
from collections import Counter
import random

class NLPAnalyzer:
    
    # Enhanced keyword mappings for better categorization
    CATEGORY_KEYWORDS = {
        'Healthcare': {
            'keywords': ['health', 'hospital', 'doctor', 'clinic', 'medicine', 'treatment', 'medical', 
                        'nurse', 'patient', 'drug', 'pharmacy', 'vaccine', 'disease', 'sick', 'medication'],
            'ministry_code': 'MOH'
        },
        'Education': {
            'keywords': ['school', 'education', 'teacher', 'student', 'university', 'learning', 'class',
                        'exam', 'books', 'tuition', 'college', 'academic', 'teaching', 'scholarship'],
            'ministry_code': 'MOES'
        },
        'Infrastructure': {
            'keywords': ['road', 'bridge', 'water', 'electricity', 'construction', 'building', 'pothole',
                        'drainage', 'street', 'highway', 'transport', 'infrastructure', 'maintenance'],
            'ministry_code': 'MOWT'
        },
        'Agriculture': {
            'keywords': ['farm', 'crop', 'agriculture', 'farming', 'harvest', 'land', 'seed', 'fertilizer',
                        'livestock', 'cattle', 'chicken', 'maize', 'beans', 'cassava', 'agricultural'],
            'ministry_code': 'MAAIF'
        },
        'Security': {
            'keywords': ['police', 'security', 'crime', 'safety', 'theft', 'robbery', 'violence', 'assault',
                        'burglar', 'gang', 'attack', 'weapon', 'protection'],
            'ministry_code': 'MIA'
        },
        'Water': {
            'keywords': ['water', 'well', 'borehole', 'tap', 'clean water', 'drinking water', 'water supply',
                        'pump', 'reservoir', 'sanitation', 'sewage', 'drainage'],
            'ministry_code': 'MWE'
        },
        'Energy': {
            'keywords': ['electricity', 'power', 'energy', 'umeme', 'transformer', 'blackout', 'outage',
                        'electrical', 'light', 'grid', 'solar', 'generator'],
            'ministry_code': 'MEMD'
        },
        'Corruption': {
            'keywords': ['corruption', 'bribe', 'fraud', 'embezzlement', 'misuse', 'steal', 'corrupt',
                        'kickback', 'nepotism', 'favoritism'],
            'ministry_code': 'MIA'
        }
    }
    
    @staticmethod
    def analyze_sentiment(text):
        """Analyze sentiment of text with enhanced accuracy"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Enhanced sentiment analysis
        if polarity > 0.15:
            return 'positive'
        elif polarity < -0.15:
            return 'negative'
        else:
            return 'neutral'
    
    @staticmethod
    def extract_themes(text):
        """Extract key themes from text with better accuracy"""
        text_lower = text.lower()
        detected_themes = []
        theme_scores = {}
        
        for theme, config in NLPAnalyzer.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in config['keywords'] if keyword in text_lower)
            if score > 0:
                theme_scores[theme] = score
        
        # Sort by score and return top themes
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        detected_themes = [theme for theme, score in sorted_themes[:3] if score > 0]
        
        return detected_themes if detected_themes else ['general']
    
    @staticmethod
    def categorize_complaint(text):
        """Categorize complaint based on content with scoring"""
        text_lower = text.lower()
        category_scores = {}
        
        for category, config in NLPAnalyzer.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in config['keywords'] if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # Return category with highest score
            best_category = max(category_scores.items(), key=lambda x: x[1])[0]
            return best_category
        
        return 'Other'
    
    @staticmethod
    def get_ministry_code_for_category(category):
        """Get ministry code for a given category"""
        config = NLPAnalyzer.CATEGORY_KEYWORDS.get(category)
        return config['ministry_code'] if config else None
    
    @staticmethod
    def assess_priority(text):
        """Assess priority level of complaint with better detection"""
        text_lower = text.lower()
        
        urgent_keywords = ['urgent', 'emergency', 'critical', 'dying', 'death', 'serious', 'life-threatening',
                          'immediate', 'crisis', 'danger', 'fatal']
        high_keywords = ['danger', 'risk', 'threat', 'severe', 'major', 'important', 'significant',
                        'urgent', 'pressing', 'concern']
        
        urgent_score = sum(1 for keyword in urgent_keywords if keyword in text_lower)
        high_score = sum(1 for keyword in high_keywords if keyword in text_lower)
        
        if urgent_score >= 2 or any(word in text_lower for word in ['dying', 'death', 'life-threatening']):
            return 'Urgent'
        elif urgent_score >= 1 or high_score >= 2:
            return 'High'
        else:
            return 'Normal'
    
    @staticmethod
    def generate_insights(text):
        """Generate AI insights from complaint text"""
        sentiment = NLPAnalyzer.analyze_sentiment(text)
        themes = NLPAnalyzer.extract_themes(text)
        priority = NLPAnalyzer.assess_priority(text)
        
        insights = []
        
        # Generate contextual insights
        if sentiment == 'negative' and priority == 'Urgent':
            insights.append("This complaint requires immediate attention due to negative sentiment and urgent priority.")
        
        if 'corruption' in text.lower():
            insights.append("Potential corruption issue detected. Consider flagging for investigation.")
        
        word_count = len(text.split())
        if word_count < 10:
            insights.append("Complaint description is brief. May need follow-up for more details.")
        
        return {
            'sentiment': sentiment,
            'themes': themes,
            'priority': priority,
            'insights': insights,
            'confidence': 0.75 + (len(themes) * 0.05)  # Simple confidence score
        }