# CitizenVoice AI - Quick Start Guide

## Prerequisites
- Python 3.8+
- SQL Server 2019+
- ODBC Driver 17 for SQL Server

## Installation

### 1. Database Setup
```sql
-- Run the schema.sql file in SQL Server Management Studio
-- Or use sqlcmd:
sqlcmd -S localhost -U sa -P YourPassword123 -i database/schema.sql
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Download TextBlob corpora
python -m textblob.download_corpora

# Update .env file with your database credentials

# Run the application
python app.py
```

### 3. Frontend Setup
```bash
# Simply open frontend/index.html in a browser
# For USSD simulator, open frontend/ussd-simulator.html
```

## Testing

### Web Portal
1. Open `http://localhost:5000` - Should see API info
2. Open `frontend/index.html` in browser
3. Test policy feedback, complaints, and ratings

### USSD Simulator
1. Open `frontend/ussd-simulator.html`
2. Click "Dial *811#"
3. Navigate through menus using numbers
4. Test complaint submission and tracking

## API Endpoints

- GET `/api/policies/` - List all policies
- POST `/api/feedback/policy` - Submit policy feedback
- POST `/api/feedback/complaint` - Submit complaint
- GET `/api/feedback/complaint/<tracking_number>` - Track complaint
- POST `/api/feedback/rating` - Submit service rating
- POST `/api/ussd/simulate` - USSD simulation

## Default Test Data

Create some test policies:
```python
python
>>> from app import app, db
>>> from models import Policy
>>> with app.app_context():
...     policy = Policy(
...         title="Universal Healthcare Policy 2026",
...         description="Proposal to provide free healthcare to all citizens",
...         category="Healthcare",
...         status="Active"
...     )
...     db.session.add(policy)
...     db.session.commit()
```

## Troubleshooting

1. **Database Connection Error**: Check DB credentials in `.env`
2. **CORS Error**: Ensure Flask-CORS is installed
3. **USSD Not Working**: Check backend is running on port 5000

## Demo Flow

1. **Register citizen** via web form
2. **View policies** on homepage
3. **Submit feedback** with AI sentiment analysis
4. **Report complaint** and get tracking number
5. **Track complaint** status
6. **Rate services** with star rating
7. **Test USSD** simulator for mobile experience