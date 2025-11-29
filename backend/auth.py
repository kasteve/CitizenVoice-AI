from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from config import Config
from models import Citizen, db

def generate_token(citizen_id, role_id):
    """Generate JWT token"""
    payload = {
        'citizen_id': citizen_id,
        'role_id': role_id,
        'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        current_user = Citizen.query.get(payload['citizen_id'])
        if not current_user or not current_user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        current_user = Citizen.query.get(payload['citizen_id'])
        if not current_user or not current_user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        if current_user.role_id != 2:  # Admin role_id = 2
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin or chairperson role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        current_user = Citizen.query.get(payload['citizen_id'])
        if not current_user or not current_user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        # Allow admin (role 2) and chairperson (role 4)
        if current_user.role_id not in [2, 4]:
            return jsonify({'error': 'Admin or Chairperson access required'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated