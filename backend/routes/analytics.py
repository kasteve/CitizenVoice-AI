from flask import Blueprint, request, jsonify
from models import db, Complaint, Ministry, District, ServiceRating, PolicyFeedback
from sqlalchemy import func, desc, case
from auth import token_required
from sqlalchemy import extract
from sqlalchemy import case, func, text
from datetime import datetime, timedelta

bp = Blueprint('analytics', __name__)

@bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get overall dashboard statistics - Public endpoint"""
    
    # Total counts
    total_complaints = Complaint.query.count()
    pending_complaints = Complaint.query.filter_by(status='Pending').count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
    in_progress_complaints = Complaint.query.filter_by(status='In Progress').count()
    
    # Complaints by priority
    urgent_complaints = Complaint.query.filter_by(priority='Urgent').count()
    high_complaints = Complaint.query.filter_by(priority='High').count()
    normal_complaints = Complaint.query.filter_by(priority='Normal').count()
    
    # Recent complaints (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_complaints = Complaint.query.filter(
        Complaint.created_at >= thirty_days_ago
    ).count()
    
    # Average rating
    avg_rating = db.session.query(func.avg(ServiceRating.rating)).scalar() or 0
    
    # Total feedback
    total_feedback = PolicyFeedback.query.count()
    
    return jsonify({
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'resolved_complaints': resolved_complaints,
        'in_progress_complaints': in_progress_complaints,
        'urgent_complaints': urgent_complaints,
        'high_complaints': high_complaints,
        'normal_complaints': normal_complaints,
        'recent_complaints': recent_complaints,
        'average_rating': round(float(avg_rating), 2) if avg_rating else 0,
        'total_feedback': total_feedback,
        'resolution_rate': round((resolved_complaints / total_complaints * 100), 2) if total_complaints > 0 else 0
    }), 200

@bp.route('/complaints-by-ministry', methods=['GET'])
def complaints_by_ministry():
    """Get complaint distribution by ministry - Public endpoint"""
    
    results = db.session.query(
        Ministry.name,
        Ministry.code,
        func.count(Complaint.id).label('total'),
        func.sum(case((Complaint.status == 'Pending', 1), else_=0)).label('pending'),
        func.sum(case((Complaint.status == 'In Progress', 1), else_=0)).label('in_progress'),
        func.sum(case((Complaint.status == 'Resolved', 1), else_=0)).label('resolved')
    ).outerjoin(
        Complaint, Ministry.id == Complaint.ministry_id
    ).group_by(
        Ministry.id, Ministry.name, Ministry.code
    ).all()
    
    data = []
    for row in results:
        total = row.total or 0
        resolved = row.resolved or 0
        data.append({
            'ministry': row.name,
            'code': row.code,
            'total': total,
            'pending': row.pending or 0,
            'in_progress': row.in_progress or 0,
            'resolved': resolved,
            'resolution_rate': round((resolved / total * 100), 2) if total > 0 else 0
        })
    
    return jsonify(data), 200

@bp.route('/complaints-by-district', methods=['GET'])
def complaints_by_district():
    """Get complaint distribution by district - Public endpoint"""
    
    results = db.session.query(
        District.name,
        District.region,
        func.count(Complaint.id).label('total'),
        func.sum(case((Complaint.status == 'Pending', 1), else_=0)).label('pending'),
        func.sum(case((Complaint.status == 'Resolved', 1), else_=0)).label('resolved')
    ).outerjoin(
        Complaint, District.id == Complaint.district_id
    ).group_by(
        District.id, District.name, District.region
    ).order_by(
        desc('total')
    ).all()
    
    data = []
    for row in results:
        data.append({
            'district': row.name,
            'region': row.region,
            'total': row.total or 0,
            'pending': row.pending or 0,
            'resolved': row.resolved or 0
        })
    
    return jsonify(data), 200

@bp.route('/complaints-by-category', methods=['GET'])
def complaints_by_category():
    """Get complaint distribution by category - Public endpoint"""
    
    results = db.session.query(
        Complaint.category,
        func.count(Complaint.id).label('count')
    ).group_by(
        Complaint.category
    ).order_by(
        desc('count')
    ).all()
    
    data = [{'category': row.category, 'count': row.count} for row in results]
    
    return jsonify(data), 200

@bp.route('/complaints-timeline', methods=['GET'])
def complaints_timeline():
    """Get complaints over time (last 12 months) - Public endpoint"""
    
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)

    results = db.session.query(
        extract('year', Complaint.created_at).label('year'),
        extract('month', Complaint.created_at).label('month'),
        func.count(Complaint.id).label('count')
    ).filter(
        Complaint.created_at >= twelve_months_ago
    ).group_by(
        extract('year', Complaint.created_at),
        extract('month', Complaint.created_at)
    ).order_by(
        extract('year', Complaint.created_at),
        extract('month', Complaint.created_at)
    ).all()
    
    data = []
    for row in results:
        month_str = f"{int(row.year)}-{int(row.month):02d}"
        data.append({
            'month': month_str,
            'count': row.count
        })
    
    return jsonify(data), 200

@bp.route('/top-issues', methods=['GET'])
def top_issues():
    """Get most common complaint themes/keywords - Public endpoint"""
    
    complaints = Complaint.query.all()
    
    keywords = {}
    common_words = ['the', 'is', 'in', 'at', 'of', 'and', 'a', 'to', 'for', 'on', 'with', 'be', 'this', 'that', 'have', 'has']
    
    for complaint in complaints:
        if complaint.description:
            words = complaint.description.lower().split()
            for word in words:
                word = word.strip('.,!?;:')
                if len(word) > 3 and word not in common_words:
                    keywords[word] = keywords.get(word, 0) + 1
    
    # Get top 10
    top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
    
    data = [{'keyword': k, 'count': v} for k, v in top_keywords]
    
    return jsonify(data), 200

@bp.route('/ministry-performance', methods=['GET'])
def ministry_performance():
    """Get ministry performance metrics - Public endpoint"""

    results = db.session.query(
        Ministry.name,
        func.count(Complaint.id).label('total_complaints'),
        func.sum(
            case((Complaint.status == 'Resolved', 1), else_=0)
        ).label('resolved'),
        func.avg(
            case(
                (Complaint.resolved_at.isnot(None),
                 func.datediff(text("day"), Complaint.created_at, Complaint.resolved_at)),
                else_=None
            )
        ).label('avg_resolution_days')
    ).outerjoin(
        Complaint, Ministry.id == Complaint.ministry_id
    ).group_by(
        Ministry.id, Ministry.name
    ).all()

    data = []
    for row in results:
        total = row.total_complaints or 0
        resolved = row.resolved or 0
        
        data.append({
            'ministry': row.name,
            'total_complaints': total,
            'resolved': resolved,
            'avg_resolution_days': round(float(row.avg_resolution_days), 1) if row.avg_resolution_days else 0,
            'resolution_rate': round((resolved / total * 100), 2) if total > 0 else 0
        })

    return jsonify(data), 200

@bp.route('/service-ratings-summary', methods=['GET'])
def service_ratings_summary():
    """Get service ratings summary - Public endpoint"""
    
    results = db.session.query(
        ServiceRating.service_type,
        func.avg(ServiceRating.rating).label('avg_rating'),
        func.count(ServiceRating.id).label('total_ratings')
    ).group_by(
        ServiceRating.service_type
    ).all()
    
    data = []
    for row in results:
        data.append({
            'service_type': row.service_type,
            'avg_rating': round(float(row.avg_rating), 2),
            'total_ratings': row.total_ratings
        })
    
    return jsonify(data), 200

@bp.route('/unresolved-by-ministry', methods=['GET'])
def unresolved_by_ministry():
    """Get ministries with highest unresolved complaints - Public endpoint"""
    
    results = db.session.query(
        Ministry.name,
        func.count(Complaint.id).label('unresolved_count')
    ).join(
        Complaint, Ministry.id == Complaint.ministry_id
    ).filter(
        Complaint.status != 'Resolved'
    ).group_by(
        Ministry.id, Ministry.name
    ).order_by(
        desc('unresolved_count')
    ).limit(10).all()
    
    data = [{'ministry': row.name, 'unresolved_count': row.unresolved_count} for row in results]
    
    return jsonify(data), 200

@bp.route('/generate-report', methods=['POST'])
@token_required
def generate_report_endpoint(current_user):
    """Generate comprehensive system report"""
    from ai.report_generator import ReportGenerator
    
    try:
        report = ReportGenerator.generate_system_report(current_user.id)
        return jsonify({
            'message': 'Report generated successfully',
            'report': report
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500