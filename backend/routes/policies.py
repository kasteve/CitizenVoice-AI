from flask import Blueprint, request, jsonify
from models import db, Policy, PolicyFeedback
from sqlalchemy import func
from auth import token_required
from datetime import datetime

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
@token_required
def create_policy(current_user):
    """Create policy - Admin only"""
    if current_user.role_id != 2:  # Only admins can create
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    policy = Policy(
        title=data['title'],
        description=data['description'],
        category=data.get('category'),
        ministry_id=data.get('ministry_id'),
        status=data.get('status', 'Draft'),
        created_by=current_user.id
    )
    
    if data.get('deadline'):
        try:
            policy.deadline = datetime.fromisoformat(data['deadline'])
        except:
            policy.deadline = None
    
    if policy.status == 'Active':
        policy.published_at = datetime.utcnow()
    
    db.session.add(policy)
    db.session.commit()
    
    return jsonify({
        'message': 'Policy created successfully',
        'policy': policy.to_dict()
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_policy(current_user, id):
    """Update policy - Admin only"""
    if current_user.role_id != 2:  # Only admins can update
        return jsonify({'error': 'Admin access required'}), 403
    
    policy = Policy.query.get_or_404(id)
    data = request.get_json()
    
    if 'title' in data:
        policy.title = data['title']
    if 'description' in data:
        policy.description = data['description']
    if 'category' in data:
        policy.category = data['category']
    if 'ministry_id' in data:
        policy.ministry_id = data['ministry_id']
    if 'status' in data:
        policy.status = data['status']
        if data['status'] == 'Active' and not policy.published_at:
            policy.published_at = datetime.utcnow()
    if 'deadline' in data:
        if data['deadline']:
            try:
                policy.deadline = datetime.fromisoformat(data['deadline'])
            except:
                policy.deadline = None
        else:
            policy.deadline = None
    
    db.session.commit()
    
    return jsonify({
        'message': 'Policy updated successfully',
        'policy': policy.to_dict()
    }), 200

@bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_policy(current_user, id):
    """Delete policy - Admin only"""
    if current_user.role_id != 2:
        return jsonify({'error': 'Admin access required'}), 403
    
    policy = Policy.query.get_or_404(id)
    
    # Don't allow deletion if there are feedbacks
    feedback_count = PolicyFeedback.query.filter_by(policy_id=id).count()
    if feedback_count > 0:
        return jsonify({'error': 'Cannot delete policy with existing feedback. Consider closing it instead.'}), 400
    
    db.session.delete(policy)
    db.session.commit()
    
    return jsonify({'message': 'Policy deleted successfully'}), 200