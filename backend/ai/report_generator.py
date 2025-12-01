from models import db, SystemReport, AIPrediction, Complaint, Ministry, District, PolicyFeedback, ServiceRating, Citizen
from ai.predictions import PredictiveAnalytics
from datetime import datetime, timedelta
from sqlalchemy import func, case, desc
import json

class ReportGenerator:
    
    @staticmethod
    def generate_system_report(generated_by_id):
        """Generate comprehensive AI-powered system report with deep analysis"""
        
        predictor = PredictiveAnalytics()
        
        print("🤖 AI Report Generator: Starting comprehensive analysis...")
        
        # Gather all data sources
        report_data = {
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'generated_by': generated_by_id,
                'report_period': '30 days',
                'analysis_depth': 'comprehensive',
                'ai_version': '2.0',
                'confidence_level': 'high'
            },
            'executive_summary': {},
            'deep_analysis': {},
            'predictions': {},
            'recommendations': {},
            'visualizations_data': {}
        }
        
        # 1. EXECUTIVE SUMMARY with Deep Insights
        print("📊 Analyzing executive summary...")
        exec_summary = ReportGenerator._generate_executive_summary()
        report_data['executive_summary'] = exec_summary
        
        # 2. COMPLAINT TREND ANALYSIS
        print("📈 Performing trend analysis...")
        complaint_trends = predictor.predict_complaint_trends()
        trend_analysis = ReportGenerator._analyze_complaint_trends(complaint_trends)
        report_data['deep_analysis']['complaint_trends'] = trend_analysis
        
        # 3. GEOGRAPHIC ANALYSIS
        print("🗺️ Analyzing geographic patterns...")
        geographic_analysis = ReportGenerator._analyze_geographic_patterns()
        report_data['deep_analysis']['geographic_patterns'] = geographic_analysis
        
        # 4. MINISTRY PERFORMANCE DEEP DIVE
        print("🏛️ Analyzing ministry performance...")
        ministry_analysis = ReportGenerator._analyze_ministry_performance()
        report_data['deep_analysis']['ministry_performance'] = ministry_analysis
        
        # 5. SYSTEMIC ISSUES DETECTION
        print("🔍 Detecting systemic issues...")
        systemic_issues = predictor.identify_systemic_issues()
        systemic_analysis = ReportGenerator._analyze_systemic_issues(systemic_issues)
        report_data['deep_analysis']['systemic_issues'] = systemic_analysis
        
        # 6. CITIZEN ENGAGEMENT ANALYSIS
        print("👥 Analyzing citizen engagement...")
        engagement_analysis = ReportGenerator._analyze_citizen_engagement()
        report_data['deep_analysis']['citizen_engagement'] = engagement_analysis
        
        # 7. POLICY FEEDBACK SENTIMENT ANALYSIS
        print("💬 Analyzing policy feedback...")
        policy_analysis = ReportGenerator._analyze_policy_sentiment()
        report_data['deep_analysis']['policy_feedback'] = policy_analysis
        
        # 8. SERVICE QUALITY ANALYSIS
        print("⭐ Analyzing service quality...")
        service_analysis = ReportGenerator._analyze_service_quality()
        report_data['deep_analysis']['service_quality'] = service_analysis
        
        # 9. PREDICTIVE FORECASTING
        print("🔮 Generating predictions...")
        predictions = ReportGenerator._generate_predictions(predictor)
        report_data['predictions'] = predictions
        
        # 10. AI-POWERED RECOMMENDATIONS
        print("💡 Generating AI recommendations...")
        recommendations = ReportGenerator._generate_ai_recommendations(report_data)
        report_data['recommendations'] = recommendations
        
        # 11. DATA FOR VISUALIZATIONS
        print("📊 Preparing visualization data...")
        viz_data = ReportGenerator._prepare_visualization_data()
        report_data['visualizations_data'] = viz_data
        
        # Calculate overall AI confidence score
        confidence_scores = [
            complaint_trends.get('confidence', 0),
            geographic_analysis.get('confidence', 75),
            ministry_analysis.get('confidence', 80),
            engagement_analysis.get('confidence', 70),
            policy_analysis.get('confidence', 75)
        ]
        report_data['metadata']['ai_confidence_score'] = round(sum(confidence_scores) / len(confidence_scores), 2)
        
        # Save report
        report = SystemReport(
            report_title=f"AI-Generated Comprehensive Analysis - {datetime.utcnow().strftime('%B %Y')}",
            report_type='AI Comprehensive Analysis',
            report_data=json.dumps(report_data),
            generated_by=generated_by_id
        )
        
        db.session.add(report)
        
        # Save predictions
        prediction = AIPrediction(
            prediction_type='Comprehensive Forecast',
            prediction_data=json.dumps(predictions),
            confidence_score=report_data['metadata']['ai_confidence_score'],
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        print("✅ Report generation complete!")
        
        return report.to_dict()
    
    @staticmethod
    def _generate_executive_summary():
        """Generate executive summary with key metrics"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        
        # Current period metrics
        current_complaints = Complaint.query.filter(Complaint.created_at >= thirty_days_ago).count()
        previous_complaints = Complaint.query.filter(
            Complaint.created_at >= sixty_days_ago,
            Complaint.created_at < thirty_days_ago
        ).count()
        
        total_complaints = Complaint.query.count()
        resolved_count = Complaint.query.filter_by(status='Resolved').count()
        pending_count = Complaint.query.filter_by(status='Pending').count()
        
        # Calculate trends
        complaint_change = ((current_complaints - previous_complaints) / previous_complaints * 100) if previous_complaints > 0 else 0
        resolution_rate = (resolved_count / total_complaints * 100) if total_complaints > 0 else 0
        
        # Average resolution time
        avg_resolution = db.session.query(
            func.avg(func.datediff('day', Complaint.created_at, Complaint.resolved_at))
        ).filter(Complaint.resolved_at.isnot(None)).scalar()
        
        # Citizen engagement
        active_citizens = db.session.query(func.count(func.distinct(Complaint.citizen_id))).scalar()
        total_citizens = Citizen.query.count()
        engagement_rate = (active_citizens / total_citizens * 100) if total_citizens > 0 else 0
        
        # Service satisfaction
        avg_rating = db.session.query(func.avg(ServiceRating.rating)).scalar() or 0
        
        return {
            'period': 'Last 30 days',
            'total_complaints': total_complaints,
            'current_period_complaints': current_complaints,
            'complaint_trend': f"{'+' if complaint_change > 0 else ''}{round(complaint_change, 1)}%",
            'resolution_rate': round(resolution_rate, 1),
            'pending_complaints': pending_count,
            'avg_resolution_time': round(avg_resolution or 0, 1),
            'citizen_engagement_rate': round(engagement_rate, 1),
            'avg_service_rating': round(float(avg_rating), 2),
            'health_score': ReportGenerator._calculate_system_health_score(
                resolution_rate, avg_resolution or 0, engagement_rate, float(avg_rating)
            )
        }
    
    @staticmethod
    def _calculate_system_health_score(resolution_rate, avg_resolution_time, engagement_rate, avg_rating):
        """Calculate overall system health score (0-100)"""
        # Weighted scoring
        resolution_score = min(resolution_rate, 100)
        speed_score = max(0, 100 - (avg_resolution_time * 5))  # Penalize slow resolution
        engagement_score = min(engagement_rate * 2, 100)
        satisfaction_score = (avg_rating / 5) * 100
        
        health_score = (
            resolution_score * 0.3 +
            speed_score * 0.3 +
            engagement_score * 0.2 +
            satisfaction_score * 0.2
        )
        
        return {
            'score': round(health_score, 1),
            'rating': 'Excellent' if health_score >= 80 else 'Good' if health_score >= 60 else 'Fair' if health_score >= 40 else 'Poor',
            'components': {
                'resolution': round(resolution_score, 1),
                'speed': round(speed_score, 1),
                'engagement': round(engagement_score, 1),
                'satisfaction': round(satisfaction_score, 1)
            }
        }
    
    @staticmethod
    def _analyze_complaint_trends(trend_data):
        """Deep analysis of complaint trends"""
        # Get historical data
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        monthly_data = db.session.query(
            func.datepart('year', Complaint.created_at).label('year'),
            func.datepart('month', Complaint.created_at).label('month'),
            func.count(Complaint.id).label('count'),
            func.avg(case([(Complaint.priority == 'Urgent', 3), (Complaint.priority == 'High', 2)], else_=1)).label('avg_severity')
        ).filter(
            Complaint.created_at >= six_months_ago
        ).group_by(
            func.datepart('year', Complaint.created_at),
            func.datepart('month', Complaint.created_at)
        ).all()
        
        # Analyze patterns
        counts = [row.count for row in monthly_data]
        severities = [row.avg_severity for row in monthly_data]
        
        # Detect seasonality
        if len(counts) >= 6:
            # Simple moving average
            ma_3 = sum(counts[-3:]) / 3
            ma_6 = sum(counts) / len(counts)
            volatility = sum(abs(counts[i] - counts[i-1]) for i in range(1, len(counts))) / len(counts)
        else:
            ma_3 = ma_6 = volatility = 0
        
        return {
            'raw_trend': trend_data,
            'monthly_pattern': [{'year': int(r.year), 'month': int(r.month), 'count': r.count} for r in monthly_data],
            'moving_average_3m': round(ma_3, 1),
            'moving_average_6m': round(ma_6, 1),
            'volatility': round(volatility, 1),
            'average_severity': round(sum(severities) / len(severities), 2) if severities else 0,
            'trend_assessment': ReportGenerator._assess_trend(trend_data, volatility),
            'confidence': trend_data.get('confidence', 75)
        }
    
    @staticmethod
    def _assess_trend(trend_data, volatility):
        """Assess the overall trend with confidence"""
        trend = trend_data.get('trend', 'stable')
        avg_change = trend_data.get('average_change', 0)
        
        if volatility > 10:
            stability = 'High volatility - unpredictable pattern'
        elif volatility > 5:
            stability = 'Moderate volatility - some fluctuation'
        else:
            stability = 'Low volatility - stable pattern'
        
        if trend == 'increasing':
            severity = 'Critical' if avg_change > 10 else 'High' if avg_change > 5 else 'Moderate'
            return f"{severity} increase detected. {stability}. Immediate intervention recommended."
        elif trend == 'decreasing':
            return f"Positive decrease observed. {stability}. Current strategies are effective."
        else:
            return f"Stable trend. {stability}. Maintain current approach with regular monitoring."
    
    @staticmethod
    def _analyze_geographic_patterns():
        """Analyze geographic distribution and patterns"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # District analysis
        district_stats = db.session.query(
            District.name,
            District.region,
            func.count(Complaint.id).label('complaint_count'),
            func.sum(case([(Complaint.priority == 'Urgent', 1)], else_=0)).label('urgent_count'),
            func.avg(case([(Complaint.status == 'Resolved', 1)], else_=0)).label('resolution_rate')
        ).join(
            Complaint, District.id == Complaint.district_id
        ).filter(
            Complaint.created_at >= thirty_days_ago
        ).group_by(
            District.id, District.name, District.region
        ).all()
        
        # Regional analysis
        regional_stats = {}
        for stat in district_stats:
            region = stat.region or 'Unknown'
            if region not in regional_stats:
                regional_stats[region] = {'count': 0, 'districts': 0, 'urgent': 0}
            regional_stats[region]['count'] += stat.complaint_count
            regional_stats[region]['districts'] += 1
            regional_stats[region]['urgent'] += stat.urgent_count
        
        # Identify hotspots
        hotspots = sorted(
            [{'district': s.name, 'region': s.region, 'complaints': s.complaint_count, 
              'urgent': s.urgent_count, 'resolution_rate': round(float(s.resolution_rate or 0) * 100, 1)}
             for s in district_stats],
            key=lambda x: x['complaints'],
            reverse=True
        )[:5]
        
        return {
            'hotspots': hotspots,
            'regional_distribution': regional_stats,
            'geographic_insights': ReportGenerator._generate_geographic_insights(hotspots, regional_stats),
            'confidence': 80
        }
    
    @staticmethod
    def _generate_geographic_insights(hotspots, regional_stats):
        """Generate insights from geographic data"""
        insights = []
        
        if hotspots:
            top_district = hotspots[0]
            insights.append(f"{top_district['district']} is the highest complaint district with {top_district['complaints']} cases and {top_district['urgent']} urgent issues.")
        
        # Find most affected region
        if regional_stats:
            max_region = max(regional_stats.items(), key=lambda x: x[1]['count'])
            insights.append(f"{max_region[0]} region has the highest complaint volume with {max_region[1]['count']} total complaints across {max_region[1]['districts']} districts.")
        
        # Identify patterns
        if len(hotspots) >= 3:
            avg_top_3 = sum(h['complaints'] for h in hotspots[:3]) / 3
            if hotspots[0]['complaints'] > avg_top_3 * 1.5:
                insights.append(f"Significant concentration detected: {hotspots[0]['district']} has disproportionately high complaint volume.")
        
        return insights
    
    @staticmethod
    def _analyze_ministry_performance():
        """Comprehensive ministry performance analysis"""
        ministries = Ministry.query.all()
        performance_data = []
        
        for ministry in ministries:
            total = Complaint.query.filter_by(ministry_id=ministry.id).count()
            resolved = Complaint.query.filter_by(ministry_id=ministry.id, status='Resolved').count()
            pending = Complaint.query.filter_by(ministry_id=ministry.id, status='Pending').count()
            in_progress = Complaint.query.filter_by(ministry_id=ministry.id, status='In Progress').count()
            
            # Average resolution time
            avg_time = db.session.query(
                func.avg(func.datediff('day', Complaint.created_at, Complaint.resolved_at))
            ).filter(
                Complaint.ministry_id == ministry.id,
                Complaint.resolved_at.isnot(None)
            ).scalar()
            
            if total > 0:
                resolution_rate = (resolved / total) * 100
                efficiency_score = ReportGenerator._calculate_ministry_efficiency(
                    resolution_rate, avg_time or 0, pending, total
                )
                
                performance_data.append({
                    'ministry': ministry.name,
                    'code': ministry.code,
                    'total_complaints': total,
                    'resolved': resolved,
                    'pending': pending,
                    'in_progress': in_progress,
                    'resolution_rate': round(resolution_rate, 1),
                    'avg_resolution_days': round(float(avg_time or 0), 1),
                    'efficiency_score': efficiency_score,
                    'performance_grade': ReportGenerator._grade_ministry(efficiency_score)
                })
        
        # Rank ministries
        ranked = sorted(performance_data, key=lambda x: x['efficiency_score'], reverse=True)
        
        return {
            'ministry_performance': ranked,
            'best_performer': ranked[0] if ranked else None,
            'needs_improvement': [m for m in ranked if m['efficiency_score'] < 50],
            'insights': ReportGenerator._generate_ministry_insights(ranked),
            'confidence': 85
        }
    
    @staticmethod
    def _calculate_ministry_efficiency(resolution_rate, avg_time, pending, total):
        """Calculate ministry efficiency score (0-100)"""
        resolution_score = resolution_rate
        speed_score = max(0, 100 - (avg_time * 7))  # Penalty for slow resolution
        workload_score = max(0, 100 - (pending / total * 100)) if total > 0 else 50
        
        efficiency = (resolution_score * 0.5 + speed_score * 0.3 + workload_score * 0.2)
        return round(efficiency, 1)
    
    @staticmethod
    def _grade_ministry(score):
        """Assign performance grade"""
        if score >= 90: return 'A+ (Excellent)'
        if score >= 80: return 'A (Very Good)'
        if score >= 70: return 'B (Good)'
        if score >= 60: return 'C (Satisfactory)'
        if score >= 50: return 'D (Needs Improvement)'
        return 'F (Critical)'
    
    @staticmethod
    def _generate_ministry_insights(ranked):
        """Generate insights from ministry performance"""
        insights = []
        
        if ranked:
            best = ranked[0]
            worst = ranked[-1]
            
            insights.append(f"{best['ministry']} leads with {best['efficiency_score']}% efficiency and {best['resolution_rate']}% resolution rate.")
            
            if worst['efficiency_score'] < 50:
                insights.append(f"{worst['ministry']} requires immediate attention with {worst['pending']} pending complaints and {worst['avg_resolution_days']} day average resolution time.")
            
            # Identify struggling ministries
            struggling = [m for m in ranked if m['efficiency_score'] < 60]
            if len(struggling) > 3:
                insights.append(f"{len(struggling)} ministries are performing below acceptable standards. Systemic resource reallocation recommended.")
        
        return insights
    
    @staticmethod
    def _analyze_systemic_issues(systemic_issues):
        """Analyze systemic issues with pattern detection"""
        if not systemic_issues:
            return {
                'total_systemic_issues': 0,
                'issues': [],
                'patterns': [],
                'confidence': 70
            }
        
        # Group by severity
        high_severity = [i for i in systemic_issues if i['severity'] == 'High']
        medium_severity = [i for i in systemic_issues if i['severity'] == 'Medium']
        
        # Detect cross-category patterns
        categories = [i['category'] for i in systemic_issues]
        most_common_category = max(set(categories), key=categories.count) if categories else None
        
        patterns = []
        if most_common_category and categories.count(most_common_category) >= 3:
            patterns.append(f"Recurring pattern in {most_common_category}: {categories.count(most_common_category)} distinct systemic issues detected.")
        
        return {
            'total_systemic_issues': len(systemic_issues),
            'high_severity_count': len(high_severity),
            'medium_severity_count': len(medium_severity),
            'issues': systemic_issues[:10],  # Top 10
            'patterns': patterns,
            'most_affected_category': most_common_category,
            'recommendations': ReportGenerator._generate_systemic_recommendations(systemic_issues),
            'confidence': 75
        }
    
    @staticmethod
    def _generate_systemic_recommendations(issues):
        """Generate recommendations for systemic issues"""
        recommendations = []
        
        for issue in issues[:5]:  # Top 5
            if issue['severity'] == 'High':
                recommendations.append({
                    'issue': f"{issue['category']} in {issue['district']}",
                    'cases': issue['complaint_count'],
                    'action': f"Establish task force to address {issue['complaint_count']} related cases. Conduct root cause analysis and implement policy changes."
                })
        
        return recommendations
    
    @staticmethod
    def _analyze_citizen_engagement():
        """Analyze citizen engagement patterns"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Active citizens
        active_last_30 = db.session.query(
            func.count(func.distinct(Complaint.citizen_id))
        ).filter(Complaint.created_at >= thirty_days_ago).scalar()
        
        total_citizens = Citizen.query.count()
        
        # Repeat complainants
        repeat_complainants = db.session.query(
            Complaint.citizen_id,
            func.count(Complaint.id).label('complaint_count')
        ).group_by(
            Complaint.citizen_id
        ).having(
            func.count(Complaint.id) > 1
        ).count()
        
        # Policy feedback participation
        feedback_participants = db.session.query(
            func.count(func.distinct(PolicyFeedback.citizen_id))
        ).scalar()
        
        # Service ratings participation
        rating_participants = db.session.query(
            func.count(func.distinct(ServiceRating.citizen_id))
        ).scalar()
        
        engagement_rate = (active_last_30 / total_citizens * 100) if total_citizens > 0 else 0
        multi_channel_users = min(feedback_participants, rating_participants)  # Users engaging in multiple ways
        
        return {
            'total_registered_citizens': total_citizens,
            'active_last_30_days': active_last_30,
            'engagement_rate': round(engagement_rate, 1),
            'repeat_users': repeat_complainants,
            'policy_feedback_participants': feedback_participants,
            'service_rating_participants': rating_participants,
            'multi_channel_engagement': multi_channel_users,
            'engagement_quality': 'High' if engagement_rate > 20 else 'Medium' if engagement_rate > 10 else 'Low',
            'insights': ReportGenerator._generate_engagement_insights(
                engagement_rate, repeat_complainants, multi_channel_users
            ),
            'confidence': 70
        }
    
    @staticmethod
    def _generate_engagement_insights(rate, repeat_users, multi_channel):
        """Generate citizen engagement insights"""
        insights = []
        
        if rate < 10:
            insights.append("Low citizen engagement detected. Launch awareness campaigns and simplify submission processes.")
        elif rate > 25:
            insights.append("Strong citizen engagement. Platform adoption is successful.")
        
        if repeat_users > 100:
            insights.append(f"{repeat_users} citizens have submitted multiple complaints, indicating either persistent issues or high trust in the system.")
        
        if multi_channel > 50:
            insights.append(f"{multi_channel} citizens engage through multiple channels (complaints, feedback, ratings), showing deep platform integration.")
        
        return insights
    
    @staticmethod
    def _analyze_policy_sentiment():
        """Analyze policy feedback sentiment trends"""
        feedbacks = PolicyFeedback.query.all()
        
        if not feedbacks:
            return {
                'total_feedback': 0,
                'sentiment_distribution': {},
                'confidence': 50
            }
        
        sentiment_counts = {
            'positive': sum(1 for f in feedbacks if f.sentiment == 'positive'),
            'neutral': sum(1 for f in feedbacks if f.sentiment == 'neutral'),
            'negative': sum(1 for f in feedbacks if f.sentiment == 'negative')
        }
        
        total = len(feedbacks)
        sentiment_percentages = {
            'positive': round((sentiment_counts['positive'] / total) * 100, 1),
            'neutral': round((sentiment_counts['neutral'] / total) * 100, 1),
            'negative': round((sentiment_counts['negative'] / total) * 100, 1)
        }
        
        # Overall sentiment score (-100 to +100)
        sentiment_score = (
            (sentiment_counts['positive'] * 100) +
            (sentiment_counts['neutral'] * 0) +
            (sentiment_counts['negative'] * -100)
        ) / total if total > 0 else 0
        
        return {
            'total_feedback': total,
            'sentiment_counts': sentiment_counts,
            'sentiment_percentages': sentiment_percentages,
            'sentiment_score': round(sentiment_score, 1),
            'overall_mood': ReportGenerator._interpret_sentiment_score(sentiment_score),
            'insights': ReportGenerator._generate_policy_insights(sentiment_percentages, total),
            'confidence': 75
        }
    
    @staticmethod
    def _interpret_sentiment_score(score):
        """Interpret sentiment score"""
        if score > 50: return 'Very Positive - Citizens strongly support policies'
        if score > 20: return 'Positive - General support for policies'
        if score > -20: return 'Mixed - Divided opinions on policies'
        if score > -50: return 'Negative - Citizens express concerns'
        return 'Very Negative - Significant citizen opposition'
    
    @staticmethod
    def _generate_policy_insights(percentages, total):
        """Generate policy sentiment insights"""
        insights = []
        
        if percentages['negative'] > 50:
            insights.append(f"Alert: {percentages['negative']}% negative feedback. Review policies for citizen concerns.")
        elif percentages['positive'] > 60:
            insights.append(f"Strong support: {percentages['positive']}% positive feedback indicates successful policy direction.")
        
        if total < 50:
            insights.append("Low participation in policy feedback. Increase citizen awareness and engagement campaigns.")
        
        return insights
    
    @staticmethod
    def _analyze_service_quality():
        """Analyze service quality ratings"""
        ratings = ServiceRating.query.all()
        
        if not ratings:
            return {
                'total_ratings': 0,
                'avg_rating': 0,
                'confidence': 50
            }
        
        # By service type
        service_stats = {}
        for rating in ratings:
            if rating.service_type not in service_stats:
                service_stats[rating.service_type] = []
            service_stats[rating.service_type].append(rating.rating)
        
        service_averages = {
            service: round(sum(ratings_list) / len(ratings_list), 2)
            for service, ratings_list in service_stats.items()
        }
        
        overall_avg = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
        
        # Identify best and worst
        best_service = max(service_averages.items(), key=lambda x: x[1]) if service_averages else None
        worst_service = min(service_averages.items(), key=lambda x: x[1]) if service_averages else None
        
        return {
            'total_ratings': len(ratings),
            'overall_average': round(overall_avg, 2),
            'service_averages': service_averages,
            'best_rated_service': {'service': best_service[0], 'rating': best_service[1]} if best_service else None,
            'worst_rated_service': {'service': worst_service[0], 'rating': worst_service[1]} if worst_service else None,
            'quality_grade': ReportGenerator._grade_service_quality(overall_avg),
            'insights': ReportGenerator._generate_quality_insights(overall_avg, service_averages),
            'confidence': 80
        }
    
    @staticmethod
    def _grade_service_quality(avg):
        """Grade overall service quality"""
        if avg >= 4.5: return 'Excellent'
        if avg >= 4.0: return 'Very Good'
        if avg >= 3.5: return 'Good'
        if avg >= 3.0: return 'Satisfactory'
        if avg >= 2.5: return 'Needs Improvement'
        return 'Poor'
    
    @staticmethod
    def _generate_quality_insights(overall_avg, service_avgs):
        """Generate service quality insights"""
        insights = []
        
        if overall_avg < 3.0:
            insights.append(f"Critical: Overall service rating of {overall_avg}/5.0 indicates widespread dissatisfaction.")
        elif overall_avg > 4.0:
            insights.append(f"Excellent: {overall_avg}/5.0 rating shows high citizen satisfaction.")
        
        if service_avgs:
            # Find disparities
            ratings = list(service_avgs.values())
            if max(ratings) - min(ratings) > 1.5:
                insights.append("Significant service quality disparity detected across service types. Standardization needed.")
        
        return insights
    
    @staticmethod
    def _generate_predictions(predictor):
        """Generate comprehensive predictions"""
        return {
            'complaint_forecast': predictor.predict_complaint_trends(),
            'high_risk_areas': predictor.identify_high_risk_areas(),
            'ministry_workload': predictor.ministry_workload_forecast(),
            'systemic_issues': predictor.identify_systemic_issues()
        }
    
    @staticmethod
    def _generate_ai_recommendations(report_data):
        """Generate AI-powered actionable recommendations"""
        recommendations = []
        
        # Based on executive summary
        exec_summary = report_data['executive_summary']
        if exec_summary['health_score']['score'] < 60:
            recommendations.append({
                'priority': 'Critical',
                'category': 'System Health',
                'recommendation': 'System health score below acceptable threshold',
                'actions': [
                    f"Address resolution rate ({exec_summary['resolution_rate']}% - target: 75%+)",
                    f"Reduce average resolution time ({exec_summary['avg_resolution_time']} days - target: <7 days)",
                    'Implement comprehensive improvement program'
                ],
                'expected_impact': 'High',
                'timeline': '30-60 days'
            })
        
        # Based on trends
        trend_analysis = report_data['deep_analysis']['complaint_trends']
        if 'increasing' in trend_analysis['raw_trend'].get('trend', ''):
            recommendations.append({
                'priority': 'High',
                'category': 'Resource Allocation',
                'recommendation': 'Prepare for projected complaint volume increase',
                'actions': [
                    f"Scale staffing to handle {trend_analysis['raw_trend'].get('predicted_complaints', 0)} expected complaints",
                    'Review resource distribution across ministries',
                    'Implement overflow protocols'
                ],
                'expected_impact': 'Medium',
                'timeline': '15-30 days'
            })
        
        # Based on geographic patterns
        geo_analysis = report_data['deep_analysis']['geographic_patterns']
        if geo_analysis['hotspots']:
            top_hotspot = geo_analysis['hotspots'][0]
            if top_hotspot['complaints'] > 50:
                recommendations.append({
                    'priority': 'High',
                    'category': 'Geographic Intervention',
                    'recommendation': f"Deploy resources to {top_hotspot['district']} district",
                    'actions': [
                        f"Establish rapid response team for {top_hotspot['district']}",
                        f"Address {top_hotspot['urgent']} urgent cases immediately",
                        'Conduct district assessment and root cause analysis'
                    ],
                    'expected_impact': 'High',
                    'timeline': '7-14 days'
                })
        
        # Based on ministry performance
        ministry_analysis = report_data['deep_analysis']['ministry_performance']
        if ministry_analysis['needs_improvement']:
            for ministry in ministry_analysis['needs_improvement'][:2]:
                recommendations.append({
                    'priority': 'High',
                    'category': 'Ministry Capacity',
                    'recommendation': f"Improve {ministry['ministry']} performance",
                    'actions': [
                        f"Address {ministry['pending']} pending complaints",
                        f"Reduce resolution time from {ministry['avg_resolution_days']} days",
                        'Provide additional training or resources',
                        'Implement performance monitoring'
                    ],
                    'expected_impact': 'Medium',
                    'timeline': '30-45 days'
                })
        
        # Based on systemic issues
        systemic_analysis = report_data['deep_analysis']['systemic_issues']
        if systemic_analysis['high_severity_count'] > 0:
            recommendations.append({
                'priority': 'Critical',
                'category': 'Policy Reform',
                'recommendation': f"Address {systemic_analysis['high_severity_count']} high-severity systemic issues",
                'actions': [
                    'Form inter-ministerial task force',
                    'Conduct comprehensive policy review',
                    'Engage stakeholders for solutions',
                    'Implement pilot programs for new policies'
                ],
                'expected_impact': 'Very High',
                'timeline': '60-90 days'
            })
        
        # Based on citizen engagement
        engagement_analysis = report_data['deep_analysis']['citizen_engagement']
        if engagement_analysis['engagement_rate'] < 15:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Citizen Engagement',
                'recommendation': 'Increase citizen participation and platform adoption',
                'actions': [
                    'Launch awareness campaigns',
                    'Simplify complaint submission process',
                    'Provide citizen education programs',
                    'Expand outreach to underserved areas'
                ],
                'expected_impact': 'Medium',
                'timeline': '30-60 days'
            })
        
        # Based on service quality
        service_analysis = report_data['deep_analysis']['service_quality']
        if service_analysis['overall_average'] < 3.5:
            recommendations.append({
                'priority': 'High',
                'category': 'Service Quality',
                'recommendation': 'Improve overall service satisfaction',
                'actions': [
                    f"Address low-rated services (current avg: {service_analysis['overall_average']}/5.0)",
                    'Implement quality assurance programs',
                    'Provide customer service training',
                    'Establish service standards and monitoring'
                ],
                'expected_impact': 'High',
                'timeline': '30-45 days'
            })
        
        # Sort by priority
        priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 99))
        
        return recommendations
    
    @staticmethod
    def _prepare_visualization_data():
        """Prepare data for charts and visualizations"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        # 1. Monthly complaint trend (6 months)
        monthly_trend = db.session.query(
            func.datepart('year', Complaint.created_at).label('year'),
            func.datepart('month', Complaint.created_at).label('month'),
            func.count(Complaint.id).label('count')
        ).filter(
            Complaint.created_at >= six_months_ago
        ).group_by(
            func.datepart('year', Complaint.created_at),
            func.datepart('month', Complaint.created_at)
        ).order_by('year', 'month').all()
        
        # 2. Complaints by status
        status_distribution = db.session.query(
            Complaint.status,
            func.count(Complaint.id).label('count')
        ).group_by(Complaint.status).all()
        
        # 3. Complaints by priority
        priority_distribution = db.session.query(
            Complaint.priority,
            func.count(Complaint.id).label('count')
        ).group_by(Complaint.priority).all()
        
        # 4. Top 10 districts by complaint count
        top_districts = db.session.query(
            District.name,
            func.count(Complaint.id).label('count')
        ).join(
            Complaint, District.id == Complaint.district_id
        ).filter(
            Complaint.created_at >= thirty_days_ago
        ).group_by(
            District.name
        ).order_by(desc('count')).limit(10).all()
        
        # 5. Ministry performance comparison
        ministry_comparison = db.session.query(
            Ministry.name,
            func.count(Complaint.id).label('total'),
            func.sum(case([(Complaint.status == 'Resolved', 1)], else_=0)).label('resolved'),
            func.sum(case([(Complaint.status == 'Pending', 1)], else_=0)).label('pending')
        ).join(
            Complaint, Ministry.id == Complaint.ministry_id
        ).group_by(
            Ministry.name
        ).all()
        
        # 6. Resolution time distribution
        resolution_times = db.session.query(
            func.datediff('day', Complaint.created_at, Complaint.resolved_at).label('days')
        ).filter(
            Complaint.resolved_at.isnot(None),
            Complaint.created_at >= six_months_ago
        ).all()
        
        # Group resolution times into buckets
        time_buckets = {'0-3 days': 0, '4-7 days': 0, '8-14 days': 0, '15-30 days': 0, '30+ days': 0}
        for time in resolution_times:
            days = time.days or 0
            if days <= 3:
                time_buckets['0-3 days'] += 1
            elif days <= 7:
                time_buckets['4-7 days'] += 1
            elif days <= 14:
                time_buckets['8-14 days'] += 1
            elif days <= 30:
                time_buckets['15-30 days'] += 1
            else:
                time_buckets['30+ days'] += 1
        
        # 7. Sentiment distribution over time
        sentiment_trend = db.session.query(
            func.datepart('year', PolicyFeedback.created_at).label('year'),
            func.datepart('month', PolicyFeedback.created_at).label('month'),
            PolicyFeedback.sentiment,
            func.count(PolicyFeedback.id).label('count')
        ).filter(
            PolicyFeedback.created_at >= six_months_ago
        ).group_by(
            func.datepart('year', PolicyFeedback.created_at),
            func.datepart('month', PolicyFeedback.created_at),
            PolicyFeedback.sentiment
        ).all()
        
        # 8. Service ratings distribution
        rating_distribution = db.session.query(
            ServiceRating.rating,
            func.count(ServiceRating.id).label('count')
        ).group_by(ServiceRating.rating).all()
        
        return {
            'monthly_trend': [
                {'year': int(r.year), 'month': int(r.month), 'count': r.count}
                for r in monthly_trend
            ],
            'status_distribution': [
                {'status': r.status, 'count': r.count}
                for r in status_distribution
            ],
            'priority_distribution': [
                {'priority': r.priority, 'count': r.count}
                for r in priority_distribution
            ],
            'top_districts': [
                {'district': r.name, 'count': r.count}
                for r in top_districts
            ],
            'ministry_comparison': [
                {
                    'ministry': r.name,
                    'total': r.total,
                    'resolved': r.resolved,
                    'pending': r.pending,
                    'resolution_rate': round((r.resolved / r.total * 100), 1) if r.total > 0 else 0
                }
                for r in ministry_comparison
            ],
            'resolution_time_buckets': time_buckets,
            'sentiment_trend': [
                {'year': int(r.year), 'month': int(r.month), 'sentiment': r.sentiment, 'count': r.count}
                for r in sentiment_trend
            ],
            'rating_distribution': [
                {'rating': r.rating, 'count': r.count}
                for r in rating_distribution
            ]
        }