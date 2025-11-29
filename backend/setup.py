"""
Setup script for CitizenVoice AI
Run this to initialize the database with sample data
"""

from app import app, db
from models import District, Ministry, Citizen, Policy, UserRole
from datetime import datetime, timedelta

def setup_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Checking for existing data...")
        if District.query.first():
            print("Database already has data. Skipping setup.")
            return
        
        print("Creating sample data...")
        
        # Create districts
        districts = [
            {'name': 'Kampala', 'region': 'Central'},
            {'name': 'Wakiso', 'region': 'Central'},
            {'name': 'Mukono', 'region': 'Central'},
            {'name': 'Jinja', 'region': 'Eastern'},
            {'name': 'Mbale', 'region': 'Eastern'},
            {'name': 'Gulu', 'region': 'Northern'},
            {'name': 'Lira', 'region': 'Northern'},
            {'name': 'Mbarara', 'region': 'Western'},
            {'name': 'Fort Portal', 'region': 'Western'},
            {'name': 'Arua', 'region': 'West Nile'}
        ]
        
        for d in districts:
            district = District(**d)
            db.session.add(district)
        
        # Create ministries
        ministries = [
            {'name': 'Ministry of Health', 'code': 'MOH', 'description': 'Healthcare services and medical facilities', 'contact_email': 'info@health.go.ug'},
            {'name': 'Ministry of Education and Sports', 'code': 'MOES', 'description': 'Education institutions and sports facilities', 'contact_email': 'info@education.go.ug'},
            {'name': 'Ministry of Works and Transport', 'code': 'MOWT', 'description': 'Infrastructure, roads, and transportation', 'contact_email': 'info@works.go.ug'},
            {'name': 'Ministry of Water and Environment', 'code': 'MWE', 'description': 'Water supply and environmental issues', 'contact_email': 'info@water.go.ug'},
            {'name': 'Ministry of Internal Affairs', 'code': 'MIA', 'description': 'Security, police, and internal security', 'contact_email': 'info@internal.go.ug'},
            {'name': 'Ministry of Local Government', 'code': 'MOLG', 'description': 'Local government and community services', 'contact_email': 'info@local.go.ug'},
            {'name': 'Ministry of Agriculture', 'code': 'MAAIF', 'description': 'Agriculture and food security', 'contact_email': 'info@agriculture.go.ug'},
            {'name': 'Ministry of Energy and Mineral Development', 'code': 'MEMD', 'description': 'Energy and electricity services', 'contact_email': 'info@energy.go.ug'}
        ]
        
        for m in ministries:
            ministry = Ministry(**m)
            db.session.add(ministry)
        
        db.session.commit()
        
        # Create admin user
        admin = Citizen(
            nin='CM12345678901234',
            name='System Administrator',
            phone='+256700000001',
            email='admin@citizenvoice.go.ug',
            district_id=1,
            role_id=2,  # Admin role
            is_active=True,
            email_verified=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create sample policies
        moh = Ministry.query.filter_by(code='MOH').first()
        moes = Ministry.query.filter_by(code='MOES').first()
        
        policies = [
            {
                'title': 'Universal Healthcare Coverage Policy 2026',
                'description': 'Proposal to provide comprehensive healthcare coverage to all Ugandan citizens, including free primary healthcare services, subsidized medications, and improved healthcare infrastructure across all districts.',
                'category': 'Healthcare',
                'ministry_id': moh.id if moh else None,
                'status': 'Active',
                'created_by': admin.id,
                'deadline': datetime.utcnow() + timedelta(days=30)
            },
            {
                'title': 'Digital Education Transformation Initiative',
                'description': 'A comprehensive plan to integrate technology in education, providing digital devices to students, training teachers in digital literacy, and establishing e-learning platforms across all schools.',
                'category': 'Education',
                'ministry_id': moes.id if moes else None,
                'status': 'Active',
                'created_by': admin.id,
                'deadline': datetime.utcnow() + timedelta(days=45)
            }
        ]
        
        for p in policies:
            policy = Policy(**p)
            db.session.add(policy)
        
        db.session.commit()
        
        print("✅ Database setup completed successfully!")
        print(f"Admin credentials: NIN=CM12345678901234, Password=admin123")

if __name__ == '__main__':
    setup_database()