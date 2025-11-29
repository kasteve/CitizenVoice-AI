from flask_mail import Mail, Message
from models import db, EmailLog
from datetime import datetime

mail = Mail()

def send_email(recipient, subject, body_text, body_html=None):
    """Send email and log the attempt"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body_text,
            html=body_html or body_text
        )
        
        mail.send(msg)
        
        # Log success
        log = EmailLog(
            recipient_email=recipient,
            subject=subject,
            body=body_text,
            status='Sent'
        )
        db.session.add(log)
        db.session.commit()
        
        return True
    except Exception as e:
        # Log failure
        log = EmailLog(
            recipient_email=recipient,
            subject=subject,
            body=body_text,
            status='Failed',
            error_message=str(e)
        )
        db.session.add(log)
        db.session.commit()
        
        return False

def send_complaint_confirmation(citizen_email, citizen_name, tracking_number, category, priority):
    """Send complaint confirmation email"""
    subject = f"Complaint Submitted - {tracking_number}"
    
    body_text = f"""
Dear {citizen_name},

Your complaint has been successfully submitted to CitizenVoice AI.

Complaint Details:
- Tracking Number: {tracking_number}
- Category: {category}
- Priority: {priority}
- Status: Pending Review

You can track your complaint status at any time using your tracking number.

Thank you for your participation in improving governance.

Best regards,
CitizenVoice AI Team
"""
    
    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: white; padding: 30px; border: 1px solid #ddd; }}
        .tracking {{ background: #f0f0f0; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0; }}
        .footer {{ background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗳️ CitizenVoice AI</h1>
            <p>Complaint Confirmation</p>
        </div>
        <div class="content">
            <h2>Dear {citizen_name},</h2>
            <p>Your complaint has been successfully submitted to CitizenVoice AI.</p>
            
            <div class="tracking">
                <h3>Complaint Details:</h3>
                <p><strong>Tracking Number:</strong> {tracking_number}</p>
                <p><strong>Category:</strong> {category}</p>
                <p><strong>Priority:</strong> {priority}</p>
                <p><strong>Status:</strong> Pending Review</p>
            </div>
            
            <p>You can track your complaint status at any time using your tracking number.</p>
            <p>Thank you for your participation in improving governance.</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 CitizenVoice AI | National AI Hackathon</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(citizen_email, subject, body_text, body_html)

def send_welcome_email(citizen_email, citizen_name):
    """Send welcome email after registration"""
    subject = "Welcome to CitizenVoice AI"
    
    body_text = f"""
Dear {citizen_name},

Welcome to CitizenVoice AI - Uganda's Participatory Governance Platform!

Your account has been successfully created. You can now:
- Participate in policy consultations
- Submit and track complaints
- Rate government services
- View analytics and insights

Login to get started: http://localhost:5000/login.html

Thank you for joining us in transforming governance.

Best regards,
CitizenVoice AI Team
"""
    
    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: white; padding: 30px; border: 1px solid #ddd; }}
        .features {{ background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗳️ Welcome to CitizenVoice AI</h1>
            <p>Empowering Citizens, Transforming Governance</p>
        </div>
        <div class="content">
            <h2>Dear {citizen_name},</h2>
            <p>Your account has been successfully created!</p>
            
            <div class="features">
                <h3>What you can do:</h3>
                <ul>
                    <li>✅ Participate in policy consultations</li>
                    <li>✅ Submit and track complaints</li>
                    <li>✅ Rate government services</li>
                    <li>✅ View analytics and insights</li>
                </ul>
            </div>
            
            <center>
                <a href="http://localhost:5000/login.html" class="button">Login to Get Started</a>
            </center>
            
            <p>Thank you for joining us in transforming governance!</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 CitizenVoice AI | National AI Hackathon</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(citizen_email, subject, body_text, body_html)
