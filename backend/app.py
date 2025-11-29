from flask import Flask, jsonify
from flask_cors import CORS
from flask_mail import Mail
from config import Config
from models import db
from email_service import mail
import routes.auth_routes as auth_routes
import routes.citizens as citizens_routes
import routes.policies as policies_routes
import routes.feedback as feedback_routes
import routes.ussd as ussd_routes
import routes.admin as admin_routes
import routes.analytics as analytics_routes

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
CORS(app)
mail.init_app(app)

# Register blueprints
app.register_blueprint(auth_routes.bp, url_prefix='/api/auth')
app.register_blueprint(citizens_routes.bp, url_prefix='/api/citizens')
app.register_blueprint(policies_routes.bp, url_prefix='/api/policies')
app.register_blueprint(feedback_routes.bp, url_prefix='/api/feedback')
app.register_blueprint(ussd_routes.bp, url_prefix='/api/ussd')
app.register_blueprint(admin_routes.bp, url_prefix='/api/admin')
app.register_blueprint(analytics_routes.bp, url_prefix='/api/analytics')

@app.route('/')
def index():
    return jsonify({
        'message': 'CitizenVoice AI API',
        'version': '2.0',
        'features': [
            'User Authentication',
            'Policy Management',
            'Complaint Tracking',
            'Analytics Dashboard',
            'AI Predictions',
            'Email Notifications',
            'USSD Interface'
        ],
        'endpoints': {
            'auth': '/api/auth',
            'citizens': '/api/citizens',
            'policies': '/api/policies',
            'feedback': '/api/feedback',
            'analytics': '/api/analytics',
            'admin': '/api/admin',
            'ussd': '/api/ussd'
        }
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'services': ['api', 'email', 'analytics']
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
        print("Starting CitizenVoice AI Server...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)