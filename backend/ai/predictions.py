from models import Complaint, Ministry, District, db
from sqlalchemy import func
from datetime import datetime, timedelta
import json

class PredictiveAnalytics:
    
    @staticmethod
    def predict_complaint_trends():
        """Predict complaint trends for next month"""
        
        # Get last 6 months of data
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        monthly_counts = db.session.query(
            func.date_trunc('month', Complaint.created_at).label('month'),
            func.count(Complaint.id).label('count')
        ).filter(
            Complaint.created_at >= six_months_ago
        ).group_by('month').order_by('month').all()
        
        if len(monthly_counts) < 3:
            return {
                'prediction': 'Insufficient data',
                'confidence': 0,
                'trend': 'unknown'
            }
        
        # Simple linear trend calculation
        counts = [row.count for row in monthly_counts]
        avg_change = (counts[-1] - counts[0]) / len(counts)
        
        predicted_next_month = counts[-1] + avg_change
        
        if avg_change > 0:
            trend = 'increasing'
            confidence = min(abs(avg_change) / counts[-1] * 100, 95)
        elif avg_change < 0:
            trend = 'decreasing'
            confidence = min(abs(avg_change) / counts[-1] * 100, 95)
        else:
            trend = 'stable'
            confidence = 80
        
        return {
            'predicted_complaints': max(0, int(predicted_next_month)),
            'current_month': counts[-1],
            'trend': trend,
            'confidence': round(confidence, 2),
            'average_change': round(avg_change, 2)
        }
    
    @staticmethod
    def identify_high_risk_areas():
        """Identify districts with high complaint rates"""
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        results = db.session.query(
            District.name,
            District.region,
            func.count(Complaint.id).label('recent_complaints'),
            func.sum(func.case((Complaint.priority == 'Urgent', 1), else_=0)).label('urgent_count')
        ).join(
            Complaint, District.id == Complaint.district_id
        ).filter(
            Complaint.created_at >= thirty_days_ago
        ).group_by(
            District.id, District.name, District.region
        ).order_by(
            func.count(Complaint.id).desc()
        ).limit(10).all()
        
        high_risk = []
        for row in results:
            risk_score = row.recent_complaints + (row.urgent_count * 2)
            high_risk.append({
                'district': row.name,
                'region': row.region,
                'recent_complaints': row.recent_complaints,
                'urgent_complaints': row.urgent_count,
                'risk_score': risk_score,
                'risk_level': 'High' if risk_score > 50 else 'Medium' if risk_score > 20 else 'Low'
            })
        
        return high_risk
    
    @staticmethod
    def predict_resolution_time(complaint_id):
        """Predict resolution time for a complaint"""
        
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return None
        
        # Get average resolution time for similar complaints
        similar_resolved = db.session.query(
            func.avg(
                func.extract('epoch', Complaint.resolved_at - Complaint.created_at)
            ).label('avg_seconds')
        ).filter(
            Complaint.category == complaint.category,
            Complaint.ministry_id == complaint.ministry_id,
            Complaint.resolved_at.isnot(None)
        ).scalar()
        
        if not similar_resolved:
            # Default estimates by priority
            estimates = {
                'Urgent': 3,
                'High': 7,
                'Normal': 14
            }
            estimated_days = estimates.get(complaint.priority, 14)
        else:
            estimated_days = similar_resolved / 86400  # Convert seconds to days
        
        return {
            'estimated_days': round(estimated_days, 1),
            'priority': complaint.priority,
            'category': complaint.category
        }
    
    @staticmethod
    def identify_systemic_issues():
        """Identify recurring systemic issues"""
        
        # Get complaints with similar descriptions/keywords
        complaints = Complaint.query.filter(
            Complaint.status != 'Resolved'
        ).all()
        
        issue_clusters = {}
        
        for complaint in complaints:
            if complaint.description:
                words = set(complaint.description.lower().split())
                
                # Look for matches with existing clusters
                matched = False
                for key, cluster in issue_clusters.items():
                    cluster_words = set(key.split('_'))
                    overlap = len(words & cluster_words)
                    
                    if overlap >= 2:  # At least 2 common words
                        cluster['count'] += 1
                        cluster['complaints'].append(complaint.id)
                        matched = True
                        break
                
                if not matched and len(words) >= 3:
                    # Create new cluster with significant words
                    key_words = sorted(list(words))[:3]
                    key = '_'.join(key_words)
                    issue_clusters[key] = {
                        'count': 1,
                        'complaints': [complaint.id],
                        'category': complaint.category
                    }
        
        # Filter clusters with multiple complaints
        systemic_issues = []
        for key, cluster in issue_clusters.items():
            if cluster['count'] >= 3:  # At least 3 similar complaints
                systemic_issues.append({
                    'issue_keywords': key.replace('_', ', '),
                    'complaint_count': cluster['count'],
                    'category': cluster['category'],
                    'severity': 'High' if cluster['count'] >= 10 else 'Medium'
                })
        
        return sorted(systemic_issues, key=lambda x: x['complaint_count'], reverse=True)
    
    @staticmethod
    def ministry_workload_forecast():
        """Forecast ministry workload for next month"""
        
        forecasts = []
        ministries = Ministry.query.all()
        
        for ministry in ministries:
            # Get last 3 months average
            three_months_ago = datetime.utcnow() - timedelta(days=90)
            
            recent_avg = db.session.query(
                func.count(Complaint.id)
            ).filter(
                Complaint.ministry_id == ministry.id,
                Complaint.created_at >= three_months_ago
            ).scalar() / 3
            
            # Current pending
            pending = Complaint.query.filter_by(
                ministry_id=ministry.id,
                status='Pending'
            ).count()
            
            # Forecast
            forecasted_new = int(recent_avg * 1.1)  # 10% buffer
            expected_workload = pending + forecasted_new
            
            forecasts.append({
                'ministry': ministry.name,
                'current_pending': pending,
                'forecasted_new_complaints': forecasted_new,
                'expected_total_workload': expected_workload,
                'capacity_status': 'Overloaded' if expected_workload > 100 else 'Normal'
})
            return sorted(forecasts, key=lambda x: x['expected_total_workload'], reverse=True)