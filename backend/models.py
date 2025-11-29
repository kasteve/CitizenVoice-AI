from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class District(db.Model):
    __tablename__ = 'Districts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    region = db.Column(db.String(100))
    chairperson_id = db.Column(db.Integer, db.ForeignKey('Citizens.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'region': self.region,
            'chairperson_id': self.chairperson_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Ministry(db.Model):
    __tablename__ = 'Ministries'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(15))
    minister_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'minister_name': self.minister_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserRole(db.Model):
    __tablename__ = 'UserRoles'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'role_name': self.role_name
        }

class Citizen(db.Model):
    __tablename__ = 'Citizens'
    
    id = db.Column(db.Integer, primary_key=True)
    nin = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('Districts.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('UserRoles.id'), default=1)
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    district = db.relationship('District', foreign_keys=[district_id], backref='citizens')
    role = db.relationship('UserRole', backref='users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nin': self.nin,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'district_id': self.district_id,
            'district_name': self.district.name if self.district else None,
            'role_id': self.role_id,
            'role_name': self.role.role_name if self.role else None,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Policy(db.Model):
    __tablename__ = 'Policies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    ministry_id = db.Column(db.Integer, db.ForeignKey('Ministries.id'))
    status = db.Column(db.String(50), default='Draft')
    created_by = db.Column(db.Integer, db.ForeignKey('Citizens.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    
    ministry = db.relationship('Ministry', backref='policies')
    creator = db.relationship('Citizen', backref='created_policies')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'ministry_id': self.ministry_id,
            'ministry_name': self.ministry.name if self.ministry else None,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }

class PolicyFeedback(db.Model):
    __tablename__ = 'PolicyFeedback'
    
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('Policies.id'))
    citizen_id = db.Column(db.Integer, db.ForeignKey('Citizens.id'))
    feedback_text = db.Column(db.Text)
    sentiment = db.Column(db.String(20))
    themes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    policy = db.relationship('Policy', backref='feedbacks')
    citizen = db.relationship('Citizen', backref='feedbacks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'citizen_id': self.citizen_id,
            'citizen_name': self.citizen.name if self.citizen else None,
            'feedback_text': self.feedback_text,
            'sentiment': self.sentiment,
            'themes': self.themes,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

class Complaint(db.Model):
    __tablename__ = 'Complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.Integer, db.ForeignKey('Citizens.id'))
    ministry_id = db.Column(db.Integer, db.ForeignKey('Ministries.id'))
    district_id = db.Column(db.Integer, db.ForeignKey('Districts.id'))
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    priority = db.Column(db.String(20))
    status = db.Column(db.String(50), default='Pending')
    tracking_number = db.Column(db.String(50), unique=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('Citizens.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    citizen = db.relationship('Citizen', foreign_keys=[citizen_id], backref='complaints')
    ministry = db.relationship('Ministry', backref='complaints')
    district = db.relationship('District', backref='complaints')
    assigned_user = db.relationship('Citizen', foreign_keys=[assigned_to])
    
    def to_dict(self):
        return {
            'id': self.id,
            'citizen_id': self.citizen_id,
            'citizen_name': self.citizen.name if self.citizen else None,
            'ministry_id': self.ministry_id,
            'ministry_name': self.ministry.name if self.ministry else None,
            'district_id': self.district_id,
            'district_name': self.district.name if self.district else None,
            'category': self.category,
            'description': self.description,
            'location': self.location,
            'priority': self.priority,
            'status': self.status,
            'tracking_number': self.tracking_number,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_notes': self.resolution_notes
        }

class ServiceRating(db.Model):
    __tablename__ = 'ServiceRatings'
    
    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.Integer, db.ForeignKey('Citizens.id'))
    service_type = db.Column(db.String(100))
    service_location = db.Column(db.String(200))
    district_id = db.Column(db.Integer, db.ForeignKey('Districts.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    citizen = db.relationship('Citizen', backref='ratings')
    district = db.relationship('District', backref='ratings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'citizen_id': self.citizen_id,
            'service_type': self.service_type,
            'service_location': self.service_location,
            'district_id': self.district_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EmailLog(db.Model):
    __tablename__ = 'EmailLogs'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(100))
    subject = db.Column(db.String(500))
    body = db.Column(db.Text)
    status = db.Column(db.String(50))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text)

class AIPrediction(db.Model):
    __tablename__ = 'AIPredictions'
    
    id = db.Column(db.Integer, primary_key=True)
    prediction_type = db.Column(db.String(100))
    prediction_data = db.Column(db.Text)
    confidence_score = db.Column(db.Float)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prediction_type': self.prediction_type,
            'prediction_data': self.prediction_data,
            'confidence_score': self.confidence_score,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None
        }

class SystemReport(db.Model):
    __tablename__ = 'SystemReports'
    
    id = db.Column(db.Integer, primary_key=True)
    report_title = db.Column(db.String(500))
    report_type = db.Column(db.String(100))
    report_data = db.Column(db.Text)
    generated_by = db.Column(db.Integer, db.ForeignKey('Citizens.id'))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    generator = db.relationship('Citizen', backref='reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_title': self.report_title,
            'report_type': self.report_type,
            'report_data': self.report_data,
            'generated_by': self.generated_by,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }

class USSDSession(db.Model):
    __tablename__ = 'USSDSessions'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    citizen_id = db.Column(db.Integer, db.ForeignKey('Citizens.id'), nullable=True)
    phone_number = db.Column(db.String(15), nullable=False)
    current_menu = db.Column(db.String(100), default='main')
    data = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    citizen = db.relationship('Citizen', backref='ussd_sessions')

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'citizen_id': self.citizen_id,
            'phone_number': self.phone_number,
            'current_menu': self.current_menu,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
