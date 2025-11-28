from flask import Blueprint, request, jsonify
from models import db, PolicyFeedback, Complaint, ServiceRating, Citizen
from ai.nlp_analyzer import NLPAnalyzer
import uuid
from datetime import datetime

bp = Blueprint('feedback', __name__)
nlp = NLPAnalyzer()

@bp.route('/policy', methods=['POST'])
def submit_policy_feedback():
    data = request.get_json()
    
    # Analyze feedback
    sentiment = nlp.analyze_sentiment(data['feedback_text'])
    themes = nlp.extract_themes(data['feedback_text'])
    
    feedback = PolicyFeedback(
        policy_id=data['policy_id'],
        citizen_id=data['citizen_id'],
        feedback_text=data['feedback_text'],
        sentiment=sentiment,
        themes=','.join(themes)
    )
    
    db.session.add(feedback)
    db.session.commit()
    
    return jsonify({
        'message': 'Feedback submitted successfully',
        'feedback': feedback.to_dict(),
        'analysis': {
            'sentiment': sentiment,
            'themes': themes
        }
    }), 201

@bp.route('/complaint', methods=['POST'])
def submit_complaint():
    data = request.get_json()
    
    # Analyze complaint
    category = nlp.categorize_complaint(data['description'])
    priority = nlp.assess_priority(data['description'])
    tracking_number = f"CMP-{uuid.uuid4().hex[:8].upper()}"
    
    complaint = Complaint(
        citizen_id=data['citizen_id'],
        category=data.get('category', category),
        description=data['description'],
        location=data.get('location'),
        priority=priority,
        tracking_number=tracking_number
    )
    
    db.session.add(complaint)
    db.session.commit()
    
    return jsonify({
        'message': 'Complaint submitted successfully',
        'complaint': complaint.to_dict(),
        'tracking_number': tracking_number
    }), 201

@bp.route('/complaint/<tracking_number>', methods=['GET'])
def track_complaint(tracking_number):
    complaint = Complaint.query.filter_by(tracking_number=tracking_number).first_or_404()
    return jsonify(complaint.to_dict())

@bp.route('/rating', methods=['POST'])
def submit_rating():
    data = request.get_json()
    
    rating = ServiceRating(
        citizen_id=data['citizen_id'],
        service_type=data['service_type'],
        service_location=data['service_location'],
        rating=data['rating'],
        comment=data.get('comment')
    )
    
    db.session.add(rating)
    db.session.commit()
    
    return jsonify({
        'message': 'Rating submitted successfully',
        'rating': rating.to_dict()
    }), 201