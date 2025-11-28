from flask import Blueprint, request, jsonify
from models import db, Policy, PolicyFeedback
from sqlalchemy import func

bp = Blueprint('policies', __name__)

@bp.route('/', methods=['GET'])
def get_policies():
    status = request.args.get('status')
    category = request.args.get('category')
    
    query = Policy.query
    
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    
    policies = query.order_by(Policy.created_at.desc()).all()
    return jsonify([p.to_dict() for p in policies])

@bp.route('/<int:id>', methods=['GET'])
def get_policy(id):
    policy = Policy.query.get_or_404(id)
    
    # Get feedback count and sentiment distribution
    feedbacks = PolicyFeedback.query.filter_by(policy_id=id).all()
    
    sentiment_dist = {
        'positive': sum(1 for f in feedbacks if f.sentiment == 'positive'),
        'neutral': sum(1 for f in feedbacks if f.sentiment == 'neutral'),
        'negative': sum(1 for f in feedbacks if f.sentiment == 'negative')
    }
    
    return jsonify({
        'policy': policy.to_dict(),
        'feedback_count': len(feedbacks),
        'sentiment_distribution': sentiment_dist
    })

@bp.route('/', methods=['POST'])
def create_policy():
    data = request.get_json()
    
    policy = Policy(
        title=data['title'],
        description=data['description'],
        category=data.get('category'),
        status=data.get('status', 'Draft'),
        deadline=data.get('deadline')
    )
    
    db.session.add(policy)
    db.session.commit()
    
    return jsonify({
        'message': 'Policy created successfully',
        'policy': policy.to_dict()
    }), 201