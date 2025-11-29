# CitizenVoice AI - Participatory Governance Platform

## Overview
CitizenVoice AI is an intelligent platform that transforms governance through AI-powered policy co-creation, complaint management, and data-driven insights. Built for the National AI Hackathon 2026.

## Features

### Core Functionality
- ✅ **User Authentication**: Secure NIN-based registration and login
- ✅ **Policy Management**: Citizens can view and provide feedback on active policies
- ✅ **Complaint System**: Submit, track, and manage complaints with AI categorization
- ✅ **Service Ratings**: Rate government services with sentiment analysis
- ✅ **Analytics Dashboard**: Interactive charts showing complaint trends, ministry performance
- ✅ **Email Notifications**: Automatic email confirmations for complaints
- ✅ **USSD Interface**: Mobile-friendly USSD simulator for feature phones
- ✅ **AI Predictions**: Machine learning-based trend forecasting and insights

### Admin Features
- District management
- Ministry management
- User role assignment
- Complaint assignment to ministries
- System reports generation

### AI Capabilities
- Sentiment analysis on feedback
- Automatic complaint categorization
- Priority assessment
- Theme extraction
- Predictive analytics
- Systemic issue identification

## Installation

### Prerequisites
```bash
- Python 3.8+
- SQL Server 2019+
- ODBC Driver 17 for SQL Server
```

### Step 1: Database Setup
```sql
-- Run in SQL Server Management Studio
sqlcmd -S localhost -U sa -P YourPassword -i database/schema.sql
```

### Step 2: Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Download TextBlob corpora
python -m textblob.download_corpora

# Configure environment
cp .env.example .env
# Edit .env with your database and email credentials

# Initialize database
python setup.py

# Run server
python app.py
```

### Step 3: Frontend Setup
```bash
run this command in the frontend path  python -m http.server 8000
and access the ui http://127.0.0.1:8000/login.html
# Simply open frontend files in browser
# Main app: http://localhost:5000
# Login: frontend/login.html
# USSD Simulator: frontend/ussd-simulator.html
```

## Usage

### For Citizens
1. **Register**: Visit `login.html` → Click "Register" → Fill in NIN, name, phone, email, district
2. **Login**: Use your NIN and password
3. **Submit Complaint**: Dashboard → "Submit Complaint" → Fill form → Get tracking number via email
4. **Track Complaint**: Enter tracking number to see status
5. **Provide Feedback**: View policies → Click policy → Submit feedback
6. **View Analytics**: Access analytics dashboard for insights

### For Administrators
1. Login with admin credentials (NIN: CM12345678901234, Password: admin123)
2. Access admin panel
3. Manage districts, ministries, users
4. Assign complaints to ministries
5. Generate AI-powered reports

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/verify-token` - Verify JWT token

### Policies
- `GET /api/policies/` - List all policies
- `GET /api/policies/<id>` - Get policy details
- `POST /api/policies/` - Create policy (admin)

### Complaints
- `POST /api/feedback/complaint` - Submit complaint
- `GET /api/feedback/complaint/<tracking_number>` - Track complaint
- `GET /api/feedback/complaint/user/<user_id>` - Get user complaints

### Analytics
- `GET /api/analytics/dashboard` - Dashboard stats
- `GET /api/analytics/complaints-by-ministry` - Ministry distribution
- `GET /api/analytics/complaints-by-district` - District distribution
- `GET /api/analytics/ministry-performance` - Performance metrics

### Admin
- `GET /api/admin/districts` - List districts
- `POST /api/admin/districts` - Create district
- `GET /api/admin/ministries` - List ministries
- `POST /api/admin/ministries` - Create ministry

## Technology
Stack
Backend

Flask (Python web framework)
SQL Server (Database)
SQLAlchemy (ORM)
Flask-Mail (Email)
JWT (Authentication)
TextBlob (NLP/Sentiment Analysis)

Frontend

HTML5/CSS3/JavaScript
Chart.js (Data visualization)
Responsive design

AI/ML

Natural Language Processing for sentiment analysis
Keyword extraction for theme identification
Predictive analytics for trend forecasting
Pattern recognition for systemic issues

Project Structure
citizenvoice-ai/
├── backend/
│   ├── app.py                 # Main application
│   ├── models.py              # Database models
│   ├── config.py              # Configuration
│   ├── auth.py                # Authentication middleware
│   ├── email_service.py       # Email handling
│   ├── routes/                # API endpoints
│   └── ai/                    # AI modules
├── frontend/
│   ├── login.html             # Login page
│   ├── register.html          # Registration
│   ├── dashboard.html         # User dashboard
│   ├── policies.html          # Policy viewing
│   ├── complaints.html        # Complaint management
│   ├── analytics.html         # Analytics dashboard
│   ├── ussd-simulator.html    # USSD interface
│   ├── css/                   # Stylesheets
│   └── js/                    # JavaScript files
└── database/
    └── schema.sql             # Database schema
Demo Credentials

Admin: NIN: CM12345678901234, Password: admin123
Citizen: Register your own account

Email Configuration (Gmail)

Enable 2FA on your Google account
Generate an "App Password" from Google Account settings
Use App Password in .env file

Features Demo
USSD Simulator

Open ussd-simulator.html
Enter phone number
Dial *811#
Navigate menus to submit complaints, track status, rate services

Analytics Dashboard

View real-time statistics
Interactive charts for complaint distribution
Ministry performance metrics
District-wise analysis
Trend forecasting

Troubleshooting
Database Connection Error
bash# Check SQL Server is running
# Verify credentials in .env
# Ensure ODBC Driver 17 is installed
Email Not Sending
bash# Verify Gmail App Password
# Check MAIL_USE_TLS=True
# Ensure less secure app access is enabled (if not using App Password)
CORS Error
bash# Ensure Flask-CORS is installed
# Check API_BASE_URL in frontend JavaScript files
Contributing
This project was built for the National AI Hackathon 2026. For improvements or issues, please contact the development team.
License
MIT License - Built for educational and governance improvement purposes.
Contact

Project: CitizenVoice AI
Event: National AI Hackathon 2026
Theme: Governance, Public Policy and Political Stability

