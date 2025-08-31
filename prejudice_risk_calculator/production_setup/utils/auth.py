"""
Authentication utilities for the API
"""

import hashlib
import functools
from flask import request, jsonify, g, current_app
from werkzeug.exceptions import Unauthorized, Forbidden

from models import APIKey

def hash_api_key(api_key):
    """Hash an API key for comparison"""
    return hashlib.sha256(api_key.encode('utf-8')).hexdigest()

def get_api_key_from_request():
    """Extract and validate API key from request"""
    # Get API key from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('ApiKey '):
        raise Unauthorized("Missing or invalid Authorization header")
    
    api_key = auth_header.replace('ApiKey ', '')
    key_hash = hash_api_key(api_key)
    
    # Query API key from database
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
    key.last_used_at = datetime.datetime.utcnow()
    
    # Store key in request context
    g.api_key = key
    
    return key

def require_api_key(f):
    """Decorator to require API key authentication"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        try:
            get_api_key_from_request()
        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            current_app.logger.exception(f"Authentication error: {str(e)}")
            return jsonify({"error": "Authentication error"}), 500
        
        return f(*args, **kwargs)
    
    return decorated

def is_admin(f):
    """Decorator to require admin privileges"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # In a real implementation, this would check admin status
        # For now, we'll assume all authenticated users are admins
        if not hasattr(g, 'api_key'):
            return jsonify({"error": "Authentication required"}), 401
        
        # Check if key has admin flag (not implemented in this version)
        # if not g.api_key.is_admin:
        #     return jsonify({"error": "Admin privileges required"}), 403
        
        return f(*args, **kwargs)
    
    return decorated