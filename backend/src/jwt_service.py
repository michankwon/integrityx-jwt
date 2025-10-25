import json
import os
import logging
from datetime import datetime, timedelta, timezone

import jwt

logger = logging.getLogger(__name__)

_ISSUER = os.getenv("JWT_ISSUER", "integrityx")
_TTL = int(os.getenv("JWT_TTL_SECONDS", "3600"))


def _load_key(path_env: str) -> str:
    path = os.getenv(path_env)
    if not path:
        raise RuntimeError(f"{path_env} not set. Please configure JWT keys in .env file")
    
    if not os.path.exists(path):
        raise RuntimeError(f"JWT key file not found: {path}. Run 'python generate_jwt_keys.py' to create keys")
    
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read JWT key from {path}: {e}")


_PRIVATE_KEY = _load_key("JWT_PRIVATE_KEY_PATH")
_PUBLIC_KEY = _load_key("JWT_PUBLIC_KEY_PATH")


def canonical_json(data: dict) -> str:
    return json.dumps(data, separators=(",", ":"), sort_keys=True)


def sign_artifact(artifact_id: str, payload: dict) -> str:
    """
    Sign an artifact with JWT using RS256 algorithm.
    
    Args:
        artifact_id: Unique identifier for the artifact
        payload: Document payload to sign
        
    Returns:
        JWT token as string
    """
    issued_at = datetime.now(timezone.utc)
    claims = {
        "iss": _ISSUER,
        "iat": int(issued_at.timestamp()),
        "exp": int((issued_at + timedelta(seconds=_TTL)).timestamp()),
        "artifact_id": artifact_id,
        "payload": canonical_json(payload),
    }
    
    try:
        token = jwt.encode(claims, _PRIVATE_KEY, algorithm="RS256")
        logger.info(f"✅ JWT signature created for artifact {artifact_id[:8]}...")
        return token
    except Exception as e:
        logger.error(f"❌ Failed to create JWT signature for {artifact_id}: {e}")
        raise


def verify_signature(token: str, payload: dict) -> dict:
    """
    Verify a JWT signature and validate payload integrity.
    
    Args:
        token: JWT token to verify
        payload: Expected document payload
        
    Returns:
        Decoded JWT claims if verification succeeds
        
    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidSignatureError: If signature is invalid
        ValueError: If payload doesn't match
    """
    try:
        claims = jwt.decode(token, _PUBLIC_KEY, algorithms=["RS256"], issuer=_ISSUER)
        expected = canonical_json(payload)
        
        if claims["payload"] != expected:
            logger.warning(f"❌ JWT payload mismatch for artifact {claims.get('artifact_id', 'unknown')}")
            raise ValueError("Payload mismatch")
            
        logger.info(f"✅ JWT signature verified for artifact {claims.get('artifact_id', 'unknown')[:8]}...")
        return claims
        
    except jwt.ExpiredSignatureError:
        logger.warning("❌ JWT signature expired")
        raise
    except jwt.InvalidSignatureError:
        logger.warning("❌ JWT signature invalid")
        raise
    except Exception as e:
        logger.error(f"❌ JWT verification failed: {e}")
        raise
