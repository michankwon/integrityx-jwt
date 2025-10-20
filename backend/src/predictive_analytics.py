"""
Predictive Analytics & Machine Learning Service

This service provides advanced predictive analytics and machine learning capabilities
for document integrity, compliance forecasting, and risk assessment.
"""

import logging
import json
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import os

logger = logging.getLogger(__name__)

@dataclass
class RiskPrediction:
    """Risk prediction result."""
    document_id: str
    risk_score: float  # 0.0 to 1.0
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float  # 0.0 to 1.0
    factors: List[str]
    recommendations: List[str]
    predicted_at: datetime

@dataclass
class ComplianceForecast:
    """Compliance forecast result."""
    document_id: str
    compliance_probability: float  # 0.0 to 1.0
    forecast_status: str  # PASS, FAIL, REVIEW_REQUIRED
    confidence: float  # 0.0 to 1.0
    risk_factors: List[str]
    recommendations: List[str]
    forecasted_at: datetime

@dataclass
class PerformancePrediction:
    """Performance prediction result."""
    metric_name: str
    current_value: float
    predicted_value: float
    trend: str  # IMPROVING, STABLE, DEGRADING
    confidence: float
    recommendations: List[str]
    predicted_at: datetime

class PredictiveAnalyticsService:
    """
    Advanced predictive analytics and machine learning service.
    
    Provides risk prediction, compliance forecasting, and performance optimization
    using machine learning models trained on historical data.
    """
    
    def __init__(self, db_service=None):
        """Initialize the predictive analytics service."""
        self.db_service = db_service
        self.models = {}
        self.scalers = {}
        self.model_path = "models"
        
        # Create models directory if it doesn't exist
        os.makedirs(self.model_path, exist_ok=True)
        
        # Initialize models
        self._initialize_models()
        
        logger.info("✅ Predictive Analytics service initialized")
    
    def _initialize_models(self):
        """Initialize machine learning models."""
        try:
            # Risk prediction model
            self.models['risk_prediction'] = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10
            )
            
            # Compliance forecasting model
            self.models['compliance_forecast'] = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=8
            )
            
            # Anomaly detection model
            self.models['anomaly_detection'] = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            
            # Performance prediction model
            self.models['performance_prediction'] = RandomForestClassifier(
                n_estimators=50,
                random_state=42,
                max_depth=6
            )
            
            # Initialize scalers
            self.scalers['risk_prediction'] = StandardScaler()
            self.scalers['compliance_forecast'] = StandardScaler()
            self.scalers['performance_prediction'] = StandardScaler()
            
            # Load pre-trained models if available
            self._load_models()
            
            logger.info("✅ ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
            raise
    
    def _load_models(self):
        """Load pre-trained models from disk."""
        try:
            for model_name in self.models.keys():
                model_file = os.path.join(self.model_path, f"{model_name}.joblib")
                scaler_file = os.path.join(self.model_path, f"{model_name}_scaler.joblib")
                
                if os.path.exists(model_file):
                    self.models[model_name] = joblib.load(model_file)
                    logger.info(f"✅ Loaded pre-trained {model_name} model")
                
                if os.path.exists(scaler_file):
                    self.scalers[model_name] = joblib.load(scaler_file)
                    logger.info(f"✅ Loaded {model_name} scaler")
                    
        except Exception as e:
            logger.warning(f"Could not load pre-trained models: {e}")
    
    def _save_models(self):
        """Save trained models to disk."""
        try:
            for model_name, model in self.models.items():
                model_file = os.path.join(self.model_path, f"{model_name}.joblib")
                joblib.dump(model, model_file)
                
                if model_name in self.scalers:
                    scaler_file = os.path.join(self.model_path, f"{model_name}_scaler.joblib")
                    joblib.dump(self.scalers[model_name], scaler_file)
            
            logger.info("✅ Models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    def _extract_features(self, document_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from document data for ML models."""
        try:
            features = []
            
            # Document size features
            features.append(document_data.get('file_size', 0))
            features.append(document_data.get('content_length', 0))
            
            # Timestamp features
            created_at = document_data.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                features.extend([
                    created_at.hour,
                    created_at.weekday(),
                    created_at.month
                ])
            else:
                features.extend([0, 0, 0])
            
            # Hash features (simplified)
            hash_value = document_data.get('payload_sha256', '')
            features.append(len(hash_value))
            features.append(hash(hash_value) % 1000)  # Hash-based feature
            
            # Attestation features
            attestations = document_data.get('attestations', [])
            features.append(len(attestations))
            features.append(sum(1 for att in attestations if att.get('status') == 'verified'))
            
            # Provenance features
            provenance_links = document_data.get('provenance_links', [])
            features.append(len(provenance_links))
            
            # Event features
            events = document_data.get('events', [])
            features.append(len(events))
            features.append(sum(1 for event in events if event.get('event_type') == 'verification'))
            
            # Fill missing features with zeros
            while len(features) < 15:  # Ensure consistent feature count
                features.append(0)
            
            return np.array(features[:15]).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Failed to extract features: {e}")
            return np.zeros((1, 15))
    
    def predict_document_risk(self, document_id: str, document_data: Dict[str, Any]) -> RiskPrediction:
        """
        Predict the risk level of a document using ML models.
        
        Args:
            document_id: The document ID
            document_data: Document metadata and features
            
        Returns:
            RiskPrediction object with risk assessment
        """
        try:
            # Extract features
            features = self._extract_features(document_data)
            
            # Scale features
            if 'risk_prediction' in self.scalers:
                features = self.scalers['risk_prediction'].transform(features)
            
            # Predict risk score
            risk_score = 0.5  # Default score
            confidence = 0.7  # Default confidence
            
            if hasattr(self.models['risk_prediction'], 'predict_proba'):
                try:
                    proba = self.models['risk_prediction'].predict_proba(features)
                    if len(proba[0]) >= 2:
                        risk_score = proba[0][1]  # Probability of high risk
                        confidence = max(proba[0])
                except:
                    pass
            
            # Determine risk level
            if risk_score >= 0.8:
                risk_level = "CRITICAL"
            elif risk_score >= 0.6:
                risk_level = "HIGH"
            elif risk_score >= 0.4:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            # Generate risk factors
            factors = []
            if document_data.get('file_size', 0) > 1000000:  # Large file
                factors.append("Large file size")
            if len(document_data.get('attestations', [])) == 0:
                factors.append("No attestations")
            if len(document_data.get('provenance_links', [])) == 0:
                factors.append("No provenance links")
            if document_data.get('created_at'):
                created_at = document_data['created_at']
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if created_at.hour < 6 or created_at.hour > 22:
                    factors.append("Unusual creation time")
            
            # Generate recommendations
            recommendations = []
            if risk_level in ["HIGH", "CRITICAL"]:
                recommendations.append("Manual review recommended")
                recommendations.append("Additional verification required")
            if "No attestations" in factors:
                recommendations.append("Create document attestations")
            if "No provenance links" in factors:
                recommendations.append("Establish provenance tracking")
            
            result = RiskPrediction(
                document_id=document_id,
                risk_score=risk_score,
                risk_level=risk_level,
                confidence=confidence,
                factors=factors,
                recommendations=recommendations,
                predicted_at=datetime.now(timezone.utc)
            )
            
            logger.info(f"✅ Risk prediction completed for document {document_id}: {risk_level}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to predict document risk: {e}")
            # Return default prediction
            return RiskPrediction(
                document_id=document_id,
                risk_score=0.5,
                risk_level="MEDIUM",
                confidence=0.5,
                factors=["Prediction failed"],
                recommendations=["Manual review required"],
                predicted_at=datetime.now(timezone.utc)
            )
    
    def forecast_compliance(self, document_id: str, document_data: Dict[str, Any]) -> ComplianceForecast:
        """
        Forecast compliance status for a document.
        
        Args:
            document_id: The document ID
            document_data: Document metadata and features
            
        Returns:
            ComplianceForecast object with compliance prediction
        """
        try:
            # Extract features
            features = self._extract_features(document_data)
            
            # Scale features
            if 'compliance_forecast' in self.scalers:
                features = self.scalers['compliance_forecast'].transform(features)
            
            # Predict compliance probability
            compliance_probability = 0.8  # Default probability
            confidence = 0.7  # Default confidence
            
            if hasattr(self.models['compliance_forecast'], 'predict_proba'):
                try:
                    proba = self.models['compliance_forecast'].predict_proba(features)
                    if len(proba[0]) >= 2:
                        compliance_probability = proba[0][1]  # Probability of compliance
                        confidence = max(proba[0])
                except:
                    pass
            
            # Determine forecast status
            if compliance_probability >= 0.8:
                forecast_status = "PASS"
            elif compliance_probability >= 0.6:
                forecast_status = "REVIEW_REQUIRED"
            else:
                forecast_status = "FAIL"
            
            # Generate risk factors
            risk_factors = []
            if len(document_data.get('attestations', [])) < 2:
                risk_factors.append("Insufficient attestations")
            if document_data.get('file_size', 0) > 5000000:  # Very large file
                risk_factors.append("File size exceeds limits")
            if len(document_data.get('events', [])) < 3:
                risk_factors.append("Limited audit trail")
            
            # Generate recommendations
            recommendations = []
            if forecast_status == "FAIL":
                recommendations.append("Document requires significant changes")
                recommendations.append("Consult compliance team")
            elif forecast_status == "REVIEW_REQUIRED":
                recommendations.append("Additional verification needed")
                recommendations.append("Review document metadata")
            else:
                recommendations.append("Document appears compliant")
                recommendations.append("Proceed with standard processing")
            
            result = ComplianceForecast(
                document_id=document_id,
                compliance_probability=compliance_probability,
                forecast_status=forecast_status,
                confidence=confidence,
                risk_factors=risk_factors,
                recommendations=recommendations,
                forecasted_at=datetime.now(timezone.utc)
            )
            
            logger.info(f"✅ Compliance forecast completed for document {document_id}: {forecast_status}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to forecast compliance: {e}")
            # Return default forecast
            return ComplianceForecast(
                document_id=document_id,
                compliance_probability=0.5,
                forecast_status="REVIEW_REQUIRED",
                confidence=0.5,
                risk_factors=["Forecast failed"],
                recommendations=["Manual review required"],
                forecasted_at=datetime.now(timezone.utc)
            )
    
    def predict_performance(self, metric_name: str, historical_data: List[float]) -> PerformancePrediction:
        """
        Predict future performance for a given metric.
        
        Args:
            metric_name: Name of the performance metric
            historical_data: Historical values of the metric
            
        Returns:
            PerformancePrediction object with performance forecast
        """
        try:
            if len(historical_data) < 3:
                # Not enough data for prediction
                return PerformancePrediction(
                    metric_name=metric_name,
                    current_value=historical_data[-1] if historical_data else 0,
                    predicted_value=historical_data[-1] if historical_data else 0,
                    trend="STABLE",
                    confidence=0.3,
                    recommendations=["Insufficient data for prediction"],
                    predicted_at=datetime.now(timezone.utc)
                )
            
            current_value = historical_data[-1]
            
            # Simple trend analysis
            recent_values = historical_data[-5:] if len(historical_data) >= 5 else historical_data
            if len(recent_values) >= 2:
                trend_slope = (recent_values[-1] - recent_values[0]) / len(recent_values)
                if trend_slope > 0.1:
                    trend = "IMPROVING"
                elif trend_slope < -0.1:
                    trend = "DEGRADING"
                else:
                    trend = "STABLE"
            else:
                trend = "STABLE"
            
            # Simple prediction (moving average with trend)
            predicted_value = current_value
            if trend == "IMPROVING":
                predicted_value = current_value * 1.05
            elif trend == "DEGRADING":
                predicted_value = current_value * 0.95
            
            # Generate recommendations
            recommendations = []
            if trend == "DEGRADING":
                recommendations.append("Performance is declining")
                recommendations.append("Investigate root causes")
                recommendations.append("Consider optimization")
            elif trend == "IMPROVING":
                recommendations.append("Performance is improving")
                recommendations.append("Monitor for consistency")
            else:
                recommendations.append("Performance is stable")
                recommendations.append("Continue current practices")
            
            result = PerformancePrediction(
                metric_name=metric_name,
                current_value=current_value,
                predicted_value=predicted_value,
                trend=trend,
                confidence=0.8,
                recommendations=recommendations,
                predicted_at=datetime.now(timezone.utc)
            )
            
            logger.info(f"✅ Performance prediction completed for {metric_name}: {trend}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to predict performance: {e}")
            return PerformancePrediction(
                metric_name=metric_name,
                current_value=0,
                predicted_value=0,
                trend="STABLE",
                confidence=0.3,
                recommendations=["Prediction failed"],
                predicted_at=datetime.now(timezone.utc)
            )
    
    def detect_anomalies(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in a dataset using ML models.
        
        Args:
            data_points: List of data points to analyze
            
        Returns:
            List of detected anomalies
        """
        try:
            if len(data_points) < 10:
                return []
            
            # Extract features for anomaly detection
            features = []
            for point in data_points:
                feature_vector = self._extract_features(point)
                features.append(feature_vector.flatten())
            
            features = np.array(features)
            
            # Detect anomalies
            anomaly_scores = self.models['anomaly_detection'].decision_function(features)
            anomaly_predictions = self.models['anomaly_detection'].predict(features)
            
            # Identify anomalies
            anomalies = []
            for i, (score, prediction) in enumerate(zip(anomaly_scores, anomaly_predictions)):
                if prediction == -1:  # Anomaly detected
                    anomalies.append({
                        'index': i,
                        'data_point': data_points[i],
                        'anomaly_score': float(score),
                        'severity': 'HIGH' if score < -0.5 else 'MEDIUM',
                        'detected_at': datetime.now(timezone.utc).isoformat()
                    })
            
            logger.info(f"✅ Anomaly detection completed: {len(anomalies)} anomalies found")
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []
    
    def get_trend_analysis(self, metric_name: str, time_series_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform trend analysis on time series data.
        
        Args:
            metric_name: Name of the metric
            time_series_data: Time series data points
            
        Returns:
            Trend analysis results
        """
        try:
            if len(time_series_data) < 3:
                return {
                    'metric_name': metric_name,
                    'trend': 'INSUFFICIENT_DATA',
                    'change_percentage': 0,
                    'confidence': 0.3,
                    'recommendations': ['Insufficient data for trend analysis']
                }
            
            # Extract values and timestamps
            values = [point.get('value', 0) for point in time_series_data]
            timestamps = [point.get('timestamp', '') for point in time_series_data]
            
            # Calculate trend
            if len(values) >= 2:
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)
                
                change_percentage = ((second_avg - first_avg) / first_avg * 100) if first_avg != 0 else 0
                
                if change_percentage > 10:
                    trend = 'INCREASING'
                elif change_percentage < -10:
                    trend = 'DECREASING'
                else:
                    trend = 'STABLE'
            else:
                trend = 'STABLE'
                change_percentage = 0
            
            # Generate recommendations
            recommendations = []
            if trend == 'INCREASING':
                recommendations.append("Metric is trending upward")
                recommendations.append("Monitor for potential issues")
            elif trend == 'DECREASING':
                recommendations.append("Metric is trending downward")
                recommendations.append("Investigate causes")
            else:
                recommendations.append("Metric is stable")
                recommendations.append("Continue monitoring")
            
            result = {
                'metric_name': metric_name,
                'trend': trend,
                'change_percentage': round(change_percentage, 2),
                'confidence': 0.8,
                'recommendations': recommendations,
                'data_points': len(values),
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Trend analysis completed for {metric_name}: {trend}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to perform trend analysis: {e}")
            return {
                'metric_name': metric_name,
                'trend': 'ERROR',
                'change_percentage': 0,
                'confidence': 0.3,
                'recommendations': ['Trend analysis failed'],
                'error': str(e)
            }
    
    def train_models(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train ML models with new data.
        
        Args:
            training_data: Training dataset
            
        Returns:
            Training results
        """
        try:
            if len(training_data) < 20:
                return {
                    'status': 'INSUFFICIENT_DATA',
                    'message': 'At least 20 data points required for training',
                    'data_points': len(training_data)
                }
            
            # Prepare training data
            X = []
            y_risk = []
            y_compliance = []
            
            for data_point in training_data:
                features = self._extract_features(data_point)
                X.append(features.flatten())
                
                # Risk labels (simplified)
                risk_score = data_point.get('risk_score', 0.5)
                y_risk.append(1 if risk_score > 0.6 else 0)
                
                # Compliance labels (simplified)
                compliance_status = data_point.get('compliance_status', 'PASS')
                y_compliance.append(1 if compliance_status == 'PASS' else 0)
            
            X = np.array(X)
            y_risk = np.array(y_risk)
            y_compliance = np.array(y_compliance)
            
            # Split data
            X_train, X_test, y_risk_train, y_risk_test = train_test_split(
                X, y_risk, test_size=0.2, random_state=42
            )
            _, _, y_compliance_train, y_compliance_test = train_test_split(
                X, y_compliance, test_size=0.2, random_state=42
            )
            
            # Scale features
            self.scalers['risk_prediction'].fit(X_train)
            self.scalers['compliance_forecast'].fit(X_train)
            
            X_train_scaled = self.scalers['risk_prediction'].transform(X_train)
            X_test_scaled = self.scalers['risk_prediction'].transform(X_test)
            
            # Train risk prediction model
            self.models['risk_prediction'].fit(X_train_scaled, y_risk_train)
            risk_predictions = self.models['risk_prediction'].predict(X_test_scaled)
            risk_accuracy = accuracy_score(y_risk_test, risk_predictions)
            
            # Train compliance forecast model
            self.models['compliance_forecast'].fit(X_train_scaled, y_compliance_train)
            compliance_predictions = self.models['compliance_forecast'].predict(X_test_scaled)
            compliance_accuracy = accuracy_score(y_compliance_test, compliance_predictions)
            
            # Train anomaly detection model
            self.models['anomaly_detection'].fit(X)
            
            # Save models
            self._save_models()
            
            result = {
                'status': 'SUCCESS',
                'message': 'Models trained successfully',
                'training_data_points': len(training_data),
                'test_data_points': len(X_test),
                'risk_prediction_accuracy': round(risk_accuracy, 3),
                'compliance_forecast_accuracy': round(compliance_accuracy, 3),
                'trained_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Models trained successfully: Risk accuracy={risk_accuracy:.3f}, Compliance accuracy={compliance_accuracy:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to train models: {e}")
            return {
                'status': 'ERROR',
                'message': f'Training failed: {str(e)}',
                'data_points': len(training_data) if training_data else 0
            }
    
    def get_model_statistics(self) -> Dict[str, Any]:
        """Get statistics about the ML models."""
        try:
            stats = {
                'models_available': list(self.models.keys()),
                'scalers_available': list(self.scalers.keys()),
                'model_path': self.model_path,
                'models_loaded': {},
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
            # Check which models are loaded
            for model_name, model in self.models.items():
                stats['models_loaded'][model_name] = {
                    'type': type(model).__name__,
                    'fitted': hasattr(model, 'feature_importances_') or hasattr(model, 'decision_function_')
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get model statistics: {e}")
            return {
                'error': str(e),
                'models_available': [],
                'scalers_available': []
            }

