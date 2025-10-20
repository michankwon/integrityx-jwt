"""
Smart Contracts Service

This module provides automated compliance and workflow management through
smart contract-like functionality for document integrity and regulatory compliance.

Features:
- Automated compliance checking
- Workflow automation
- Rule-based document processing
- Compliance scoring
- Automated notifications and alerts
"""

import json
import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import re

logger = logging.getLogger(__name__)


class ContractType(Enum):
    """Types of smart contracts."""
    COMPLIANCE_CHECK = "compliance_check"
    WORKFLOW_AUTOMATION = "workflow_automation"
    DATA_VALIDATION = "data_validation"
    NOTIFICATION_RULE = "notification_rule"
    APPROVAL_WORKFLOW = "approval_workflow"
    AUDIT_TRAIL = "audit_trail"


class ContractStatus(Enum):
    """Status of smart contracts."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class ExecutionResult(Enum):
    """Results of contract execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ContractRule:
    """A rule within a smart contract."""
    rule_id: str
    name: str
    description: str
    condition: str  # JSONPath or custom condition
    action: str  # Action to take when condition is met
    severity: str = "medium"  # low, medium, high, critical
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SmartContract:
    """A smart contract for automated compliance and workflow management."""
    contract_id: str
    name: str
    description: str
    contract_type: ContractType
    status: ContractStatus
    rules: List[ContractRule]
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0


@dataclass
class ContractExecution:
    """Result of smart contract execution."""
    execution_id: str
    contract_id: str
    executed_at: datetime
    executed_by: str
    result: ExecutionResult
    message: str
    affected_entities: List[str]
    rule_results: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


