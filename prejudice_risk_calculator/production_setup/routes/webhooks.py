"""
Routes for webhook management
"""

import datetime
import uuid
import hmac
import hashlib
import json
from flask import Blueprint, jsonify, request, current_app, g
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound, BadRequest, Forbidden
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from models import Webhook, WebhookDelivery
from utils.auth import require_api_key
from utils.validation import validate_webhook_data
from utils.events import register_webhook_handler

# Create blueprint
webhooks_bp = Blueprint('webhooks', __name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

@webhooks_bp.route('', methods=['POST'])
@require_api_key
def register_webhook():
    """Register a new webhook"""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        errors = validate_webhook_data(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        # Generate webhook ID and hash secret
        webhook_id = f"wh_{str(uuid.uuid4())[:8]}"
        timestamp = datetime.datetime.utcnow()
        
        # Hash the secret
        secret = data["secret"]
        secret_hash = hashlib.sha256(secret.encode('utf-8')).hexdigest()
        
        # Create webhook record
        webhook = Webhook(
            webhook_id=webhook_id,
            target_url=data["target_url"],
            events=json.dumps(data["events"]),
            description=data.get("description", ""),
            secret_hash=secret_hash,
            active=data.get("active", True),
            content_type=data.get("content_type", "application/json"),
            created_at=timestamp,
            updated_at=timestamp
        )
        
        # Save to database
        g.db_session.add(webhook)
        g.db_session.commit()
        
        # Register webhook handler
        register_webhook_handler(webhook)
        
        # Return response (without secret hash)
        return jsonify({
            "webhook_id": webhook_id,
            "target_url": webhook.target_url,
            "events": json.loads(webhook.events) if isinstance(webhook.events, str) else webhook.events,
            "description": webhook.description,
            "active": webhook.active,
            "content_type": webhook.content_type,
            "created_at": webhook.created_at.isoformat()
        }), 201
        
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error registering webhook: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error registering webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@webhooks_bp.route('', methods=['GET'])
@require_api_key
def list_webhooks():
    """List all webhooks"""
    try:
        # Query webhooks
        webhooks = g.db_session.query(Webhook).all()
        
        # Convert to dictionaries (without secret hash)
        webhook_list = []
        for webhook in webhooks:
            webhook_dict = {
                "webhook_id": webhook.webhook_id,
                "target_url": webhook.target_url,
                "events": json.loads(webhook.events) if isinstance(webhook.events, str) else webhook.events,
                "description": webhook.description,
                "active": webhook.active,
                "content_type": webhook.content_type,
                "created_at": webhook.created_at.isoformat()
            }
            webhook_list.append(webhook_dict)
        
        return jsonify({
            "webhooks": webhook_list
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Error listing webhooks: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@webhooks_bp.route('/<webhook_id>', methods=['GET'])
@require_api_key
def get_webhook(webhook_id):
    """Get a specific webhook"""
    try:
        # Query webhook
        webhook = g.db_session.query(Webhook).filter_by(webhook_id=webhook_id).first()
        if not webhook:
            raise NotFound(f"Webhook {webhook_id} not found")
        
        # Get delivery statistics
        total_deliveries = g.db_session.query(WebhookDelivery).filter_by(webhook_id=webhook.id).count()
        successful_deliveries = g.db_session.query(WebhookDelivery).filter_by(
            webhook_id=webhook.id,
            status="delivered"
        ).count()
        
        success_rate = successful_deliveries / total_deliveries if total_deliveries > 0 else 0
        
        # Get last successful delivery
        last_successful = g.db_session.query(WebhookDelivery).filter_by(
            webhook_id=webhook.id,
            status="delivered"
        ).order_by(WebhookDelivery.delivered_at.desc()).first()
        
        # Convert to dictionary (without secret hash)
        webhook_dict = {
            "webhook_id": webhook.webhook_id,
            "target_url": webhook.target_url,
            "events": json.loads(webhook.events) if isinstance(webhook.events, str) else webhook.events,
            "description": webhook.description,
            "active": webhook.active,
            "content_type": webhook.content_type,
            "created_at": webhook.created_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat(),
            "delivery_success_rate": success_rate,
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "last_successful_delivery": last_successful.delivered_at.isoformat() if last_successful else None
        }
        
        return jsonify(webhook_dict), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception(f"Error retrieving webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@webhooks_bp.route('/<webhook_id>', methods=['PUT'])
@require_api_key
def update_webhook(webhook_id):
    """Update a webhook"""
    try:
        # Query webhook
        webhook = g.db_session.query(Webhook).filter_by(webhook_id=webhook_id).first()
        if not webhook:
            raise NotFound(f"Webhook {webhook_id} not found")
        
        # Get request data
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        # Update webhook fields
        timestamp = datetime.datetime.utcnow()
        updated = False
        
        if "target_url" in data:
            webhook.target_url = data["target_url"]
            updated = True
        
        if "events" in data:
            if not isinstance(data["events"], list):
                raise BadRequest("Events must be an array")
            webhook.events = json.dumps(data["events"])
            updated = True
        
        if "description" in data:
            webhook.description = data["description"]
            updated = True
        
        if "active" in data:
            webhook.active = bool(data["active"])
            updated = True
        
        if "content_type" in data:
            webhook.content_type = data["content_type"]
            updated = True
        
        if "secret" in data:
            # Hash the new secret
            secret = data["secret"]
            webhook.secret_hash = hashlib.sha256(secret.encode('utf-8')).hexdigest()
            updated = True
        
        if updated:
            webhook.updated_at = timestamp
            g.db_session.commit()
            
            # Re-register webhook handler with updated configuration
            register_webhook_handler(webhook)
        
        # Convert to dictionary (without secret hash)
        webhook_dict = {
            "webhook_id": webhook.webhook_id,
            "target_url": webhook.target_url,
            "events": json.loads(webhook.events) if isinstance(webhook.events, str) else webhook.events,
            "description": webhook.description,
            "active": webhook.active,
            "content_type": webhook.content_type,
            "created_at": webhook.created_at.isoformat(),
            "updated_at": webhook.updated_at.isoformat()
        }
        
        return jsonify(webhook_dict), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error updating webhook: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error updating webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@webhooks_bp.route('/<webhook_id>', methods=['DELETE'])
@require_api_key
def delete_webhook(webhook_id):
    """Delete a webhook"""
    try:
        # Query webhook
        webhook = g.db_session.query(Webhook).filter_by(webhook_id=webhook_id).first()
        if not webhook:
            raise NotFound(f"Webhook {webhook_id} not found")
        
        # Delete webhook
        timestamp = datetime.datetime.utcnow()
        g.db_session.delete(webhook)
        g.db_session.commit()
        
        return jsonify({
            "webhook_id": webhook_id,
            "deleted": True,
            "deleted_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error deleting webhook: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error deleting webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@webhooks_bp.route('/<webhook_id>/deliveries', methods=['GET'])
@require_api_key
def list_webhook_deliveries(webhook_id):
    """List all deliveries for a webhook"""
    try:
        # Query webhook
        webhook = g.db_session.query(Webhook).filter_by(webhook_id=webhook_id).first()
        if not webhook:
            raise NotFound(f"Webhook {webhook_id} not found")
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Limit to 100 items per page
        status = request.args.get('status')
        
        # Build query
        query = g.db_session.query(WebhookDelivery).filter_by(webhook_id=webhook.id)
        
        # Apply filters
        if status:
            query = query.filter(WebhookDelivery.status == status)
        
        # Count total
        total = query.count()
        
        # Paginate
        query = query.order_by(WebhookDelivery.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        # Execute query
        deliveries = query.all()
        
        # Convert to dictionaries
        delivery_list = []
        for delivery in deliveries:
            delivery_dict = {
                "delivery_id": delivery.delivery_id,
                "event_id": delivery.event_id,
                "event_type": delivery.event_type,
                "status": delivery.status,
                "response_code": delivery.response_code,
                "response_body": delivery.response_body,
                "error": delivery.error,
                "retry_count": delivery.retry_count,
                "created_at": delivery.created_at.isoformat(),
                "updated_at": delivery.updated_at.isoformat(),
                "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None
            }
            delivery_list.append(delivery_dict)
        
        return jsonify({
            "webhook_id": webhook_id,
            "deliveries": delivery_list,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page  # Ceiling division
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": "Invalid pagination parameters"}), 400
    except Exception as e:
        current_app.logger.exception(f"Error listing webhook deliveries: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@webhooks_bp.route('/test', methods=['POST'])
@require_api_key
def test_webhook():
    """Send a test webhook"""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        required_fields = ["target_url", "event"]
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")
        
        target_url = data["target_url"]
        event_type = data["event"]
        include_sample_data = data.get("include_sample_data", True)
        
        # Generate test event ID
        test_id = f"test_{str(uuid.uuid4())[:8]}"
        timestamp = datetime.datetime.utcnow()
        
        # Create sample payload
        if include_sample_data:
            if event_type == "assessment.created":
                payload = {
                    "id": "evt_test",
                    "event": "assessment.created",
                    "created_at": timestamp.isoformat(),
                    "api_version": "v1",
                    "data": {
                        "assessment_id": "PRF-2025-TEST",
                        "case_name": "Test Case",
                        "judge_name": "Test Judge",
                        "assessor_name": "Test Assessor",
                        "assessment_date": timestamp.strftime("%Y-%m-%d"),
                        "case_id": "CASE-TEST",
                        "case_management_system_id": "CMS-TEST",
                        "status": "created"
                    }
                }
            elif event_type == "result.calculated":
                payload = {
                    "id": "evt_test",
                    "event": "result.calculated",
                    "created_at": timestamp.isoformat(),
                    "api_version": "v1",
                    "data": {
                        "assessment_id": "PRF-2025-TEST",
                        "overall_score": 18,
                        "risk_level": "High",
                        "category_scores": {
                            "relationship": 17,
                            "conduct": 12,
                            "contextual": 9
                        },
                        "high_risk_factors": [
                            {
                                "id": "financial-direct",
                                "name": "Direct financial interest",
                                "score": 20
                            }
                        ],
                        "recommendations": [
                            "File a motion to recuse/disqualify or for disclosure of potential conflicts",
                            "Consider requesting a hearing on prejudice concerns",
                            "Develop detailed documentation of all prejudice indicators",
                            "Implement strategic adjustments to case presentation",
                            "Prepare record for potential appeal on prejudice grounds"
                        ],
                        "calculated_at": timestamp.isoformat()
                    }
                }
            else:
                payload = {
                    "id": "evt_test",
                    "event": event_type,
                    "created_at": timestamp.isoformat(),
                    "api_version": "v1",
                    "data": {
                        "message": "This is a test webhook",
                        "timestamp": timestamp.isoformat()
                    }
                }
        else:
            payload = {
                "id": "evt_test",
                "event": event_type,
                "created_at": timestamp.isoformat(),
                "api_version": "v1",
                "data": {
                    "message": "This is a test webhook",
                    "timestamp": timestamp.isoformat()
                }
            }
        
        # Generate signature
        test_secret = "test_webhook_secret"
        signature_payload = f"{int(timestamp.timestamp())}.{json.dumps(payload)}"
        signature = hmac.new(
            test_secret.encode('utf-8'),
            signature_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Prejudice-Signature": f"sha256={signature}",
            "X-Prejudice-Timestamp": str(int(timestamp.timestamp())),
            "X-Prejudice-Event": event_type,
            "X-Prejudice-Webhook-ID": "wh_test",
            "User-Agent": "PrejudiceRiskCalculator-Webhook/1.0"
        }
        
        # In a real implementation, this would send an HTTP request
        # For now, we'll simulate a successful delivery
        
        # Return response
        return jsonify({
            "test_id": test_id,
            "target_url": target_url,
            "event": event_type,
            "status": "delivered",
            "response_code": 200,
            "response_body": '{"status":"received"}',
            "request_headers": headers,
            "request_body": json.dumps(payload),
            "created_at": timestamp.isoformat(),
            "delivered_at": timestamp.isoformat()
        }), 200
        
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.exception(f"Error testing webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500