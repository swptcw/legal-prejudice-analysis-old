"""
Routes for authentication and API key management
"""

import datetime
import uuid
import secrets
import hashlib
from flask import Blueprint, jsonify, request, current_app, g
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from models import APIKey
from utils.auth import require_api_key, is_admin

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def generate_api_key():
    """Generate a secure API key"""
    # Format: prfk_<random string>
    return f"prfk_{secrets.token_urlsafe(32)}"

def hash_api_key(api_key):
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()

@auth_bp.route('/keys', methods=['POST'])
@require_api_key
@is_admin
@limiter.limit("10 per hour")
def create_api_key():
    """Create a new API key"""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        required_fields = ["name", "created_by"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")
        
        # Generate API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        timestamp = datetime.datetime.utcnow()
        
        # Set expiration if provided
        expires_at = None
        if "expires_in_days" in data:
            try:
                days = int(data["expires_in_days"])
                if days > 0:
                    expires_at = timestamp + datetime.timedelta(days=days)
            except (ValueError, TypeError):
                pass
        
        # Create API key record
        key = APIKey(
            key_id=str(uuid.uuid4()),
            key_hash=key_hash,
            name=data["name"],
            description=data.get("description", ""),
            created_by=data["created_by"],
            is_active=True,
            expires_at=expires_at,
            created_at=timestamp,
            updated_at=timestamp
        )
        
        # Save to database
        g.db_session.add(key)
        g.db_session.commit()
        
        # Return response with the actual API key
        # This is the only time the actual key will be returned
        return jsonify({
            "key_id": key.key_id,
            "api_key": api_key,  # Only returned once
            "name": key.name,
            "description": key.description,
            "created_by": key.created_by,
            "is_active": key.is_active,
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "created_at": key.created_at.isoformat()
        }), 201
        
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error creating API key: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error creating API key: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/keys', methods=['GET'])
@require_api_key
@is_admin
def list_api_keys():
    """List all API keys"""
    try:
        # Query API keys
        keys = g.db_session.query(APIKey).all()
        
        # Convert to dictionaries (without key hash)
        key_list = []
        for key in keys:
            key_dict = {
                "key_id": key.key_id,
                "name": key.name,
                "description": key.description,
                "created_by": key.created_by,
                "is_active": key.is_active,
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
                "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                "created_at": key.created_at.isoformat()
            }
            key_list.append(key_dict)
        
        return jsonify({
            "api_keys": key_list
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Error listing API keys: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/keys/<key_id>', methods=['GET'])
@require_api_key
@is_admin
def get_api_key(key_id):
    """Get a specific API key"""
    try:
        # Query API key
        key = g.db_session.query(APIKey).filter_by(key_id=key_id).first()
        if not key:
            raise NotFound(f"API key {key_id} not found")
        
        # Convert to dictionary (without key hash)
        key_dict = {
            "key_id": key.key_id,
            "name": key.name,
            "description": key.description,
            "created_by": key.created_by,
            "is_active": key.is_active,
            "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "created_at": key.created_at.isoformat(),
            "updated_at": key.updated_at.isoformat()
        }
        
        return jsonify(key_dict), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception(f"Error retrieving API key: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/keys/<key_id>', methods=['PUT'])
@require_api_key
@is_admin
def update_api_key(key_id):
    """Update an API key"""
    try:
        # Query API key
        key = g.db_session.query(APIKey).filter_by(key_id=key_id).first()
        if not key:
            raise NotFound(f"API key {key_id} not found")
        
        # Get request data
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        # Update API key fields
        timestamp = datetime.datetime.utcnow()
        updated = False
        
        if "name" in data:
            key.name = data["name"]
            updated = True
        
        if "description" in data:
            key.description = data["description"]
            updated = True
        
        if "is_active" in data:
            key.is_active = bool(data["is_active"])
            updated = True
        
        if "expires_at" in data:
            if data["expires_at"] is None:
                key.expires_at = None
                updated = True
            else:
                try:
                    key.expires_at = datetime.datetime.fromisoformat(data["expires_at"])
                    updated = True
                except ValueError:
                    raise BadRequest("Invalid expires_at format. Use ISO 8601 format")
        
        if updated:
            key.updated_at = timestamp
            g.db_session.commit()
        
        # Convert to dictionary (without key hash)
        key_dict = {
            "key_id": key.key_id,
            "name": key.name,
            "description": key.description,
            "created_by": key.created_by,
            "is_active": key.is_active,
            "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "created_at": key.created_at.isoformat(),
            "updated_at": key.updated_at.isoformat()
        }
        
        return jsonify(key_dict), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error updating API key: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error updating API key: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/keys/<key_id>', methods=['DELETE'])
@require_api_key
@is_admin
def delete_api_key(key_id):
    """Delete an API key"""
    try:
        # Query API key
        key = g.db_session.query(APIKey).filter_by(key_id=key_id).first()
        if not key:
            raise NotFound(f"API key {key_id} not found")
        
        # Delete API key
        timestamp = datetime.datetime.utcnow()
        g.db_session.delete(key)
        g.db_session.commit()
        
        return jsonify({
            "key_id": key_id,
            "deleted": True,
            "deleted_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error deleting API key: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error deleting API key: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/keys/<key_id>/revoke', methods=['POST'])
@require_api_key
@is_admin
def revoke_api_key(key_id):
    """Revoke an API key"""
    try:
        # Query API key
        key = g.db_session.query(APIKey).filter_by(key_id=key_id).first()
        if not key:
            raise NotFound(f"API key {key_id} not found")
        
        # Revoke API key
        timestamp = datetime.datetime.utcnow()
        key.is_active = False
        key.updated_at = timestamp
        g.db_session.commit()
        
        return jsonify({
            "key_id": key_id,
            "is_active": False,
            "revoked_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error revoking API key: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error revoking API key: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/keys/<key_id>/rotate', methods=['POST'])
@require_api_key
@is_admin
@limiter.limit("10 per hour")
def rotate_api_key(key_id):
    """Rotate an API key (generate a new key while preserving metadata)"""
    try:
        # Query API key
        key = g.db_session.query(APIKey).filter_by(key_id=key_id).first()
        if not key:
            raise NotFound(f"API key {key_id} not found")
        
        # Generate new API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        timestamp = datetime.datetime.utcnow()
        
        # Update API key
        key.key_hash = key_hash
        key.updated_at = timestamp
        g.db_session.commit()
        
        # Return response with the new API key
        return jsonify({
            "key_id": key.key_id,
            "api_key": api_key,  # Only returned once
            "name": key.name,
            "description": key.description,
            "created_by": key.created_by,
            "is_active": key.is_active,
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "rotated_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error rotating API key: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error rotating API key: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/validate', methods=['POST'])
@limiter.limit("60 per minute")
def validate_api_key():
    """Validate an API key"""
    try:
        # Get API key from request
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('ApiKey '):
            raise Unauthorized("Missing or invalid Authorization header")
        
        api_key = auth_header.replace('ApiKey ', '')
        key_hash = hash_api_key(api_key)
        
        # Query API key
        key = g.db_session.query(APIKey).filter_by(key_hash=key_hash).first()
        if not key:
            raise Unauthorized("Invalid API key")
        
        # Check if key is active
        if not key.is_active:
            raise Unauthorized("API key is inactive")
        
        # Check if key is expired
        if key.expires_at and key.expires_at < datetime.datetime.utcnow():
            raise Unauthorized("API key is expired")
        
        # Update last used timestamp
        timestamp = datetime.datetime.utcnow()
        key.last_used_at = timestamp
        g.db_session.commit()
        
        return jsonify({
            "valid": True,
            "key_id": key.key_id,
            "name": key.name,
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "validated_at": timestamp.isoformat()
        }), 200
        
    except Unauthorized as e:
        return jsonify({
            "valid": False,
            "error": str(e)
        }), 401
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error validating API key: {str(e)}")
        return jsonify({
            "valid": False,
            "error": "Database error"
        }), 500
    except Exception as e:
        current_app.logger.exception(f"Error validating API key: {str(e)}")
        return jsonify({
            "valid": False,
            "error": "Internal server error"
        }), 500