from models import Complaint, Ministry, District, db, PolicyFeedback
from sqlalchemy import func
from datetime import datetime, timedelta
import json
from sqlalchemy import case
import statistics

class PredictiveAnalytics:
    
    @staticmethod
    def predict_complaint_trends():
        """Predict complaint trends for next month with improved algorithm"""
        
        # Get last 6 months of data
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        monthly_counts = db.session.query(
        func.datepart(db.text('year'), Complaint.created_at).label('year'),
        func.datepart(db.text('month'), Complaint.created_at).label('month'),
        func.count(Complaint.id).label('count')
        ).filter(
        Complaint.created_at >= six_months_ago
        ).group_by(
        func.datepart(db.text('year'), Complaint.created_at),
        func.datepart(db.text('month'), Complaint.created_at)
        ).order_by(
        db.text('year'), db.text('month')
        ).all()
        
        if len(monthly_counts) < 3:
            return {
                'prediction': 'Insufficient data for prediction',
                'confidence': 0,
                'trend': 'unknown',
                'message': 'Need at least 3 months of data for trend analysis'
            }
        
        # Calculate trend using linear regression approximation
        counts = [row.count for row in monthly_counts]
        n = len(counts)
        
        # Simple moving average for smoothing
        if n >= 3:
            recent_avg = sum(counts[-3:]) / 3
            older_avg = sum(counts[:3]) / 3
        else:
            recent_avg = counts[-1]
            older_avg = counts[0]
        
        # Calculate trend
        avg_change = (recent_avg - older_avg) / n
        predicted_next_month = int(counts[-1] + avg_change)
        
        # Determine trend direction and confidence
        if avg_change > 5:
            trend = 'increasing'
            confidence = min(85 + (avg_change * 2), 95)
            warning = "⚠️ Significant increase expected. Consider resource allocation."
        elif avg_change > 0:
            trend = 'slightly increasing'
            confidence = min(70 + (avg_change * 3), 85)
            warning = "📈 Moderate increase expected."
        elif avg_change < -5:
            trend = 'decreasing'
            confidence = min(85 + (abs(avg_change) * 2), 95)
            warning = "✅ Positive trend: complaints decreasing."
        elif avg_change < 0:
            trend = 'slightly decreasing'
            confidence = min(70 + (abs(avg_change) * 3), 85)
            warning = "📉 Minor decrease expected."
        else:
            trend = 'stable'
            confidence = 80
            warning = "➡️ Complaint volume expected to remain stable."
        
        return {
            'predicted_complaints': max(0, predicted_next_month),
            'current_month': counts[-1],
            'previous_month': counts[-2] if len(counts) > 1 else counts[-1],
            'trend': trend,
            'confidence': round(confidence, 2),
            'average_change': round(avg_change, 2),
            'warning': warning,
            'historical_data': counts
        }
    
    @staticmethod
    def identify_high_risk_areas():
        """Identify districts with high complaint rates with risk scoring"""
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        results = db.session.query(
        District.name,
        District.region,
        func.count(Complaint.id).label('recent_complaints'),
        func.sum(
            case(
                (Complaint.priority == 'Urgent', 1),
                else_=0
            )
        ).label('urgent_count'),
        func.sum(
            case(
                (Complaint.status == 'Pending', 1),
                else_=0
            )
        ).label('pending_count')
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
            # Enhanced risk scoring algorithm
            base_score = row.recent_complaints
            urgent_multiplier = row.urgent_count * 3
            pending_penalty = row.pending_count * 1.5
            
            risk_score = base_score + urgent_multiplier + pending_penalty
            
            # Determine risk level
            if risk_score > 100:
                risk_level = 'Critical'
                action = 'Immediate intervention required'
            elif risk_score > 50:
                risk_level = 'High'
                action = 'Priority attention needed'
            elif risk_score > 20:
                risk_level = 'Medium'
                action = 'Monitor closely'
            else:
                risk_level = 'Low'
                action = 'Routine monitoring'
            
            high_risk.append({
                'district': row.name,
                'region': row.region,
                'recent_complaints': row.recent_complaints,
                'urgent_complaints': row.urgent_count,
                'pending_complaints': row.pending_count,
                'risk_score': int(risk_score),
                'risk_level': risk_level,
                'recommended_action': action
            })
        
        return high_risk
    
    @staticmethod
    def predict_resolution_time(complaint_id):
        """Predict resolution time for a complaint with ML-like approach"""
        
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return None
        
        # Get historical data for similar complaints
        similar_resolved = db.session.query(
            func.avg(
                func.datediff('day', Complaint.created_at, Complaint.resolved_at)
            ).label('avg_days'),
            func.count(Complaint.id).label('count')
        ).filter(
            Complaint.category == complaint.category,
            Complaint.priority == complaint.priority,
            Complaint.resolved_at.isnot(None)
        ).first()
        
        if similar_resolved and similar_resolved.avg_days:
            estimated_days = similar_resolved.avg_days
            confidence = min(60 + (similar_resolved.count * 2), 90)
        else:
            # Default estimates by priority
            estimates = {
                'Urgent': 3,
                'High': 7,
                'Normal': 14
            }
            estimated_days = estimates.get(complaint.priority, 14)
            confidence = 50
        
        return {
            'estimated_days': round(estimated_days, 1),
            'priority': complaint.priority,
            'category': complaint.category,
            'confidence': confidence,
            'similar_cases_analyzed': similar_resolved.count if similar_resolved else 0
        }
    
    @staticmethod
    def identify_systemic_issues():
        """Identify recurring systemic issues with pattern matching"""
        
        # Get unresolved complaints
        complaints = Complaint.query.filter(
            Complaint.status != 'Resolved'
        ).all()
        
        # Analyze by category and location
        issue_patterns = {}
        
        for complaint in complaints:
            key = f"{complaint.category}_{complaint.district_id}"
            
            if key not in issue_patterns:
                issue_patterns[key] = {
                    'category': complaint.category,
                    'district': complaint.district.name if complaint.district else 'Unknown',
                    'complaints': [],
                    'count': 0,
                    'keywords': []
                }
            
            issue_patterns[key]['count'] += 1
            issue_patterns[key]['complaints'].append(complaint.id)
            
            # Extract keywords
            if complaint.description:
                words = complaint.description.lower().split()
                issue_patterns[key]['keywords'].extend([w for w in words if len(w) > 4])
        
        # Identify systemic issues (3+ similar complaints)
        systemic_issues = []
        for key, data in issue_patterns.items():
            if data['count'] >= 3:
                # Find most common keywords
                keyword_counts = {}
                for word in data['keywords']:
                    keyword_counts[word] = keyword_counts.get(word, 0) + 1
                
                top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                systemic_issues.append({
                    'category': data['category'],
                    'district': data['district'],
                    'complaint_count': data['count'],
                    'common_keywords': [k for k, v in top_keywords],
                    'severity': 'High' if data['count'] >= 10 else 'Medium',
                    'recommendation': f"Policy review needed for {data['category']} in {data['district']}"
                })
        
        return sorted(systemic_issues, key=lambda x: x['complaint_count'], reverse=True)
    
    @staticmethod
    def ministry_workload_forecast():
        """Forecast ministry workload for next month with capacity analysis"""
        
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
            
            in_progress = Complaint.query.filter_by(
                ministry_id=ministry.id,
                status='In Progress'
            ).count()
            
            # Forecast with seasonal adjustment
            forecasted_new = int(recent_avg * 1.15)  # 15% buffer for variation
            expected_workload = pending + in_progress + forecasted_new
            
            # Capacity assessment (assuming 50 complaints per month is normal capacity)
            capacity_percentage = (expected_workload / 50) * 100 if expected_workload > 0 else 0
            
            if capacity_percentage > 150:
                capacity_status = 'Critically Overloaded'
            elif capacity_percentage > 100:
                capacity_status = 'Overloaded'
            elif capacity_percentage > 75:
                capacity_status = 'High Load'
            else:
                capacity_status = 'Normal'
            
            forecasts.append({
                'ministry': ministry.name,
                'ministry_code': ministry.code,
                'current_pending': pending,
                'current_in_progress': in_progress,
                'forecasted_new_complaints': forecasted_new,
                'expected_total_workload': expected_workload,
                'capacity_percentage': round(capacity_percentage, 1),
                'capacity_status': capacity_status
            })
        
        return sorted(forecasts, key=lambda x: x['expected_total_workload'], reverse=True)
    
    @staticmethod
    def analyze_policy_feedback_sentiment():
        """Analyze overall sentiment trends in policy feedback"""
        
        feedbacks = PolicyFeedback.query.all()
        
        if not feedbacks:
            return {
                'message': 'No policy feedback available yet',
                'total_feedback': 0
            }
        
        sentiment_counts = {
            'positive': sum(1 for f in feedbacks if f.sentiment == 'positive'),
            'neutral': sum(1 for f in feedbacks if f.sentiment == 'neutral'),
            'negative': sum(1 for f in feedbacks if f.sentiment == 'negative')
        }
        
        total = len(feedbacks)
        
        # Calculate percentages
        sentiment_percentages = {
            'positive': round((sentiment_counts['positive'] / total) * 100, 1),
            'neutral': round((sentiment_counts['neutral'] / total) * 100, 1),
            'negative': round((sentiment_counts['negative'] / total) * 100, 1)
        }
        
        # Overall sentiment
        if sentiment_percentages['positive'] > 50:
            overall = 'Positive - Citizens are generally supportive'
        elif sentiment_percentages['negative'] > 50:
            overall = 'Negative - Significant citizen concerns'
        else:
            overall = 'Mixed - Diverse opinions'
        
        return {
            'total_feedback': total,
            'sentiment_counts': sentiment_counts,
            'sentiment_percentages': sentiment_percentages,
            'overall_sentiment': overall
        }