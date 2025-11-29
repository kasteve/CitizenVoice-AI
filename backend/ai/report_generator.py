## 10. Report Generator (backend/ai/report_generator.py)
```python
from models import db, SystemReport, AIPrediction
from ai.predictions import PredictiveAnalytics
from datetime import datetime, timedelta
import json

class ReportGenerator:
    
    @staticmethod
    def generate_system_report(generated_by_id):
        """Generate comprehensive system data-based report"""
        
        predictor = PredictiveAnalytics()
        
        # Get all predictions
        complaint_trends = predictor.predict_complaint_trends()
        high_risk_areas = predictor.identify_high_risk_areas()
        systemic_issues = predictor.identify_systemic_issues()
        ministry_workload = predictor.ministry_workload_forecast()
        
        report_data = {
            'executive_summary': {
                'generated_at': datetime.utcnow().isoformat(),
                'report_period': '30 days',
                'key_findings': []
            },
            'complaint_trends': complaint_trends,
            'high_risk_areas': high_risk_areas,
            'systemic_issues': systemic_issues,
            'ministry_workload_forecast': ministry_workload,
            'recommendations': []
        }
        
        # Generate key findings
        if complaint_trends['trend'] == 'increasing':
            report_data['executive_summary']['key_findings'].append(
                f"Complaint volume is {complaint_trends['trend']} with {complaint_trends['confidence']}% confidence. "
                f"Expected {complaint_trends['predicted_complaints']} complaints next month."
            )
        
        if high_risk_areas:
            top_district = high_risk_areas[0]
            report_data['executive_summary']['key_findings'].append(
                f"{top_district['district']} district shows highest complaint rate with "
                f"{top_district['recent_complaints']} recent complaints and risk level: {top_district['risk_level']}."
            )
        
        if systemic_issues:
            report_data['executive_summary']['key_findings'].append(
                f"Identified {len(systemic_issues)} systemic issues requiring policy intervention."
            )
        
        # Generate recommendations
        report_data['recommendations'] = ReportGenerator._generate_recommendations(
            complaint_trends, high_risk_areas, systemic_issues, ministry_workload
        )
        
        # Save report
        report = SystemReport(
            report_title=f"System Data-Based Report - {datetime.utcnow().strftime('%B %Y')}",
            report_type='Predictive Analysis',
            report_data=json.dumps(report_data),
            generated_by=generated_by_id
        )
        
        db.session.add(report)
        
        # Save predictions
        prediction = AIPrediction(
            prediction_type='Monthly Complaint Forecast',
            prediction_data=json.dumps(complaint_trends),
            confidence_score=complaint_trends['confidence'],
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return report.to_dict()
    
    @staticmethod
    def _generate_recommendations(trends, risk_areas, issues, workload):
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Trend-based recommendations
        if trends['trend'] == 'increasing':
            recommendations.append({
                'category': 'Resource Allocation',
                'priority': 'High',
                'recommendation': 'Increase staffing and resources to handle projected complaint surge.',
                'rationale': f"Complaints expected to increase to {trends['predicted_complaints']} next month."
            })
        
        # Risk area recommendations
        if risk_areas:
            for area in risk_areas[:3]:
                if area['risk_level'] == 'High':
                    recommendations.append({
                        'category': 'District Intervention',
                        'priority': 'High',
                        'recommendation': f"Deploy additional resources to {area['district']} district.",
                        'rationale': f"High complaint rate: {area['recent_complaints']} recent complaints with {area['urgent_complaints']} urgent cases."
                    })
        
        # Systemic issue recommendations
        if issues:
            for issue in issues[:3]:
                if issue['severity'] == 'High':
                    recommendations.append({
                        'category': 'Policy Review',
                        'priority': 'High',
                        'recommendation': f"Conduct policy review for recurring {issue['category']} issues.",
                        'rationale': f"{issue['complaint_count']} similar complaints identified: {issue['issue_keywords']}."
                    })
        
        # Ministry workload recommendations
        overloaded_ministries = [m for m in workload if m['capacity_status'] == 'Overloaded']
        if overloaded_ministries:
            for ministry in overloaded_ministries[:2]:
                recommendations.append({
                    'category': 'Capacity Building',
                    'priority': 'Medium',
                    'recommendation': f"Increase capacity for {ministry['ministry']}.",
                    'rationale': f"Expected workload: {ministry['expected_total_workload']} complaints with {ministry['current_pending']} currently pending."
                })
        
        return recommendations

