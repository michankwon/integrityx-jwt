import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add src directory to Python path for local imports
sys.path.append(str(Path(__file__).parent))

from walacor_service import WalacorIntegrityService


class AnomalyDetector:
    """
    AI-powered anomaly detection system for predictive fraud analysis in financial documents.
    
    This class analyzes loan data and historical patterns to predict potential fraud
    scenarios before they occur. It uses a weighted risk scoring system to identify
    high-risk loans and generate actionable recommendations for fraud prevention.
    
    The system evaluates multiple risk factors:
    - High-value transactions that may be targets for fraud
    - Multiple servicing transfers indicating potential laundering
    - Rapid document modifications suggesting tampering
    - Unusual access patterns indicating insider threats
    - Missing attestations indicating compliance gaps
    
    Example Usage:
        detector = AnomalyDetector()
        risk_analysis = detector.analyze_loan_risk(loan_data, audit_history)
        print(f"Risk Level: {risk_analysis['risk_level']}")
        print(f"Risk Score: {risk_analysis['risk_score']}/100")
    """
    
    def __init__(self):
        """
        Initialize the AnomalyDetector with risk factor weights.
        
        The weights are calibrated based on historical fraud patterns and represent
        the relative importance of each risk factor in predicting fraud likelihood.
        """
        # Risk factor weights (must sum to 1.0)
        self.risk_weights = {
            'high_value': 0.30,           # High-value loans are prime fraud targets
            'multiple_transfers': 0.20,   # Multiple transfers suggest laundering
            'rapid_modifications': 0.25,  # Rapid changes indicate tampering
            'unusual_access_pattern': 0.15, # After-hours access suggests insider threat
            'missing_attestations': 0.10   # Missing attestations indicate compliance gaps
        }
        
        # Validate weights sum to 1.0
        total_weight = sum(self.risk_weights.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Risk weights must sum to 1.0, got {total_weight}")
        
        try:
            self.walacor_service = WalacorIntegrityService()
            print("✅ AnomalyDetector initialized with AI-powered fraud prediction capabilities!")
        except Exception as e:
            print(f"⚠️  AnomalyDetector initialized in offline mode: {e}")
            self.walacor_service = None
    
    def analyze_loan_risk(self, loan_data: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze loan risk and predict potential fraud scenarios.
        
        This method performs comprehensive risk analysis by evaluating multiple
        risk factors and generating intelligent predictions about potential
        fraud scenarios. It provides actionable recommendations to prevent
        fraud before it occurs.
        
        Args:
            loan_data (Dict[str, Any]): Loan information including:
                - loan_amount: The loan amount in dollars
                - loan_id: Unique identifier for the loan
                - expected_attestations: Number of required attestations
                - other loan metadata
            history (List[Dict[str, Any]]): Audit history including:
                - timestamp: When each event occurred
                - event_type: Type of event (transfer, modification, access, etc.)
                - user: Who performed the action
                - details: Additional event details
        
        Returns:
            Dict[str, Any]: Comprehensive risk analysis containing:
                - risk_score: Overall risk score (0-100)
                - risk_level: Risk level category (LOW/MEDIUM/HIGH/CRITICAL)
                - risk_factors: Individual risk factor scores
                - recommendations: List of actionable recommendations
                - fraud_predictions: Predicted fraud scenarios with probabilities
                - analysis_timestamp: When the analysis was performed
        """
        print(f"\n🤖 Starting AI-powered risk analysis for loan: {loan_data.get('loan_id', 'Unknown')}")
        
        # Calculate individual risk factors
        risk_factors = self._calculate_risk_factors(loan_data, history)
        
        # Calculate weighted risk score
        risk_score = self._calculate_weighted_risk_score(risk_factors)
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_score)
        
        # Generate intelligent recommendations
        recommendations = self._generate_recommendations(risk_score, risk_factors)
        
        # Predict fraud scenarios
        fraud_predictions = self._predict_fraud_scenarios(risk_factors)
        
        # Create comprehensive analysis result
        analysis_result = {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'fraud_predictions': fraud_predictions,
            'analysis_timestamp': datetime.now().isoformat(),
            'loan_id': loan_data.get('loan_id', 'Unknown'),
            'analysis_summary': self._generate_analysis_summary(risk_score, risk_level, fraud_predictions)
        }
        
        print(f"✅ Risk analysis completed: {risk_level} (Score: {risk_score:.1f}/100)")
        return analysis_result
    
    def _calculate_risk_factors(self, loan_data: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate individual risk factor scores based on loan data and history.
        
        Args:
            loan_data: Loan information
            history: Audit history events
            
        Returns:
            Dict[str, float]: Risk factor scores (0.0 to 1.0)
        """
        risk_factors = {}
        
        # 1. High Value Risk (0.0 to 1.0)
        loan_amount = loan_data.get('loan_amount', 0)
        risk_factors['high_value'] = 1.0 if loan_amount > 1_000_000 else 0.0
        
        # 2. Multiple Transfers Risk (0.0 to 1.0)
        transfer_count = sum(1 for event in history if 'transfer' in event.get('event_type', '').lower())
        risk_factors['multiple_transfers'] = min(transfer_count / 5.0, 1.0)
        
        # 3. Rapid Modifications Risk (0.0 to 1.0)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_modifications = sum(1 for event in history 
                                 if 'modification' in event.get('event_type', '').lower() and
                                 self._parse_timestamp(event.get('timestamp', '')) > seven_days_ago)
        risk_factors['rapid_modifications'] = min(recent_modifications / 10.0, 1.0)
        
        # 4. Unusual Access Pattern Risk (0.0 to 1.0)
        after_hours_access = sum(1 for event in history 
                               if self._is_after_hours(event.get('timestamp', '')))
        risk_factors['unusual_access_pattern'] = min(after_hours_access / 5.0, 1.0)
        
        # 5. Missing Attestations Risk (0.0 to 1.0)
        expected_attestations = loan_data.get('expected_attestations', 3)
        actual_attestations = sum(1 for event in history 
                                if 'attestation' in event.get('event_type', '').lower())
        if expected_attestations > 0:
            risk_factors['missing_attestations'] = max(0.0, (expected_attestations - actual_attestations) / expected_attestations)
        else:
            risk_factors['missing_attestations'] = 0.0
        
        print("📊 Risk factors calculated:")
        for factor, score in risk_factors.items():
            print(f"   {factor}: {score:.2f}")
        
        return risk_factors
    
    def _calculate_weighted_risk_score(self, risk_factors: Dict[str, float]) -> float:
        """
        Calculate weighted risk score from individual risk factors.
        
        Args:
            risk_factors: Individual risk factor scores
            
        Returns:
            float: Weighted risk score (0-100)
        """
        weighted_score = 0.0
        for factor, score in risk_factors.items():
            weight = self.risk_weights.get(factor, 0.0)
            weighted_score += score * weight
        
        # Convert to 0-100 scale
        final_score = weighted_score * 100
        print(f"🎯 Weighted risk score: {final_score:.1f}/100")
        return final_score
    
    def _get_risk_level(self, score: float) -> str:
        """
        Determine risk level category based on risk score.
        
        Args:
            score: Risk score (0-100)
            
        Returns:
            str: Risk level with emoji indicator
        """
        if score < 20:
            return "🟢 LOW"
        elif score < 50:
            return "🟡 MEDIUM"
        elif score < 75:
            return "🟠 HIGH"
        else:
            return "🔴 CRITICAL"
    
    def _generate_recommendations(self, risk_score: float, risk_factors: Dict[str, float]) -> List[str]:
        """
        Generate intelligent, actionable recommendations based on risk analysis.
        
        Args:
            risk_score: Overall risk score
            risk_factors: Individual risk factor scores
            
        Returns:
            List[str]: List of actionable recommendations
        """
        recommendations = []
        
        # Base recommendations on overall risk score
        if risk_score >= 75:
            recommendations.extend([
                "🚨 URGENT: Freeze loan modifications pending investigation",
                "🔒 Require executive approval for any loan changes",
                "👥 Assign dedicated compliance officer to monitor this loan",
                "📞 Notify legal team of potential fraud indicators"
            ])
        elif risk_score >= 50:
            recommendations.extend([
                "⚠️ Flag for manual review by compliance team",
                "💰 Require dual authorization for modifications",
                "🔍 Enable real-time monitoring for this loan",
                "📋 Schedule weekly compliance review meetings"
            ])
        elif risk_score >= 20:
            recommendations.extend([
                "🔍 Enable real-time monitoring for this loan",
                "📊 Increase audit frequency to weekly",
                "👤 Assign senior underwriter for oversight"
            ])
        else:
            recommendations.extend([
                "✅ Continue standard monitoring procedures",
                "📅 Schedule quarterly compliance review"
            ])
        
        # Factor-specific recommendations
        if risk_factors.get('high_value', 0) > 0.5:
            recommendations.append("💎 Implement enhanced due diligence for high-value loan")
        
        if risk_factors.get('multiple_transfers', 0) > 0.5:
            recommendations.append("🔄 Investigate servicing transfer history for potential laundering")
        
        if risk_factors.get('rapid_modifications', 0) > 0.5:
            recommendations.append("⚡ Review recent modifications for unauthorized changes")
        
        if risk_factors.get('unusual_access_pattern', 0) > 0.5:
            recommendations.append("🕐 Investigate after-hours access patterns for insider threats")
        
        if risk_factors.get('missing_attestations', 0) > 0.5:
            recommendations.append("📝 Complete missing attestations to ensure compliance")
        
        return recommendations
    
    def _predict_fraud_scenarios(self, risk_factors: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Predict specific fraud scenarios based on risk factors.
        
        Args:
            risk_factors: Individual risk factor scores
            
        Returns:
            List[Dict[str, Any]]: Predicted fraud scenarios with probabilities
        """
        scenarios = []
        
        # Loan Amount Inflation Fraud
        if risk_factors.get('high_value', 0) > 0.5 and risk_factors.get('rapid_modifications', 0) > 0.5:
            probability = (risk_factors['high_value'] + risk_factors['rapid_modifications']) / 2 * 100
            scenarios.append({
                'scenario_name': 'Loan Amount Inflation',
                'probability': round(probability, 1),
                'description': 'Fraudster inflates loan amount through rapid document modifications',
                'watch_fields': ['loan_amount', 'document_modifications', 'approval_chain'],
                'risk_indicators': ['High value loan', 'Rapid modifications', 'Missing approvals']
            })
        
        # Servicing Transfer Fraud
        if risk_factors.get('multiple_transfers', 0) > 0.7:
            probability = risk_factors['multiple_transfers'] * 100
            scenarios.append({
                'scenario_name': 'Servicing Transfer Fraud',
                'probability': round(probability, 1),
                'description': 'Multiple transfers used to obscure loan ownership and evade detection',
                'watch_fields': ['servicing_transfers', 'transfer_timeline', 'beneficiary_changes'],
                'risk_indicators': ['Multiple transfers', 'Short transfer intervals', 'Unusual beneficiaries']
            })
        
        # Insider Threat
        if risk_factors.get('unusual_access_pattern', 0) > 0.6:
            probability = risk_factors['unusual_access_pattern'] * 100
            scenarios.append({
                'scenario_name': 'Insider Threat',
                'probability': round(probability, 1),
                'description': 'Internal user accessing documents outside normal hours for unauthorized purposes',
                'watch_fields': ['access_logs', 'user_behavior', 'privilege_escalation'],
                'risk_indicators': ['After-hours access', 'Unusual user patterns', 'Privilege abuse']
            })
        
        # Document Tampering
        if risk_factors.get('rapid_modifications', 0) > 0.8:
            probability = risk_factors['rapid_modifications'] * 100
            scenarios.append({
                'scenario_name': 'Document Tampering',
                'probability': round(probability, 1),
                'description': 'Systematic modification of loan documents to hide fraudulent activities',
                'watch_fields': ['document_versions', 'modification_history', 'integrity_checks'],
                'risk_indicators': ['Rapid modifications', 'Version discrepancies', 'Failed integrity checks']
            })
        
        # Compliance Evasion
        if risk_factors.get('missing_attestations', 0) > 0.7:
            probability = risk_factors['missing_attestations'] * 100
            scenarios.append({
                'scenario_name': 'Compliance Evasion',
                'probability': round(probability, 1),
                'description': 'Deliberate avoidance of required attestations to bypass compliance checks',
                'watch_fields': ['attestation_status', 'compliance_timeline', 'regulatory_requirements'],
                'risk_indicators': ['Missing attestations', 'Delayed compliance', 'Regulatory gaps']
            })
        
        # Sort scenarios by probability (highest first)
        scenarios.sort(key=lambda x: x['probability'], reverse=True)
        
        print(f"🔮 Predicted {len(scenarios)} fraud scenarios")
        return scenarios
    
    def _is_after_hours(self, timestamp: str) -> bool:
        """
        Check if a timestamp represents after-hours access.
        
        Args:
            timestamp: ISO format timestamp string
            
        Returns:
            bool: True if access was before 6am or after 6pm
        """
        try:
            if not timestamp:
                return False
            
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = dt.hour
            return hour < 6 or hour >= 18
        except (ValueError, AttributeError):
            return False
    
    def _parse_timestamp(self, timestamp: str) -> datetime:
        """
        Parse timestamp string to datetime object.
        
        Args:
            timestamp: ISO format timestamp string
            
        Returns:
            datetime: Parsed datetime object, or epoch if parsing fails
        """
        try:
            if not timestamp:
                return datetime.fromtimestamp(0)
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return datetime.fromtimestamp(0)
    
    def _generate_analysis_summary(self, risk_score: float, _risk_level: str, fraud_predictions: List[Dict[str, Any]]) -> str:
        """
        Generate a human-readable summary of the risk analysis.
        
        Args:
            risk_score: Overall risk score
            risk_level: Risk level category
            fraud_predictions: List of predicted fraud scenarios
            
        Returns:
            str: Summary of the analysis
        """
        if risk_score >= 75:
            return f"CRITICAL RISK: This loan shows multiple indicators of potential fraud. {len(fraud_predictions)} fraud scenarios identified. Immediate action required."
        elif risk_score >= 50:
            return f"HIGH RISK: This loan requires enhanced monitoring. {len(fraud_predictions)} potential fraud scenarios detected. Review recommended."
        elif risk_score >= 20:
            return f"MEDIUM RISK: This loan shows some risk indicators. {len(fraud_predictions)} potential scenarios identified. Standard monitoring with increased frequency."
        else:
            return "LOW RISK: This loan appears to be operating within normal parameters. No significant fraud indicators detected."
    
    def get_risk_weights(self) -> Dict[str, float]:
        """
        Get the current risk factor weights.
        
        Returns:
            Dict[str, float]: Current risk factor weights
        """
        return self.risk_weights.copy()
    
    def update_risk_weights(self, new_weights: Dict[str, float]) -> None:
        """
        Update risk factor weights (must sum to 1.0).
        
        Args:
            new_weights: New risk factor weights
            
        Raises:
            ValueError: If weights don't sum to 1.0 or contain invalid factors
        """
        # Validate weights sum to 1.0
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Risk weights must sum to 1.0, got {total_weight}")
        
        # Validate all required factors are present
        required_factors = set(self.risk_weights.keys())
        provided_factors = set(new_weights.keys())
        if required_factors != provided_factors:
            missing = required_factors - provided_factors
            extra = provided_factors - required_factors
            error_msg = []
            if missing:
                error_msg.append(f"Missing factors: {missing}")
            if extra:
                error_msg.append(f"Extra factors: {extra}")
            raise ValueError(f"Invalid risk factors: {'; '.join(error_msg)}")
        
        self.risk_weights = new_weights.copy()
        print(f"✅ Risk weights updated: {self.risk_weights}")
