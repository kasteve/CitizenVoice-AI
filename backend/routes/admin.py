from flask import Blueprint, request, jsonify
from models import db, District, Ministry, Citizen, Complaint, SystemReport, AIPrediction
from auth import admin_required
from datetime import datetime

bp = Blueprint('admin', __name__)

@bp.route('/districts', methods=['GET'])
@admin_required
def get_districts(current_user):
    """Get all districts"""
    districts = District.query.all()
    return jsonify([d.to_dict() for d in districts]), 200

@bp.route('/districts', methods=['POST'])
@admin_required
def create_district(current_user):
    """Create new district"""
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({'error': 'District name required'}), 400
    
    # Check if district already exists
    if District.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'District already exists'}), 400
    
    district = District(
        name=data['name'],
        region=data.get('region')
    )
    
    db.session.add(district)
    db.session.commit()
    
    return jsonify({
        'message': 'District created successfully',
        'district': district.to_dict()
    }), 201

@bp.route('/districts/<int:id>', methods=['PUT'])
@admin_required
def update_district(current_user, id):
    """Update district"""
    district = District.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        district.name = data['name']
    if 'region' in data:
        district.region = data['region']
    if 'chairperson_id' in data:
        # Validate chairperson exists and has correct role
        chairperson = Citizen.query.get(data['chairperson_id'])
        if not chairperson:
            return jsonify({'error': 'Chairperson not found'}), 404
        if chairperson.role_id != 4:  # Chairperson role
            return jsonify({'error': 'User must have Chairperson role'}), 400
        district.chairperson_id = data['chairperson_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'District updated successfully',
        'district': district.to_dict()
    }), 200

@bp.route('/ministries', methods=['GET'])
@admin_required
def get_ministries(current_user):
    """Get all ministries"""
    ministries = Ministry.query.all()
    return jsonify([m.to_dict() for m in ministries]), 200

@bp.route('/ministries', methods=['POST'])
@admin_required
def create_ministry(current_user):
    """Create new ministry"""
    data = request.get_json()
    
    required_fields = ['name', 'code']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if ministry already exists
    if Ministry.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Ministry already exists'}), 400
    
    if Ministry.query.filter_by(code=data['code']).first():
        return jsonify({'error': 'Ministry code already exists'}), 400
    
    ministry = Ministry(
        name=data['name'],
        code=data['code'],
        description=data.get('description'),
        contact_email=data.get('contact_email'),
        contact_phone=data.get('contact_phone'),
        minister_name=data.get('minister_name')
    )
    
    db.session.add(ministry)
    db.session.commit()
    
    return jsonify({
        'message': 'Ministry created successfully',
        'ministry': ministry.to_dict()
    }), 201

@bp.route('/ministries/<int:id>', methods=['PUT'])
@admin_required
def update_ministry(current_user, id):
    """Update ministry"""
    ministry = Ministry.query.get_or_404(id)
    data = request.get_json()
    
    updateable_fields = ['name', 'code', 'description', 'contact_email', 'contact_phone', 'minister_name']
    for field in updateable_fields:
        if field in data:
            setattr(ministry, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Ministry updated successfully',
        'ministry': ministry.to_dict()
    }), 200

@bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user):
    """Get all users"""
    role_filter = request.args.get('role')
    
    query = Citizen.query
    if role_filter:
        query = query.filter_by(role_id=int(role_filter))
    
    users = query.all()
    return jsonify([u.to_dict() for u in users]), 200

@bp.route('/users/<int:id>/role', methods=['PUT'])
@admin_required
def update_user_role(current_user, id):
    """Update user role"""
    user = Citizen.query.get_or_404(id)
    data = request.get_json()
    
    if 'role_id' not in data:
        return jsonify({'error': 'role_id required'}), 400
    
    if data['role_id'] not in [1, 2, 3, 4]:
        return jsonify({'error': 'Invalid role_id'}), 400
    
    user.role_id = data['role_id']
    db.session.commit()
    
    return jsonify({
        'message': 'User role updated successfully',
        'user': user.to_dict()
    }), 200

@bp.route('/complaints/<int:id>/assign', methods=['PUT'])
@admin_required
def assign_complaint(current_user, id):
    """Assign complaint to ministry and update status"""
    complaint = Complaint.query.get_or_404(id)
    data = request.get_json()
    
    if 'ministry_id' in data:
        ministry = Ministry.query.get(data['ministry_id'])
        if not ministry:
            return jsonify({'error': 'Ministry not found'}), 404
        complaint.ministry_id = data['ministry_id']
    
    if 'status' in data:
        complaint.status = data['status']
    
    if 'assigned_to' in data:
        assignee = Citizen.query.get(data['assigned_to'])
        if not assignee:
            return jsonify({'error': 'Assignee not found'}), 404
        complaint.assigned_to = data['assigned_to']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Complaint updated successfully',
        'complaint': complaint.to_dict()
    }), 200

@bp.route('/complaints', methods=['GET'])
@admin_required
def get_all_complaints(current_user):
    """Get all complaints for admin/chairperson"""
    status_filter = request.args.get('status')
    
    query = Complaint.query
    
    # If chairperson, only show complaints from their district
    if current_user.role_id == 4:  # Chairperson
        query = query.filter_by(district_id=current_user.district_id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    complaints = query.order_by(Complaint.created_at.desc()).all()
    return jsonify([c.to_dict() for c in complaints]), 200

@bp.route('/complaints/<int:id>/assign', methods=['PUT'])
@admin_required
def update_complaint_status(current_user, id):
    """Update complaint status and assignment"""
    complaint = Complaint.query.get_or_404(id)
    data = request.get_json()
    
    # Chairpersons can only update complaints in their district
    if current_user.role_id == 4 and complaint.district_id != current_user.district_id:
        return jsonify({'error': 'You can only manage complaints in your district'}), 403
    
    if 'ministry_id' in data and data['ministry_id']:
        complaint.ministry_id = data['ministry_id']
    
    if 'status' in data:
        complaint.status = data['status']
        
        if data['status'] == 'Resolved':
            complaint.resolved_at = datetime.utcnow()
            if 'resolution_notes' in data:
                complaint.resolution_notes = data['resolution_notes']
    
    if 'assigned_to' in data:
        complaint.assigned_to = data['assigned_to']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Complaint updated successfully',
        'complaint': complaint.to_dict()
    }), 200

@bp.route('/reports', methods=['GET'])
@admin_required
def get_reports(current_user):
    """Get all system reports"""
    reports = SystemReport.query.order_by(SystemReport.generated_at.desc()).all()
    return jsonify([r.to_dict() for r in reports]), 200

@bp.route('/reports/<int:id>', methods=['GET'])
@admin_required
def get_report(current_user, id):
    """Get specific report"""
    report = SystemReport.query.get_or_404(id)
    return jsonify(report.to_dict()), 200