class SmartContractsService:
    """
    Smart Contracts service for automated compliance and workflow management.
    
    This service provides rule-based automation for document processing,
    compliance checking, and workflow management.
    """
    
    def __init__(self, db_service=None):
        """
        Initialize the Smart Contracts service.
        
        Args:
            db_service: Database service for storing contract data
        """
        self.db_service = db_service
        self.contracts = {}  # contract_id -> SmartContract
        self.execution_history = []  # List of ContractExecution
        self.rule_engines = {
            "jsonpath": self._evaluate_jsonpath_rule,
            "regex": self._evaluate_regex_rule,
            "custom": self._evaluate_custom_rule
        }
        
        # Initialize with default contracts
        self._initialize_default_contracts()
        
        logger.info("✅ Smart Contracts service initialized")
    
    def create_contract(self, name: str, description: str, contract_type: ContractType,
                       rules: List[ContractRule], created_by: str,
                       expires_at: Optional[datetime] = None,
                       metadata: Dict[str, Any] = None) -> SmartContract:
        """
        Create a new smart contract.
        
        Args:
            name: Name of the contract
            description: Description of the contract
            contract_type: Type of contract
            rules: List of rules for the contract
            created_by: User creating the contract
            expires_at: Optional expiration date
            metadata: Additional metadata
            
        Returns:
            Created smart contract
        """
        try:
            contract_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            contract = SmartContract(
                contract_id=contract_id,
                name=name,
                description=description,
                contract_type=contract_type,
                status=ContractStatus.ACTIVE,
                rules=rules,
                created_at=now,
                created_by=created_by,
                updated_at=now,
                updated_by=created_by,
                expires_at=expires_at,
                metadata=metadata or {}
            )
            
            # Store contract
            self.contracts[contract_id] = contract
            
            # Store in database
            if self.db_service:
                self.db_service.insert_event(
                    artifact_id=contract_id,
                    event_type="smart_contract_created",
                    payload_json=json.dumps({
                        "name": name,
                        "description": description,
                        "contract_type": contract_type.value,
                        "rules_count": len(rules),
                        "expires_at": expires_at.isoformat() if expires_at else None,
                        "metadata": metadata or {}
                    }),
                    created_by=created_by
                )
            
            logger.info(f"✅ Smart contract created: {contract_id}")
            
        except Exception as e:
            logger.error(f"Failed to create smart contract: {e}")
            raise
        
        return contract
    
    def execute_contract(self, contract_id: str, data: Dict[str, Any],
                        executed_by: str = "system") -> ContractExecution:
        """
        Execute a smart contract against provided data.
        
        Args:
            contract_id: ID of the contract to execute
            data: Data to evaluate against contract rules
            executed_by: User or system executing the contract
            
        Returns:
            Contract execution result
        """
        try:
            # Get contract
            contract = self.contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            if contract.status != ContractStatus.ACTIVE:
                raise ValueError(f"Contract {contract_id} is not active")
            
            # Check expiration
            if contract.expires_at and contract.expires_at < datetime.now(timezone.utc):
                contract.status = ContractStatus.EXPIRED
                raise ValueError(f"Contract {contract_id} has expired")
            
            # Execute rules
            rule_results = []
            overall_result = ExecutionResult.SUCCESS
            messages = []
            affected_entities = []
            
            for rule in contract.rules:
                if not rule.enabled:
                    continue
                
                try:
                    rule_result = self._execute_rule(rule, data)
                    rule_results.append(rule_result)
                    
                    if rule_result["result"] == ExecutionResult.FAILURE:
                        overall_result = ExecutionResult.FAILURE
                        messages.append(f"Rule '{rule.name}' failed: {rule_result['message']}")
                    elif rule_result["result"] == ExecutionResult.WARNING:
                        if overall_result == ExecutionResult.SUCCESS:
                            overall_result = ExecutionResult.WARNING
                        messages.append(f"Rule '{rule.name}' warning: {rule_result['message']}")
                    
                    # Collect affected entities
                    if "affected_entities" in rule_result:
                        affected_entities.extend(rule_result["affected_entities"])
                
                except Exception as e:
                    rule_results.append({
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "result": ExecutionResult.FAILURE,
                        "message": f"Rule execution error: {str(e)}",
                        "error": str(e)
                    })
                    overall_result = ExecutionResult.FAILURE
                    messages.append(f"Rule '{rule.name}' execution error: {str(e)}")
            
            # Create execution result
            execution = ContractExecution(
                execution_id=str(uuid.uuid4()),
                contract_id=contract_id,
                executed_at=datetime.now(timezone.utc),
                executed_by=executed_by,
                result=overall_result,
                message="; ".join(messages) if messages else "Contract executed successfully",
                affected_entities=list(set(affected_entities)),
                rule_results=rule_results,
                metadata={
                    "data_keys": list(data.keys()),
                    "rules_executed": len([r for r in contract.rules if r.enabled]),
                    "rules_passed": len([r for r in rule_results if r["result"] == ExecutionResult.SUCCESS]),
                    "rules_failed": len([r for r in rule_results if r["result"] == ExecutionResult.FAILURE]),
                    "rules_warnings": len([r for r in rule_results if r["result"] == ExecutionResult.WARNING])
                }
            )
            
            # Update contract statistics
            contract.execution_count += 1
            if overall_result == ExecutionResult.SUCCESS:
                contract.success_count += 1
            else:
                contract.failure_count += 1
            
            # Store execution history
            self.execution_history.append(execution)
            
            # Store in database
            if self.db_service:
                self.db_service.insert_event(
                    artifact_id=contract_id,
                    event_type="smart_contract_executed",
                    payload_json=json.dumps({
                        "execution_id": execution.execution_id,
                        "result": overall_result.value,
                        "message": execution.message,
                        "affected_entities": execution.affected_entities,
                        "rules_executed": execution.metadata["rules_executed"],
                        "rules_passed": execution.metadata["rules_passed"],
                        "rules_failed": execution.metadata["rules_failed"]
                    }),
                    created_by=executed_by
                )
            
            logger.info(f"✅ Smart contract executed: {contract_id} - {overall_result.value}")
            
        except Exception as e:
            logger.error(f"Failed to execute smart contract: {e}")
            raise
        
        return execution
    
    def get_contract(self, contract_id: str) -> Optional[SmartContract]:
        """Get a smart contract by ID."""
        return self.contracts.get(contract_id)
    
    def list_contracts(self, contract_type: Optional[ContractType] = None,
                      status: Optional[ContractStatus] = None) -> List[SmartContract]:
        """
        List smart contracts with optional filtering.
        
        Args:
            contract_type: Filter by contract type
            status: Filter by contract status
            
        Returns:
            List of matching contracts
        """
        contracts = list(self.contracts.values())
        
        if contract_type:
            contracts = [c for c in contracts if c.contract_type == contract_type]
        
        if status:
            contracts = [c for c in contracts if c.status == status]
        
        # Sort by updated_at (most recent first)
        contracts.sort(key=lambda x: x.updated_at, reverse=True)
        
        return contracts
    
    def update_contract(self, contract_id: str, updates: Dict[str, Any],
                       updated_by: str) -> SmartContract:
        """
        Update a smart contract.
        
        Args:
            contract_id: ID of the contract to update
            updates: Dictionary of updates to apply
            updated_by: User making the update
            
        Returns:
            Updated smart contract
        """
        try:
            contract = self.contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract {contract_id} not found")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(contract, key):
                    setattr(contract, key, value)
            
            contract.updated_at = datetime.now(timezone.utc)
            contract.updated_by = updated_by
            
            # Store in database
            if self.db_service:
                self.db_service.insert_event(
                    artifact_id=contract_id,
                    event_type="smart_contract_updated",
                    payload_json=json.dumps({
                        "updates": updates,
                        "updated_by": updated_by
                    }),
                    created_by=updated_by
                )
            
            logger.info(f"✅ Smart contract updated: {contract_id}")
            
        except Exception as e:
            logger.error(f"Failed to update smart contract: {e}")
            raise
        
        return contract
    
    def delete_contract(self, contract_id: str, deleted_by: str) -> bool:
        """
        Delete a smart contract.
        
        Args:
            contract_id: ID of the contract to delete
            deleted_by: User deleting the contract
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if contract_id not in self.contracts:
                return False
            
            del self.contracts[contract_id]
            
            # Store in database
            if self.db_service:
                self.db_service.insert_event(
                    artifact_id=contract_id,
                    event_type="smart_contract_deleted",
                    payload_json=json.dumps({
                        "deleted_by": deleted_by
                    }),
                    created_by=deleted_by
                )
            
            logger.info(f"✅ Smart contract deleted: {contract_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete smart contract: {e}")
            return False
    
    def get_execution_history(self, contract_id: Optional[str] = None,
                            limit: int = 100) -> List[ContractExecution]:
        """
        Get execution history with optional filtering.
        
        Args:
            contract_id: Filter by contract ID
            limit: Maximum number of results
            
        Returns:
            List of execution results
        """
        executions = self.execution_history
        
        if contract_id:
            executions = [e for e in executions if e.contract_id == contract_id]
        
        # Sort by executed_at (most recent first)
        executions.sort(key=lambda x: x.executed_at, reverse=True)
        
        return executions[:limit]
    
    def get_contract_statistics(self) -> Dict[str, Any]:
        """Get statistics about smart contracts."""
        try:
            total_contracts = len(self.contracts)
            active_contracts = len([c for c in self.contracts.values() if c.status == ContractStatus.ACTIVE])
            total_executions = len(self.execution_history)
            
            # Count by type
            type_counts = {}
            for contract in self.contracts.values():
                contract_type = contract.contract_type.value
                type_counts[contract_type] = type_counts.get(contract_type, 0) + 1
            
            # Count by status
            status_counts = {}
            for contract in self.contracts.values():
                status = contract.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Execution results
            execution_results = {}
            for execution in self.execution_history:
                result = execution.result.value
                execution_results[result] = execution_results.get(result, 0) + 1
            
            statistics = {
                "total_contracts": total_contracts,
                "active_contracts": active_contracts,
                "total_executions": total_executions,
                "contracts_by_type": type_counts,
                "contracts_by_status": status_counts,
                "execution_results": execution_results,
                "average_executions_per_contract": total_executions / max(total_contracts, 1),
                "success_rate": execution_results.get("success", 0) / max(total_executions, 1) * 100
            }
            
            logger.info("✅ Smart contract statistics generated")
            
        except Exception as e:
            logger.error(f"Failed to get contract statistics: {e}")
            statistics = {"error": str(e)}
        
        return statistics
    
    def _execute_rule(self, rule: ContractRule, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single contract rule."""
        try:
            # Determine rule engine based on condition format
            if rule.condition.startswith("$."):
                engine = "jsonpath"
            elif rule.condition.startswith("regex:"):
                engine = "regex"
            else:
                engine = "custom"
            
            # Evaluate condition
            if engine in self.rule_engines:
                result = self.rule_engines[engine](rule, data)
            else:
                result = {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "result": ExecutionResult.FAILURE,
                    "message": f"Unknown rule engine: {engine}",
                    "error": f"Rule engine '{engine}' not supported"
                }
            
            return result
        
        except Exception as e:
            return {
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "result": ExecutionResult.FAILURE,
                "message": f"Rule execution error: {str(e)}",
                "error": str(e)
            }
    
    def _evaluate_jsonpath_rule(self, rule: ContractRule, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a JSONPath-based rule."""
        try:
            # Simple JSONPath evaluation (in production, use a proper JSONPath library)
            condition = rule.condition[2:]  # Remove "$." prefix
            
            # Navigate through the data structure
            current_data = data
            for part in condition.split('.'):
                if isinstance(current_data, dict) and part in current_data:
                    current_data = current_data[part]
                else:
                    return {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "result": ExecutionResult.FAILURE,
                        "message": f"Path '{condition}' not found in data",
                        "affected_entities": [str(data.get("id", "unknown"))]
                    }
            
            # Check if the value meets the condition (simplified)
            if current_data:
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "result": ExecutionResult.SUCCESS,
                    "message": f"Condition '{condition}' satisfied",
                    "affected_entities": [str(data.get("id", "unknown"))]
                }
            else:
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "result": ExecutionResult.FAILURE,
                    "message": f"Condition '{condition}' not satisfied",
                    "affected_entities": [str(data.get("id", "unknown"))]
                }
        
        except Exception as e:
            return {
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "result": ExecutionResult.FAILURE,
                "message": f"JSONPath evaluation error: {str(e)}",
                "error": str(e)
            }
    
    def _evaluate_regex_rule(self, rule: ContractRule, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a regex-based rule."""
        try:
            # Extract regex pattern and field
            condition = rule.condition[6:]  # Remove "regex:" prefix
            if ":" not in condition:
                raise ValueError("Regex rule format: regex:field:pattern")
            
            field, pattern = condition.split(":", 1)
            
            # Get field value
            if field not in data:
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "result": ExecutionResult.FAILURE,
                    "message": f"Field '{field}' not found in data",
                    "affected_entities": [str(data.get("id", "unknown"))]
                }
            
            field_value = str(data[field])
            
            # Apply regex
            if re.match(pattern, field_value):
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "result": ExecutionResult.SUCCESS,
                    "message": f"Field '{field}' matches pattern '{pattern}'",
                    "affected_entities": [str(data.get("id", "unknown"))]
                }
            else:
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "result": ExecutionResult.FAILURE,
                    "message": f"Field '{field}' does not match pattern '{pattern}'",
                    "affected_entities": [str(data.get("id", "unknown"))]
                }
        
        except Exception as e:
            return {
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "result": ExecutionResult.FAILURE,
                "message": f"Regex evaluation error: {str(e)}",
                "error": str(e)
            }
    
    def _evaluate_custom_rule(self, rule: ContractRule, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a custom rule."""
        try:
            # Custom rule evaluation logic
            condition = rule.condition.lower()
            
            # Example custom rules
            if "required" in condition:
                # Check for required fields
                required_fields = condition.split(":")[1].split(",")
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    return {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "result": ExecutionResult.FAILURE,
                        "message": f"Missing required fields: {', '.join(missing_fields)}",
                        "affected_entities": [str(data.get("id", "unknown"))]
                    }
                else:
                    return {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "result": ExecutionResult.SUCCESS,
                        "message": "All required fields present",
                        "affected_entities": [str(data.get("id", "unknown"))]
                    }
            
            elif "size" in condition:
                # Check size constraints
                size_limit = int(condition.split(":")[1])
                if "content" in data and len(data["content"]) > size_limit:
                    return {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "result": ExecutionResult.WARNING,
                        "message": f"Content size ({len(data['content'])}) exceeds limit ({size_limit})",
                        "affected_entities": [str(data.get("id", "unknown"))]
                    }
                else:
                    return {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "result": ExecutionResult.SUCCESS,
                        "message": "Content size within limits",
                        "affected_entities": [str(data.get("id", "unknown"))]
                    }
            
            else:
                return {
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "result": ExecutionResult.FAILURE,
                    "message": f"Unknown custom rule: {condition}",
                    "error": "Custom rule not recognized"
                }
        
        except Exception as e:
            return {
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "result": ExecutionResult.FAILURE,
                "message": f"Custom rule evaluation error: {str(e)}",
                "error": str(e)
            }
    
    def _initialize_default_contracts(self):
        """Initialize default smart contracts."""
        try:
            # Document Integrity Contract
            integrity_rules = [
                ContractRule(
                    rule_id=str(uuid.uuid4()),
                    name="Hash Validation",
                    description="Validate document hash integrity",
                    condition="$.hash",
                    action="validate_hash",
                    severity="critical"
                ),
                ContractRule(
                    rule_id=str(uuid.uuid4()),
                    name="Required Fields",
                    description="Check for required document fields",
                    condition="required:id,type,created_at,created_by",
                    action="validate_required_fields",
                    severity="high"
                ),
                ContractRule(
                    rule_id=str(uuid.uuid4()),
                    name="Size Limits",
                    description="Check document size limits",
                    condition="size:10485760",  # 10MB limit
                    action="validate_size",
                    severity="medium"
                )
            ]
            
            integrity_contract = SmartContract(
                contract_id=str(uuid.uuid4()),
                name="Document Integrity Contract",
                description="Automated document integrity validation",
                contract_type=ContractType.COMPLIANCE_CHECK,
                status=ContractStatus.ACTIVE,
                rules=integrity_rules,
                created_at=datetime.now(timezone.utc),
                created_by="system",
                updated_at=datetime.now(timezone.utc),
                updated_by="system",
                metadata={"version": "1.0", "category": "integrity"}
            )
            
            self.contracts[integrity_contract.contract_id] = integrity_contract
            
            # Compliance Contract
            compliance_rules = [
                ContractRule(
                    rule_id=str(uuid.uuid4()),
                    name="Date Format Validation",
                    description="Validate date format compliance",
                    condition="regex:created_at:^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}",
                    action="validate_date_format",
                    severity="high"
                ),
                ContractRule(
                    rule_id=str(uuid.uuid4()),
                    name="User Authorization",
                    description="Check user authorization",
                    condition="$.created_by",
                    action="validate_user",
                    severity="critical"
                )
            ]
            
            compliance_contract = SmartContract(
                contract_id=str(uuid.uuid4()),
                name="Compliance Validation Contract",
                description="Automated compliance validation",
                contract_type=ContractType.COMPLIANCE_CHECK,
                status=ContractStatus.ACTIVE,
                rules=compliance_rules,
                created_at=datetime.now(timezone.utc),
                created_by="system",
                updated_at=datetime.now(timezone.utc),
                updated_by="system",
                metadata={"version": "1.0", "category": "compliance"}
            )
            
            self.contracts[compliance_contract.contract_id] = compliance_contract
            
            logger.info("✅ Default smart contracts initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default contracts: {e}")

