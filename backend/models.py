from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Citizen(db.Model):
    __tablename__ = 'Citizens'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100))
    district = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'district': self.district,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Policy(db.Model):
    __tablename__ = 'Policies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    status = db.Column(db.String(50), default='Draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None
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
            'feedback_text': self.feedback_text,
            'sentiment': self.sentiment,
            'themes': self.themes,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }

class Complaint(db.Model):
    __tablename__ = 'Complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.Integer, db.ForeignKey('Citizens.id'))
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    priority = db.Column(db.String(20))
    status = db.Column(db.String(50), default='Pending')
    tracking_number = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    citizen = db.relationship('Citizen', backref='complaints')
    
    def to_dict(self):
        return {
            'id': self.id,
            'citizen_id': self.citizen_id,
            'category': self.category,
            'description': self.description,
            'location': self.location,
            'priority': self.priority,
            'status': self.status,
            'tracking_number': self.tracking_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

class ServiceRating(db.Model):
    __tablename__ = 'ServiceRatings'
    
    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(db.Integer, db.ForeignKey('Citizens.id'))
    service_type = db.Column(db.String(100))
    service_location = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    citizen = db.relationship('Citizen', backref='ratings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'citizen_id': self.citizen_id,
            'service_type': self.service_type,
            'service_location': self.service_location,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class USSDSession(db.Model):
    __tablename__ = 'USSDSessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(15))
    current_menu = db.Column(db.String(50))
    data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)