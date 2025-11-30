from models import db, SystemReport, AIPrediction
from ai.predictions import PredictiveAnalytics
from datetime import datetime, timedelta
import json

class ReportGenerator:
    
    @staticmethod
    def generate_system_report(generated_by_id):
        """Generate comprehensive system data-based report with AI insights"""
        
        predictor = PredictiveAnalytics()
        
        print("Generating predictions...")
        
        # Get all predictions
        complaint_trends = predictor.predict_complaint_trends()
        high_risk_areas = predictor.identify_high_risk_areas()
        systemic_issues = predictor.identify_systemic_issues()
        ministry_workload = predictor.ministry_workload_forecast()
        policy_sentiment = predictor.analyze_policy_feedback_sentiment()
        
        print("Predictions generated, creating report...")
        
        report_data = {
            'executive_summary': {
                'generated_at': datetime.utcnow().isoformat(),
                'report_period': 'Last 30 days',
                'key_findings': [],
                'critical_alerts': []
            },
            'complaint_trends': complaint_trends,
            'high_risk_areas': high_risk_areas,
            'systemic_issues': systemic_issues,
            'ministry_workload_forecast': ministry_workload,
            'policy_feedback_sentiment': policy_sentiment,
            'recommendations': [],
            'ai_confidence_score': 0.0
        }
        
        # Generate key findings
        findings = []
        alerts = []
        
        if complaint_trends['trend'] == 'increasing':
            finding = f"⚠️ Complaint volume is {complaint_trends['trend']} with {complaint_trends['confidence']}% confidence. Expected {complaint_trends['predicted_complaints']} complaints next month (current: {complaint_trends['current_month']})."
            findings.append(finding)
            if complaint_trends['average_change'] > 10:
                alerts.append("CRITICAL: Rapid increase in complaint volume detected")
        
        if high_risk_areas:
            top_district = high_risk_areas[0]
            finding = f"🚨 {top_district['district']} district shows highest risk level: {top_district['risk_level']} with {top_district['recent_complaints']} recent complaints ({top_district['urgent_complaints']} urgent)."
            findings.append(finding)
            if top_district['risk_level'] == 'Critical':
                alerts.append(f"CRITICAL: {top_district['district']} requires immediate intervention")
        
        if systemic_issues:
            finding = f"🔍 Identified {len(systemic_issues)} systemic issues requiring policy intervention."
            findings.append(finding)
            for issue in systemic_issues[:3]:
                if issue['severity'] == 'High':
                    alerts.append(f"SYSTEMIC: {issue['category']} issues in {issue['district']} ({issue['complaint_count']} cases)")
        
        # Check ministry workload
        overloaded = [m for m in ministry_workload if m['capacity_status'] in ['Overloaded', 'Critically Overloaded']]
        if overloaded:
            finding = f"⚡ {len(overloaded)} ministries are overloaded or critically overloaded."
            findings.append(finding)
            for ministry in overloaded:
                if ministry['capacity_status'] == 'Critically Overloaded':
                    alerts.append(f"CAPACITY: {ministry['ministry']} critically overloaded ({ministry['capacity_percentage']}%)")
        
        # Policy sentiment
        if policy_sentiment.get('total_feedback', 0) > 0:
            finding = f"💬 Policy feedback sentiment: {policy_sentiment['overall_sentiment']} (Total: {policy_sentiment['total_feedback']} feedback submissions)"
            findings.append(finding)
        
        report_data['executive_summary']['key_findings'] = findings
        report_data['executive_summary']['critical_alerts'] = alerts
        
        # Generate recommendations
        report_data['recommendations'] = ReportGenerator._generate_recommendations(
            complaint_trends, high_risk_areas, systemic_issues, ministry_workload
        )
        
        # Calculate overall AI confidence
        confidence_scores = [
            complaint_trends.get('confidence', 0),
            75 if high_risk_areas else 0,
            80 if systemic_issues else 0,
            70 if ministry_workload else 0
        ]
        report_data['ai_confidence_score'] = round(sum(confidence_scores) / len(confidence_scores), 2)
        
        # Save report
        report = SystemReport(
            report_title=f"AI-Generated System Report - {datetime.utcnow().strftime('%B %Y')}",
            report_type='Predictive Analysis',
            report_data=json.dumps(report_data),
            generated_by=generated_by_id
        )
        
        db.session.add(report)
        
        # Save predictions
        prediction = AIPrediction(
            prediction_type='Monthly Forecast',
            prediction_data=json.dumps({
                'complaint_forecast': complaint_trends,
                'high_risk_districts': high_risk_areas[:5],
                'systemic_issues': systemic_issues[:5]
            }),
            confidence_score=report_data['ai_confidence_score'],
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        print("Report saved successfully")
        
        return report.to_dict()
    
    @staticmethod
    def _generate_recommendations(trends, risk_areas, issues, workload):
        """Generate actionable recommendations with priority levels"""
        
        recommendations = []
        
        # Trend-based recommendations
        if trends['trend'] in ['increasing', 'slightly increasing']:
            recommendations.append({
                'category': 'Resource Allocation',
                'priority': 'High' if trends['average_change'] > 10 else 'Medium',
                'recommendation': 'Increase staffing and resources to handle projected complaint surge.',
                'rationale': f"Complaints expected to increase to {trends['predicted_complaints']} next month.",
                'action_items': [
                    'Review current staff capacity',
                    'Consider temporary staff augmentation',
                    'Prepare response protocols for high volume'
                ]
            })
        
        # Risk area recommendations
        if risk_areas:
            for area in risk_areas[:3]:
                if area['risk_level'] in ['High', 'Critical']:
                    recommendations.append({
                        'category': 'District Intervention',
                        'priority': 'Critical' if area['risk_level'] == 'Critical' else 'High',
                        'recommendation': f"Deploy additional resources to {area['district']} district - {area['recommended_action']}",
                        'rationale': f"{area['recent_complaints']} recent complaints with {area['urgent_complaints']} urgent cases. Risk score: {area['risk_score']}.",
                        'action_items': [
                            f"Conduct assessment in {area['district']}",
                            'Allocate emergency response team',
                            'Set up district coordination center'
                        ]
                    })
        
        # Systemic issue recommendations
        if issues:
            for issue in issues[:3]:
                if issue['severity'] == 'High':
                    recommendations.append({
                        'category': 'Policy Review',
                        'priority': 'High',
                        'recommendation': issue['recommendation'],
                        'rationale': f"{issue['complaint_count']} similar complaints identified in {issue['category']}.",
                        'action_items': [
                            'Form policy review committee',
                            'Conduct stakeholder consultations',
                            'Draft policy amendments',
                            'Implement pilot program'
                        ]
                    })
        
        # Ministry workload recommendations
        overloaded_ministries = [m for m in workload if m['capacity_status'] in ['Overloaded', 'Critically Overloaded']]
        if overloaded_ministries:
            for ministry in overloaded_ministries[:2]:
                recommendations.append({
                    'category': 'Capacity Building',
                    'priority': 'Critical' if ministry['capacity_status'] == 'Critically Overloaded' else 'High',
                    'recommendation': f"Urgent capacity increase needed for {ministry['ministry']}",
                    'rationale': f"Expected workload: {ministry['expected_total_workload']} complaints ({ministry['capacity_percentage']}% of normal capacity). Currently {ministry['current_pending']} pending.",
                    'action_items': [
                        'Hire additional staff or contractors',
                        'Implement complaint triage system',
                        'Automate routine processes',
                        'Consider inter-ministry support'
                    ]
                })
        
        return sorted(recommendations, key=lambda x: {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}.get(x['priority'], 4))