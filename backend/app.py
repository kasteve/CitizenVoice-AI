from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
import routes.citizens as citizens_routes
import routes.policies as policies_routes
import routes.feedback as feedback_routes
import routes.ussd as ussd_routes
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
CORS(app)

# Register blueprints
app.register_blueprint(citizens_routes.bp, url_prefix='/api/citizens')
app.register_blueprint(policies_routes.bp, url_prefix='/api/policies')
app.register_blueprint(feedback_routes.bp, url_prefix='/api/feedback')
app.register_blueprint(ussd_routes.bp, url_prefix='/api/ussd')

@app.route('/')
def index():
    return jsonify({
        'message': 'CitizenVoice AI API',
        'version': '1.0',
        'endpoints': {
            'citizens': '/api/citizens',
            'policies': '/api/policies',
            'feedback': '/api/feedback',
            'ussd': '/api/ussd'
        }
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT @@VERSION"))
                print("Connected to SQL Server:", result.fetchone()[0])
        except Exception as e:
            print("DB connection error:", e)
            exit(1)

        db.create_all()

    app.run(debug=True, port=5000)
