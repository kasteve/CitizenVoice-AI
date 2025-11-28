from flask import Blueprint, request, jsonify
from models import db, USSDSession, Citizen, Complaint, Policy
from ai.nlp_analyzer import NLPAnalyzer
import json
import uuid

bp = Blueprint('ussd', __name__)
nlp = NLPAnalyzer()

@bp.route('/simulate', methods=['POST'])
def ussd_simulate():
    data = request.get_json()
    session_id = data.get('sessionId', str(uuid.uuid4()))
    phone_number = data.get('phoneNumber')
    text = data.get('text', '')
    
    # Get or create session
    session = USSDSession.query.filter_by(session_id=session_id).first()
    if not session:
        session = USSDSession(
            session_id=session_id,
            phone_number=phone_number,
            current_menu='main',
            data='{}'
        )
        db.session.add(session)
    
    # Parse user input
    inputs = text.split('*') if text else []
    current_input = inputs[-1] if inputs else ''
    
    response = process_ussd_input(session, current_input, phone_number)
    
    db.session.commit()
    
    return jsonify(response)

def process_ussd_input(session, user_input, phone_number):
    session_data = json.loads(session.data) if session.data else {}
    
    # Main menu
    if session.current_menu == 'main':
        if not user_input:
            session.current_menu = 'main'
            return {
                'message': 'CON Welcome to CitizenVoice AI\n1. Submit Complaint\n2. Track Complaint\n3. Rate Service\n4. View Policies\n5. Register',
                'continue': True
            }
        
        if user_input == '1':
            session.current_menu = 'complaint_category'
            return {
                'message': 'CON Select Category:\n1. Infrastructure\n2. Healthcare\n3. Education\n4. Security\n5. Other',
                'continue': True
            }
        elif user_input == '2':
            session.current_menu = 'track_input'
            return {
                'message': 'CON Enter Tracking Number:',
                'continue': True
            }
        elif user_input == '3':
            session.current_menu = 'rating_type'
            return {
                'message': 'CON Rate Service:\n1. Hospital\n2. School\n3. Police Station\n4. Government Office',
                'continue': True
            }
        elif user_input == '4':
            # Show active policies
            policies = Policy.query.filter_by(status='Active').limit(3).all()
            msg = 'CON Active Policies:\n'
            for i, p in enumerate(policies, 1):
                msg += f'{i}. {p.title[:30]}\n'
            return {
                'message': msg,
                'continue': True
            }
        elif user_input == '5':
            session.current_menu = 'register_name'
            return {
                'message': 'CON Enter Your Name:',
                'continue': True
            }
    
    # Complaint flow
    elif session.current_menu == 'complaint_category':
        categories = {
            '1': 'Infrastructure',
            '2': 'Healthcare',
            '3': 'Education',
            '4': 'Security',
            '5': 'Other'
        }
        session_data['complaint_category'] = categories.get(user_input, 'Other')
        session.current_menu = 'complaint_description'
        session.data = json.dumps(session_data)
        return {
            'message': 'CON Describe the issue (be specific):',
            'continue': True
        }
    
    elif session.current_menu == 'complaint_description':
        session_data['complaint_description'] = user_input
        session.current_menu = 'complaint_location'
        session.data = json.dumps(session_data)
        return {
            'message': 'CON Enter Location/District:',
            'continue': True
        }
    
    elif session.current_menu == 'complaint_location':
        session_data['complaint_location'] = user_input
        
        # Get or create citizen
        citizen = Citizen.query.filter_by(phone=phone_number).first()
        if not citizen:
            citizen = Citizen(
                name='USSD User',
                phone=phone_number,
                district=user_input
            )
            db.session.add(citizen)
            db.session.flush()
        
        # Create complaint
        tracking_number = f"CMP-{uuid.uuid4().hex[:8].upper()}"
        priority = nlp.assess_priority(session_data['complaint_description'])
        
        complaint = Complaint(
            citizen_id=citizen.id,
            category=session_data['complaint_category'],
            description=session_data['complaint_description'],
            location=user_input,
            priority=priority,
            tracking_number=tracking_number
        )
        db.session.add(complaint)
        
        session.current_menu = 'main'
        session.data = '{}'
        
        return {
            'message': f'END Complaint submitted!\nTracking #: {tracking_number}\nPriority: {priority}\nSMS sent with details.',
            'continue': False
        }
    
    # Track complaint
    elif session.current_menu == 'track_input':
        complaint = Complaint.query.filter_by(tracking_number=user_input.upper()).first()
        if complaint:
            msg = f'END Complaint Status:\nID: {complaint.tracking_number}\nStatus: {complaint.status}\nCategory: {complaint.category}\nPriority: {complaint.priority}'
        else:
            msg = 'END Tracking number not found.'
        
        session.current_menu = 'main'
        return {
            'message': msg,
            'continue': False
        }
    
    # Rating flow
    elif session.current_menu == 'rating_type':
        services = {
            '1': 'Hospital',
            '2': 'School',
            '3': 'Police Station',
            '4': 'Government Office'
        }
        session_data['service_type'] = services.get(user_input, 'Other')
        session.current_menu = 'rating_location'
        session.data = json.dumps(session_data)
        return {
            'message': 'CON Enter Service Location:',
            'continue': True
        }
    
    elif session.current_menu == 'rating_location':
        session_data['service_location'] = user_input
        session.current_menu = 'rating_score'
        session.data = json.dumps(session_data)
        return {
            'message': 'CON Rate 1-5 (5=Excellent):',
            'continue': True
        }
    
    elif session.current_menu == 'rating_score':
        try:
            rating_value = int(user_input)
            if 1 <= rating_value <= 5:
                citizen = Citizen.query.filter_by(phone=phone_number).first()
                if not citizen:
                    citizen = Citizen(name='USSD User', phone=phone_number)
                    db.session.add(citizen)
                    db.session.flush()
                
                rating = ServiceRating(
                    citizen_id=citizen.id,
                    service_type=session_data['service_type'],
                    service_location=session_data['service_location'],
                    rating=rating_value
                )
                db.session.add(rating)
                
                session.current_menu = 'main'
                session.data = '{}'
                
                return {
                    'message': 'END Thank you for your rating!',
                    'continue': False
                }
        except ValueError:
            pass
        
        return {
            'message': 'END Invalid rating. Please try again.',
            'continue': False
        }
    
    # Registration flow
    elif session.current_menu == 'register_name':
        session_data['name'] = user_input
        session.current_menu = 'register_district'
        session.data = json.dumps(session_data)
        return {
            'message': 'CON Enter Your District:',
            'continue': True
        }
    
    elif session.current_menu == 'register_district':
        citizen = Citizen(
            name=session_data['name'],
            phone=phone_number,
            district=user_input
        )
        db.session.add(citizen)
        
        session.current_menu = 'main'
        session.data = '{}'
        
        return {
            'message': 'END Registration successful! Welcome to CitizenVoice AI.',
            'continue': False
        }
    
    return {
        'message': 'END Invalid input. Please try again.',
        'continue': False
    }