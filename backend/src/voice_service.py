"""
Voice Command Processing Service

Handles voice-activated commands for document operations.
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class VoiceCommandProcessor:
    """Processes voice commands and converts them to API operations."""
    
    def __init__(self):
        self.command_patterns = {
            # Document operations
            "create_attestation": [
                r"create attestation for document (\w+)",
                r"attest document (\w+)",
                r"certify document (\w+)",
                r"create attestation for (\w+)"
            ],
            "generate_disclosure": [
                r"generate disclosure pack for document (\w+)",
                r"create disclosure pack for (\w+)",
                r"export disclosure for document (\w+)",
                r"generate compliance pack for (\w+)"
            ],
            "verify_document": [
                r"verify document (\w+)",
                r"check integrity of document (\w+)",
                r"validate document (\w+)",
                r"verify (\w+)"
            ],
            "show_history": [
                r"show history for document (\w+)",
                r"document history for (\w+)",
                r"show timeline for (\w+)",
                r"history of document (\w+)"
            ],
            "list_attestations": [
                r"list all attestations",
                r"show attestations",
                r"display attestations",
                r"get attestation list"
            ],
            "list_documents": [
                r"list all documents",
                r"show documents",
                r"display documents",
                r"get document list"
            ],
            "system_status": [
                r"system status",
                r"show system status",
                r"check system health",
                r"system health"
            ]
        }
        
        self.confirmation_phrases = [
            "yes", "yeah", "yep", "sure", "okay", "ok", "confirm", "proceed"
        ]
        
        self.cancellation_phrases = [
            "no", "nope", "cancel", "stop", "abort", "nevermind"
        ]

    def process_voice_command(self, command_text: str, user_id: str = "voice_user") -> Dict[str, Any]:
        """
        Process a voice command and return the corresponding API operation.
        
        Args:
            command_text: The transcribed voice command
            user_id: ID of the user issuing the command
            
        Returns:
            Dict containing the operation details and response
        """
        try:
            # Normalize the command text
            normalized_command = command_text.lower().strip()
            
            # Remove common filler words
            normalized_command = re.sub(r'\b(please|can you|could you|would you)\b', '', normalized_command)
            normalized_command = re.sub(r'\s+', ' ', normalized_command).strip()
            
            logger.info(f"Processing voice command: '{normalized_command}' from user: {user_id}")
            
            # Try to match against known patterns
            for operation, patterns in self.command_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, normalized_command)
                    if match:
                        return self._execute_operation(operation, match, user_id, command_text)
            
            # If no pattern matches, return help
            return {
                "success": False,
                "operation": "help",
                "message": "I didn't understand that command. Here are some things you can say:",
                "suggestions": [
                    "Create attestation for document [ID]",
                    "Generate disclosure pack for document [ID]",
                    "Verify document [ID]",
                    "Show history for document [ID]",
                    "List all attestations",
                    "System status"
                ],
                "original_command": command_text,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            return {
                "success": False,
                "operation": "error",
                "message": f"Sorry, I encountered an error processing your command: {str(e)}",
                "original_command": command_text,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _execute_operation(self, operation: str, match: re.Match, user_id: str, original_command: str) -> Dict[str, Any]:
        """Execute the matched operation."""
        
        base_response = {
            "success": True,
            "operation": operation,
            "user_id": user_id,
            "original_command": original_command,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if operation == "create_attestation":
            document_id = match.group(1)
            return {
                **base_response,
                "action": "create_attestation",
                "parameters": {
                    "artifact_id": document_id,
                    "attestation_type": "compliance_check",
                    "attestation_data": {
                        "voice_triggered": True,
                        "triggered_by": user_id,
                        "command": original_command
                    }
                },
                "message": f"Creating attestation for document {document_id}...",
                "api_endpoint": "/api/attestations",
                "method": "POST"
            }
            
        elif operation == "generate_disclosure":
            document_id = match.group(1)
            return {
                **base_response,
                "action": "generate_disclosure_pack",
                "parameters": {
                    "artifact_id": document_id
                },
                "message": f"Generating disclosure pack for document {document_id}...",
                "api_endpoint": "/api/disclosure-pack",
                "method": "GET"
            }
            
        elif operation == "verify_document":
            document_id = match.group(1)
            return {
                **base_response,
                "action": "verify_document",
                "parameters": {
                    "artifact_id": document_id
                },
                "message": f"Verifying document {document_id}...",
                "api_endpoint": "/api/artifacts/{artifact_id}/verify",
                "method": "GET"
            }
            
        elif operation == "show_history":
            document_id = match.group(1)
            return {
                **base_response,
                "action": "get_document_history",
                "parameters": {
                    "artifact_id": document_id
                },
                "message": f"Retrieving history for document {document_id}...",
                "api_endpoint": "/api/artifacts/{artifact_id}/history",
                "method": "GET"
            }
            
        elif operation == "list_attestations":
            return {
                **base_response,
                "action": "list_attestations",
                "parameters": {
                    "limit": 50,
                    "offset": 0
                },
                "message": "Retrieving all attestations...",
                "api_endpoint": "/api/attestations",
                "method": "GET"
            }
            
        elif operation == "list_documents":
            return {
                **base_response,
                "action": "list_documents",
                "parameters": {
                    "limit": 50,
                    "offset": 0
                },
                "message": "Retrieving all documents...",
                "api_endpoint": "/api/artifacts",
                "method": "GET"
            }
            
        elif operation == "system_status":
            return {
                **base_response,
                "action": "system_status",
                "parameters": {},
                "message": "Checking system status...",
                "api_endpoint": "/api/health",
                "method": "GET"
            }
        
        return base_response

    def get_available_commands(self) -> List[Dict[str, Any]]:
        """Get a list of available voice commands."""
        commands = []
        
        for operation, patterns in self.command_patterns.items():
            commands.append({
                "operation": operation,
                "examples": [pattern.replace(r"(\w+)", "[DOCUMENT_ID]") for pattern in patterns[:2]],
                "description": self._get_operation_description(operation)
            })
        
        return commands

    def _get_operation_description(self, operation: str) -> str:
        """Get a human-readable description of an operation."""
        descriptions = {
            "create_attestation": "Create a compliance attestation for a document",
            "generate_disclosure": "Generate a regulatory disclosure pack for a document",
            "verify_document": "Verify the integrity and authenticity of a document",
            "show_history": "Show the complete history and timeline of a document",
            "list_attestations": "List all attestations in the system",
            "list_documents": "List all documents in the system",
            "system_status": "Check the current system health and status"
        }
        return descriptions.get(operation, "Unknown operation")

    def is_confirmation(self, text: str) -> bool:
        """Check if the text is a confirmation."""
        return any(phrase in text.lower() for phrase in self.confirmation_phrases)

    def is_cancellation(self, text: str) -> bool:
        """Check if the text is a cancellation."""
        return any(phrase in text.lower() for phrase in self.cancellation_phrases)

