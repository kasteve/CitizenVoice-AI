from flask import Blueprint, request, jsonify
from models import db, Citizen, District
from auth import generate_token
from email_service import send_welcome_email
from datetime import datetime

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['nin', 'name', 'phone', 'email', 'password', 'district_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if NIN already exists
    if Citizen.query.filter_by(nin=data['nin']).first():
        return jsonify({'error': 'NIN already registered'}), 400
    
    # Check if phone already exists
    if Citizen.query.filter_by(phone=data['phone']).first():
        return jsonify({'error': 'Phone number already registered'}), 400
    
    # Check if email already exists
    if Citizen.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Validate district
    district = District.query.get(data['district_id'])
    if not district:
        return jsonify({'error': 'Invalid district'}), 400
    
    # Create new citizen
    citizen = Citizen(
        nin=data['nin'],
        name=data['name'],
        phone=data['phone'],
        email=data['email'],
        district_id=data['district_id'],
        role_id=1  # Default to Citizen role
    )
    citizen.set_password(data['password'])
    
    db.session.add(citizen)
    db.session.commit()
    
    # Send welcome email
    send_welcome_email(citizen.email, citizen.name)
    
    # Generate token
    token = generate_token(citizen.id, citizen.role_id)
    
    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': citizen.to_dict()
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate required fields
    if 'nin' not in data or 'password' not in data:
        return jsonify({'error': 'NIN and password required'}), 400
    
    # Find citizen by NIN
    citizen = Citizen.query.filter_by(nin=data['nin']).first()
    
    if not citizen or not citizen.check_password(data['password']):
        return jsonify({'error': 'Invalid NIN or password'}), 401
    
    if not citizen.is_active:
        return jsonify({'error': 'Account is inactive'}), 401
    
    # Update last login
    citizen.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate token
    token = generate_token(citizen.id, citizen.role_id)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': citizen.to_dict()
    }), 200

@bp.route('/verify-token', methods=['POST'])
def verify_token():
    from auth import decode_token
    
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({'valid': False}), 400
    
    payload = decode_token(token)
    if not payload:
        return jsonify({'valid': False}), 401
    
    citizen = Citizen.query.get(payload['citizen_id'])
    if not citizen or not citizen.is_active:
        return jsonify({'valid': False}), 401
    
    return jsonify({
        'valid': True,
        'user': citizen.to_dict()
    }), 200