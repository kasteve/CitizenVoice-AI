from flask import Blueprint, request, jsonify
from models import db, PolicyFeedback, Complaint, ServiceRating, Citizen, Ministry
from ai.nlp_analyzer import NLPAnalyzer
from email_service import send_complaint_confirmation
from auth import token_required
import uuid
from datetime import datetime

bp = Blueprint('feedback', __name__)
nlp = NLPAnalyzer()

@bp.route('/policy', methods=['POST'])
@token_required
def submit_policy_feedback(current_user):
    data = request.get_json()
    
    # Analyze feedback
    sentiment = nlp.analyze_sentiment(data['feedback_text'])
    themes = nlp.extract_themes(data['feedback_text'])
    
    feedback = PolicyFeedback(
        policy_id=data['policy_id'],
        citizen_id=current_user.id,
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
@token_required
def submit_complaint(current_user):
    data = request.get_json()
    
    # Analyze complaint
    category = data.get('category') or nlp.categorize_complaint(data['description'])
    priority = nlp.assess_priority(data['description'])
    tracking_number = f"CMP-{uuid.uuid4().hex[:8].upper()}"
    
    # Auto-assign ministry based on category
    ministry_mapping = {
        'Infrastructure': 'MOWT',
        'Healthcare': 'MOH',
        'Education': 'MOES',
        'Security': 'MIA',
        'Agriculture': 'MAAIF',
        'Water': 'MWE',
        'Energy': 'MEMD'
    }
    
    ministry = None
    if category in ministry_mapping:
        ministry = Ministry.query.filter_by(code=ministry_mapping[category]).first()
    
    complaint = Complaint(
        citizen_id=current_user.id,
        ministry_id=ministry.id if ministry else None,
        district_id=current_user.district_id,
        category=category,
        description=data['description'],
        location=data.get('location'),
        priority=priority,
        tracking_number=tracking_number
    )
    
    db.session.add(complaint)
    db.session.commit()
    
    # Send email confirmation
    if current_user.email:
        send_complaint_confirmation(
            current_user.email,
            current_user.name,
            tracking_number,
            category,
            priority
        )
    
    return jsonify({
        'message': 'Complaint submitted successfully',
        'complaint': complaint.to_dict(),
        'tracking_number': tracking_number
    }), 201

@bp.route('/complaint/<tracking_number>', methods=['GET'])
def track_complaint(tracking_number):
    complaint = Complaint.query.filter_by(tracking_number=tracking_number.upper()).first_or_404()
    return jsonify(complaint.to_dict())

@bp.route('/complaint/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_complaints(current_user, user_id):
    # Users can only view their own complaints unless they're admin
    if current_user.id != user_id and current_user.role_id != 2:
        return jsonify({'error': 'Unauthorized'}), 403
    
    complaints = Complaint.query.filter_by(citizen_id=user_id).order_by(Complaint.created_at.desc()).all()
    return jsonify([c.to_dict() for c in complaints])

@bp.route('/rating', methods=['POST'])
@token_required
def submit_rating(current_user):
    data = request.get_json()
    
    rating = ServiceRating(
        citizen_id=current_user.id,
        service_type=data['service_type'],
        service_location=data['service_location'],
        district_id=data.get('district_id') or current_user.district_id,
        rating=data['rating'],
        comment=data.get('comment')
    )
    
    db.session.add(rating)
    db.session.commit()
    
    return jsonify({
        'message': 'Rating submitted successfully',
        'rating': rating.to_dict()
    }), 201