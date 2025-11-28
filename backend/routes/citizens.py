from flask import Blueprint, request, jsonify
from models import db, Citizen

bp = Blueprint('citizens', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Check if citizen exists
    existing = Citizen.query.filter_by(phone=data['phone']).first()
    if existing:
        return jsonify({'error': 'Phone number already registered'}), 400
    
    citizen = Citizen(
        name=data['name'],
        phone=data['phone'],
        email=data.get('email'),
        district=data.get('district')
    )
    
    db.session.add(citizen)
    db.session.commit()
    
    return jsonify({
        'message': 'Citizen registered successfully',
        'citizen': citizen.to_dict()
    }), 201

@bp.route('/<int:id>', methods=['GET'])
def get_citizen(id):
    citizen = Citizen.query.get_or_404(id)
    return jsonify(citizen.to_dict())

@bp.route('/phone/<phone>', methods=['GET'])
def get_by_phone(phone):
    citizen = Citizen.query.filter_by(phone=phone).first()
    if not citizen:
        return jsonify({'error': 'Citizen not found'}), 404
    return jsonify(citizen.to_dict())