"""
AI-Powered Anomaly Detection Service

This module provides machine learning-based anomaly detection for document integrity,
compliance monitoring, and system behavior analysis.

Features:
- Document pattern analysis
- Compliance anomaly detection
- System behavior monitoring
- Predictive risk assessment
- Automated alert generation
"""

import json
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import re

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    DOCUMENT_TAMPERING = "document_tampering"
    COMPLIANCE_VIOLATION = "compliance_violation"
    UNUSUAL_ACCESS_PATTERN = "unusual_access_pattern"
    DATA_INCONSISTENCY = "data_inconsistency"
    PERFORMANCE_ANOMALY = "performance_anomaly"
    SECURITY_THREAT = "security_threat"


class SeverityLevel(Enum):
    """Severity levels for detected anomalies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyDetectionResult:
    """Result of anomaly detection analysis."""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    confidence_score: float
    description: str
    detected_at: datetime
    affected_entities: List[str]
    metadata: Dict[str, Any]
    recommendations: List[str]


class AIAnomalyDetector:
    """
    AI-powered anomaly detection service for document integrity and compliance monitoring.
    
    This service uses machine learning algorithms and pattern recognition to identify
    unusual patterns, potential security threats, and compliance violations.
    """
    
    def __init__(self, db_service=None):
        """
        Initialize the AI Anomaly Detector.
        
        Args:
            db_service: Database service for storing detection results
        """
        self.db_service = db_service
        self.detection_history = []
        self.patterns_learned = {}
        self.risk_thresholds = {
            "document_tampering": 0.8,
            "compliance_violation": 0.7,
            "unusual_access_pattern": 0.6,
            "data_inconsistency": 0.75,
            "performance_anomaly": 0.65,
            "security_threat": 0.9
        }
        
        logger.info("✅ AI Anomaly Detector initialized")
    
    def analyze_document_integrity(self, document_data: Dict[str, Any]) -> List[AnomalyDetectionResult]:
        """
        Analyze document for integrity anomalies.
        
        Args:
            document_data: Document metadata and content
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        try:
            # Check for document tampering indicators
            tampering_anomalies = self._detect_document_tampering(document_data)
            anomalies.extend(tampering_anomalies)
            
            # Check for compliance violations
            compliance_anomalies = self._detect_compliance_violations(document_data)
            anomalies.extend(compliance_anomalies)
            
            # Check for data inconsistencies
            inconsistency_anomalies = self._detect_data_inconsistencies(document_data)
            anomalies.extend(inconsistency_anomalies)
            
            # Store detection results
            for anomaly in anomalies:
                self._store_anomaly_result(anomaly)
            
            logger.info(f"✅ Document integrity analysis completed: {len(anomalies)} anomalies detected")
            
        except Exception as e:
            logger.error(f"Failed to analyze document integrity: {e}")
        
        return anomalies
    
    def analyze_access_patterns(self, access_logs: List[Dict[str, Any]]) -> List[AnomalyDetectionResult]:
        """
        Analyze access patterns for unusual behavior.
        
        Args:
            access_logs: List of access log entries
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        try:
            # Analyze access frequency patterns
            frequency_anomalies = self._detect_unusual_access_frequency(access_logs)
            anomalies.extend(frequency_anomalies)
            
            # Analyze access time patterns
            time_anomalies = self._detect_unusual_access_times(access_logs)
            anomalies.extend(time_anomalies)
            
            # Analyze geographic patterns
            geo_anomalies = self._detect_unusual_geographic_access(access_logs)
            anomalies.extend(geo_anomalies)
            
            # Store detection results
            for anomaly in anomalies:
                self._store_anomaly_result(anomaly)
            
            logger.info(f"✅ Access pattern analysis completed: {len(anomalies)} anomalies detected")
            
        except Exception as e:
            logger.error(f"Failed to analyze access patterns: {e}")
        
        return anomalies
    
    def analyze_system_performance(self, performance_metrics: Dict[str, Any]) -> List[AnomalyDetectionResult]:
        """
        Analyze system performance for anomalies.
        
        Args:
            performance_metrics: System performance data
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        try:
            # Check response time anomalies
            response_anomalies = self._detect_response_time_anomalies(performance_metrics)
            anomalies.extend(response_anomalies)
            
            # Check resource usage anomalies
            resource_anomalies = self._detect_resource_usage_anomalies(performance_metrics)
            anomalies.extend(resource_anomalies)
            
            # Check error rate anomalies
            error_anomalies = self._detect_error_rate_anomalies(performance_metrics)
            anomalies.extend(error_anomalies)
            
            # Store detection results
            for anomaly in anomalies:
                self._store_anomaly_result(anomaly)
            
            logger.info(f"✅ System performance analysis completed: {len(anomalies)} anomalies detected")
            
        except Exception as e:
            logger.error(f"Failed to analyze system performance: {e}")
        
        return anomalies
    
    def predict_risk_factors(self, entity_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Predict risk factors for an entity.
        
        Args:
            entity_data: Entity data for risk assessment
            
        Returns:
            Dictionary of risk factors and their scores
        """
        risk_factors = {}
        
        try:
            # Calculate document integrity risk
            risk_factors["document_integrity_risk"] = self._calculate_document_integrity_risk(entity_data)
            
            # Calculate compliance risk
            risk_factors["compliance_risk"] = self._calculate_compliance_risk(entity_data)
            
            # Calculate security risk
            risk_factors["security_risk"] = self._calculate_security_risk(entity_data)
            
            # Calculate operational risk
            risk_factors["operational_risk"] = self._calculate_operational_risk(entity_data)
            
            # Calculate overall risk score
            risk_factors["overall_risk"] = np.mean(list(risk_factors.values()))
            
            logger.info(f"✅ Risk prediction completed: {risk_factors}")
            
        except Exception as e:
            logger.error(f"Failed to predict risk factors: {e}")
            risk_factors = {"error": str(e)}
        
        return risk_factors
    
    def get_anomaly_summary(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """
        Get summary of anomalies detected in the specified time range.
        
        Args:
            time_range_hours: Time range in hours to analyze
            
        Returns:
            Summary of anomalies
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_range_hours)
            
            recent_anomalies = [
                anomaly for anomaly in self.detection_history
                if anomaly.detected_at >= cutoff_time
            ]
            
            summary = {
                "total_anomalies": len(recent_anomalies),
                "by_type": {},
                "by_severity": {},
                "by_confidence": {
                    "high_confidence": len([a for a in recent_anomalies if a.confidence_score >= 0.8]),
                    "medium_confidence": len([a for a in recent_anomalies if 0.6 <= a.confidence_score < 0.8]),
                    "low_confidence": len([a for a in recent_anomalies if a.confidence_score < 0.6])
                },
                "trends": self._calculate_anomaly_trends(recent_anomalies),
                "top_affected_entities": self._get_top_affected_entities(recent_anomalies),
                "recommendations": self._generate_recommendations(recent_anomalies)
            }
            
            # Count by type
            for anomaly in recent_anomalies:
                anomaly_type = anomaly.anomaly_type.value
                summary["by_type"][anomaly_type] = summary["by_type"].get(anomaly_type, 0) + 1
            
            # Count by severity
            for anomaly in recent_anomalies:
                severity = anomaly.severity.value
                summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            logger.info(f"✅ Anomaly summary generated: {summary['total_anomalies']} anomalies in last {time_range_hours}h")
            
        except Exception as e:
            logger.error(f"Failed to generate anomaly summary: {e}")
            summary = {"error": str(e)}
        
        return summary
    
    def _detect_document_tampering(self, document_data: Dict[str, Any]) -> List[AnomalyDetectionResult]:
        """Detect potential document tampering."""
        anomalies = []
        
        try:
            # Check for hash inconsistencies
            if "hash" in document_data and "content" in document_data:
                calculated_hash = hashlib.sha256(document_data["content"].encode()).hexdigest()
                if calculated_hash != document_data["hash"]:
                    anomalies.append(AnomalyDetectionResult(
                        anomaly_id=f"tamper_{hashlib.md5(str(document_data).encode()).hexdigest()[:8]}",
                        anomaly_type=AnomalyType.DOCUMENT_TAMPERING,
                        severity=SeverityLevel.CRITICAL,
                        confidence_score=0.95,
                        description="Document hash mismatch detected - potential tampering",
                        detected_at=datetime.now(timezone.utc),
                        affected_entities=[document_data.get("id", "unknown")],
                        metadata={"expected_hash": document_data["hash"], "calculated_hash": calculated_hash},
                        recommendations=["Immediate investigation required", "Document integrity compromised"]
                    ))
            
            # Check for unusual modification patterns
            if "modification_history" in document_data:
                modifications = document_data["modification_history"]
                if len(modifications) > 10:  # Threshold for unusual activity
                    anomalies.append(AnomalyDetectionResult(
                        anomaly_id=f"mod_activity_{hashlib.md5(str(document_data).encode()).hexdigest()[:8]}",
                        anomaly_type=AnomalyType.DOCUMENT_TAMPERING,
                        severity=SeverityLevel.MEDIUM,
                        confidence_score=0.7,
                        description=f"Unusual modification activity: {len(modifications)} modifications",
                        detected_at=datetime.now(timezone.utc),
                        affected_entities=[document_data.get("id", "unknown")],
                        metadata={"modification_count": len(modifications)},
                        recommendations=["Review modification history", "Verify document authenticity"]
                    ))
        
        except Exception as e:
            logger.error(f"Error detecting document tampering: {e}")
        
        return anomalies
    
    def _detect_compliance_violations(self, document_data: Dict[str, Any]) -> List[AnomalyDetectionResult]:
        """Detect compliance violations."""
        anomalies = []
        
        try:
            # Check for missing required fields
            required_fields = ["id", "type", "created_at", "created_by"]
            missing_fields = [field for field in required_fields if field not in document_data]
            
            if missing_fields:
                anomalies.append(AnomalyDetectionResult(
                    anomaly_id=f"compliance_{hashlib.md5(str(document_data).encode()).hexdigest()[:8]}",
                    anomaly_type=AnomalyType.COMPLIANCE_VIOLATION,
                    severity=SeverityLevel.HIGH,
                    confidence_score=0.9,
                    description=f"Missing required fields: {', '.join(missing_fields)}",
                    detected_at=datetime.now(timezone.utc),
                    affected_entities=[document_data.get("id", "unknown")],
                    metadata={"missing_fields": missing_fields},
                    recommendations=["Add missing required fields", "Update compliance documentation"]
                ))
            
            # Check for data format violations
            if "created_at" in document_data:
                try:
                    datetime.fromisoformat(document_data["created_at"].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    anomalies.append(AnomalyDetectionResult(
                        anomaly_id=f"format_{hashlib.md5(str(document_data).encode()).hexdigest()[:8]}",
                        anomaly_type=AnomalyType.COMPLIANCE_VIOLATION,
                        severity=SeverityLevel.MEDIUM,
                        confidence_score=0.8,
                        description="Invalid date format in created_at field",
                        detected_at=datetime.now(timezone.utc),
                        affected_entities=[document_data.get("id", "unknown")],
                        metadata={"invalid_field": "created_at", "value": document_data["created_at"]},
                        recommendations=["Fix date format", "Validate data entry"]
                    ))
        
        except Exception as e:
            logger.error(f"Error detecting compliance violations: {e}")
        
        return anomalies
    
    def _detect_data_inconsistencies(self, document_data: Dict[str, Any]) -> List[AnomalyDetectionResult]:
        """Detect data inconsistencies."""
        anomalies = []
        
        try:
            # Check for logical inconsistencies
            if "size" in document_data and "content" in document_data:
                actual_size = len(document_data["content"])
                reported_size = document_data["size"]
                
                if abs(actual_size - reported_size) > 100:  # Threshold for size mismatch
                    anomalies.append(AnomalyDetectionResult(
                        anomaly_id=f"size_{hashlib.md5(str(document_data).encode()).hexdigest()[:8]}",
                        anomaly_type=AnomalyType.DATA_INCONSISTENCY,
                        severity=SeverityLevel.MEDIUM,
                        confidence_score=0.75,
                        description=f"Size mismatch: reported {reported_size}, actual {actual_size}",
                        detected_at=datetime.now(timezone.utc),
                        affected_entities=[document_data.get("id", "unknown")],
                        metadata={"reported_size": reported_size, "actual_size": actual_size},
                        recommendations=["Verify document size", "Check data integrity"]
                    ))
        
        except Exception as e:
            logger.error(f"Error detecting data inconsistencies: {e}")
        
        return anomalies
    
    def _detect_unusual_access_frequency(self, access_logs: List[Dict[str, Any]]) -> List[AnomalyDetectionResult]:
        """Detect unusual access frequency patterns."""
        anomalies = []
        
        try:
            # Group by user and count accesses
            user_access_counts = {}
            for log in access_logs:
                user = log.get("user_id", "unknown")
                user_access_counts[user] = user_access_counts.get(user, 0) + 1
            
            # Detect users with unusually high access frequency
            avg_access = np.mean(list(user_access_counts.values())) if user_access_counts else 0
            threshold = avg_access * 3  # 3x average is considered unusual
            
            for user, count in user_access_counts.items():
                if count > threshold:
                    anomalies.append(AnomalyDetectionResult(
                        anomaly_id=f"freq_{hashlib.md5(user.encode()).hexdigest()[:8]}",
                        anomaly_type=AnomalyType.UNUSUAL_ACCESS_PATTERN,
                        severity=SeverityLevel.MEDIUM,
                        confidence_score=0.7,
                        description=f"Unusual access frequency: {count} accesses (avg: {avg_access:.1f})",
                        detected_at=datetime.now(timezone.utc),
                        affected_entities=[user],
                        metadata={"access_count": count, "average": avg_access, "threshold": threshold},
                        recommendations=["Review user access patterns", "Consider access restrictions"]
                    ))
        
        except Exception as e:
            logger.error(f"Error detecting unusual access frequency: {e}")
        
        return anomalies
    
    def _detect_unusual_access_times(self, access_logs: List[Dict[str, Any]]) -> List[AnomalyDetectionResult]:
        """Detect unusual access time patterns."""
        anomalies = []
        
        try:
            # Analyze access times
            access_times = []
            for log in access_logs:
                if "timestamp" in log:
                    try:
                        access_time = datetime.fromisoformat(log["timestamp"].replace('Z', '+00:00'))
                        access_times.append(access_time.hour)
                    except (ValueError, AttributeError):
                        continue
            
            if access_times:
                # Detect off-hours access (outside 9 AM - 5 PM)
                off_hours_access = [hour for hour in access_times if hour < 9 or hour > 17]
                off_hours_ratio = len(off_hours_access) / len(access_times)
                
                if off_hours_ratio > 0.3:  # More than 30% off-hours access
                    anomalies.append(AnomalyDetectionResult(
                        anomaly_id=f"time_{hashlib.md5(str(access_times).encode()).hexdigest()[:8]}",
                        anomaly_type=AnomalyType.UNUSUAL_ACCESS_PATTERN,
                        severity=SeverityLevel.LOW,
                        confidence_score=0.6,
                        description=f"High off-hours access ratio: {off_hours_ratio:.1%}",
                        detected_at=datetime.now(timezone.utc),
                        affected_entities=["system"],
                        metadata={"off_hours_ratio": off_hours_ratio, "total_accesses": len(access_times)},
                        recommendations=["Monitor access patterns", "Review security policies"]
                    ))
        
        except Exception as e:
            logger.error(f"Error detecting unusual access times: {e}")
        
        return anomalies
    
    def _detect_unusual_geographic_access(self, access_logs: List[Dict[str, Any]]) -> List[AnomalyDetectionResult]:
        """Detect unusual geographic access patterns."""
        anomalies = []
        
        try:
            # Group by IP/location
            location_counts = {}
            for log in access_logs:
                location = log.get("ip_address", "unknown")
                location_counts[location] = location_counts.get(location, 0) + 1
            
            # Detect access from unusual locations
            if len(location_counts) > 1:
                most_common_location = max(location_counts, key=location_counts.get)
                most_common_count = location_counts[most_common_location]
                
                for location, count in location_counts.items():
                    if location != most_common_location and count > most_common_count * 0.1:
                        anomalies.append(AnomalyDetectionResult(
                            anomaly_id=f"geo_{hashlib.md5(location.encode()).hexdigest()[:8]}",
                            anomaly_type=AnomalyType.UNUSUAL_ACCESS_PATTERN,
                            severity=SeverityLevel.MEDIUM,
                            confidence_score=0.65,
                            description=f"Access from unusual location: {location} ({count} times)",
                            detected_at=datetime.now(timezone.utc),
                            affected_entities=[location],
                            metadata={"location": location, "access_count": count},
                            recommendations=["Verify location authenticity", "Review access permissions"]
                        ))
        
        except Exception as e:
            logger.error(f"Error detecting unusual geographic access: {e}")
        
        return anomalies
    
    def _detect_response_time_anomalies(self, performance_metrics: Dict[str, Any]) -> List[AnomalyDetectionResult]:
        """Detect response time anomalies."""
        anomalies = []
        
        try:
            response_time = performance_metrics.get("response_time_ms", 0)
            
            # Threshold for slow response (5 seconds)
            if response_time > 5000:
                anomalies.append(AnomalyDetectionResult(
                    anomaly_id=f"response_{hashlib.md5(str(performance_metrics).encode()).hexdigest()[:8]}",
                    anomaly_type=AnomalyType.PERFORMANCE_ANOMALY,
                    severity=SeverityLevel.MEDIUM,
                    confidence_score=0.8,
                    description=f"Slow response time: {response_time}ms",
                    detected_at=datetime.now(timezone.utc),
                    affected_entities=["system"],
                    metadata={"response_time_ms": response_time},
                    recommendations=["Investigate performance bottlenecks", "Optimize system resources"]
                ))
        
        except Exception as e:
            logger.error(f"Error detecting response time anomalies: {e}")
        
        return anomalies
    
    def _detect_resource_usage_anomalies(self, performance_metrics: Dict[str, Any]) -> List[AnomalyDetectionResult]:
        """Detect resource usage anomalies."""
        anomalies = []
        
        try:
            cpu_usage = performance_metrics.get("cpu_usage_percent", 0)
            memory_usage = performance_metrics.get("memory_usage_percent", 0)
            
            # High CPU usage
            if cpu_usage > 90:
                anomalies.append(AnomalyDetectionResult(
                    anomaly_id=f"cpu_{hashlib.md5(str(performance_metrics).encode()).hexdigest()[:8]}",
                    anomaly_type=AnomalyType.PERFORMANCE_ANOMALY,
                    severity=SeverityLevel.HIGH,
                    confidence_score=0.85,
                    description=f"High CPU usage: {cpu_usage}%",
                    detected_at=datetime.now(timezone.utc),
                    affected_entities=["system"],
                    metadata={"cpu_usage_percent": cpu_usage},
                    recommendations=["Scale system resources", "Optimize CPU-intensive operations"]
                ))
            
            # High memory usage
            if memory_usage > 90:
                anomalies.append(AnomalyDetectionResult(
                    anomaly_id=f"memory_{hashlib.md5(str(performance_metrics).encode()).hexdigest()[:8]}",
                    anomaly_type=AnomalyType.PERFORMANCE_ANOMALY,
                    severity=SeverityLevel.HIGH,
                    confidence_score=0.85,
                    description=f"High memory usage: {memory_usage}%",
                    detected_at=datetime.now(timezone.utc),
                    affected_entities=["system"],
                    metadata={"memory_usage_percent": memory_usage},
                    recommendations=["Increase memory allocation", "Optimize memory usage"]
                ))
        
        except Exception as e:
            logger.error(f"Error detecting resource usage anomalies: {e}")
        
        return anomalies
    
    def _detect_error_rate_anomalies(self, performance_metrics: Dict[str, Any]) -> List[AnomalyDetectionResult]:
        """Detect error rate anomalies."""
        anomalies = []
        
        try:
            error_rate = performance_metrics.get("error_rate_percent", 0)
            
            # High error rate
            if error_rate > 5:  # More than 5% error rate
                anomalies.append(AnomalyDetectionResult(
                    anomaly_id=f"error_{hashlib.md5(str(performance_metrics).encode()).hexdigest()[:8]}",
                    anomaly_type=AnomalyType.PERFORMANCE_ANOMALY,
                    severity=SeverityLevel.HIGH,
                    confidence_score=0.9,
                    description=f"High error rate: {error_rate}%",
                    detected_at=datetime.now(timezone.utc),
                    affected_entities=["system"],
                    metadata={"error_rate_percent": error_rate},
                    recommendations=["Investigate error sources", "Implement error handling improvements"]
                ))
        
        except Exception as e:
            logger.error(f"Error detecting error rate anomalies: {e}")
        
        return anomalies
    
    def _calculate_document_integrity_risk(self, entity_data: Dict[str, Any]) -> float:
        """Calculate document integrity risk score."""
        risk_score = 0.0
        
        try:
            # Check for hash mismatches
            if "hash_mismatch" in entity_data:
                risk_score += 0.4
            
            # Check for modification frequency
            if "modification_count" in entity_data:
                if entity_data["modification_count"] > 10:
                    risk_score += 0.3
            
            # Check for access anomalies
            if "unusual_access" in entity_data:
                risk_score += 0.3
        
        except Exception as e:
            logger.error(f"Error calculating document integrity risk: {e}")
        
        return min(risk_score, 1.0)
    
    def _calculate_compliance_risk(self, entity_data: Dict[str, Any]) -> float:
        """Calculate compliance risk score."""
        risk_score = 0.0
        
        try:
            # Check for missing required fields
            if "missing_fields" in entity_data:
                risk_score += 0.4
            
            # Check for format violations
            if "format_violations" in entity_data:
                risk_score += 0.3
            
            # Check for validation failures
            if "validation_failures" in entity_data:
                risk_score += 0.3
        
        except Exception as e:
            logger.error(f"Error calculating compliance risk: {e}")
        
        return min(risk_score, 1.0)
    
    def _calculate_security_risk(self, entity_data: Dict[str, Any]) -> float:
        """Calculate security risk score."""
        risk_score = 0.0
        
        try:
            # Check for unusual access patterns
            if "unusual_access_patterns" in entity_data:
                risk_score += 0.4
            
            # Check for failed authentication attempts
            if "failed_auth_attempts" in entity_data:
                risk_score += 0.3
            
            # Check for privilege escalation attempts
            if "privilege_escalation" in entity_data:
                risk_score += 0.3
        
        except Exception as e:
            logger.error(f"Error calculating security risk: {e}")
        
        return min(risk_score, 1.0)
    
    def _calculate_operational_risk(self, entity_data: Dict[str, Any]) -> float:
        """Calculate operational risk score."""
        risk_score = 0.0
        
        try:
            # Check for performance issues
            if "performance_issues" in entity_data:
                risk_score += 0.4
            
            # Check for system errors
            if "system_errors" in entity_data:
                risk_score += 0.3
            
            # Check for resource constraints
            if "resource_constraints" in entity_data:
                risk_score += 0.3
        
        except Exception as e:
            logger.error(f"Error calculating operational risk: {e}")
        
        return min(risk_score, 1.0)
    
    def _calculate_anomaly_trends(self, anomalies: List[AnomalyDetectionResult]) -> Dict[str, Any]:
        """Calculate anomaly trends."""
        try:
            if not anomalies:
                return {"trend": "stable", "change_percent": 0}
            
            # Group by hour for trend analysis
            hourly_counts = {}
            for anomaly in anomalies:
                hour = anomaly.detected_at.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            
            # Calculate trend (simplified)
            hours = sorted(hourly_counts.keys())
            if len(hours) >= 2:
                recent_avg = np.mean([hourly_counts[h] for h in hours[-3:]])  # Last 3 hours
                earlier_avg = np.mean([hourly_counts[h] for h in hours[:-3]]) if len(hours) > 3 else recent_avg
                
                if earlier_avg > 0:
                    change_percent = ((recent_avg - earlier_avg) / earlier_avg) * 100
                else:
                    change_percent = 0
                
                if change_percent > 20:
                    trend = "increasing"
                elif change_percent < -20:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "stable"
                change_percent = 0
            
            return {"trend": trend, "change_percent": change_percent}
        
        except Exception as e:
            logger.error(f"Error calculating anomaly trends: {e}")
            return {"trend": "unknown", "change_percent": 0}
    
    def _get_top_affected_entities(self, anomalies: List[AnomalyDetectionResult]) -> List[Dict[str, Any]]:
        """Get top affected entities."""
        try:
            entity_counts = {}
            for anomaly in anomalies:
                for entity in anomaly.affected_entities:
                    entity_counts[entity] = entity_counts.get(entity, 0) + 1
            
            # Sort by count and return top 5
            sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
            return [{"entity": entity, "anomaly_count": count} for entity, count in sorted_entities[:5]]
        
        except Exception as e:
            logger.error(f"Error getting top affected entities: {e}")
            return []
    
    def _generate_recommendations(self, anomalies: List[AnomalyDetectionResult]) -> List[str]:
        """Generate recommendations based on detected anomalies."""
        recommendations = []
        
        try:
            # Collect all recommendations from anomalies
            for anomaly in anomalies:
                recommendations.extend(anomaly.recommendations)
            
            # Remove duplicates and return top recommendations
            unique_recommendations = list(set(recommendations))
            return unique_recommendations[:10]  # Top 10 recommendations
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Review system logs for more details"]
    
    def _store_anomaly_result(self, anomaly: AnomalyDetectionResult):
        """Store anomaly detection result."""
        try:
            self.detection_history.append(anomaly)
            
            # Store in database if available
            if self.db_service:
                self.db_service.insert_event(
                    artifact_id=anomaly.anomaly_id,
                    event_type="anomaly_detected",
                    payload_json=json.dumps({
                        "anomaly_type": anomaly.anomaly_type.value,
                        "severity": anomaly.severity.value,
                        "confidence_score": anomaly.confidence_score,
                        "description": anomaly.description,
                        "affected_entities": anomaly.affected_entities,
                        "metadata": anomaly.metadata,
                        "recommendations": anomaly.recommendations
                    }),
                    created_by="ai_anomaly_detector"
                )
        
        except Exception as e:
            logger.error(f"Error storing anomaly result: {e}")

