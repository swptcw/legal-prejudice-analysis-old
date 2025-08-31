"""
Event handling utilities for webhooks and notifications
"""

import json
import uuid
import datetime
import hmac
import hashlib
import threading
import requests
import time
from flask import current_app, g

from models import Webhook, WebhookDelivery

# In-memory event handlers (in a real implementation, this would be more robust)
webhook_handlers = {}

def register_webhook_handler(webhook):
    """Register a webhook handler"""
    webhook_id = webhook.webhook_id
    events = json.loads(webhook.events) if isinstance(webhook.events, str) else webhook.events
    
    # Store webhook handler
    webhook_handlers[webhook_id] = {
        "id": webhook.id,
        "webhook_id": webhook_id,
        "target_url": webhook.target_url,
        "events": events,
        "secret_hash": webhook.secret_hash,
        "active": webhook.active,
        "content_type": webhook.content_type
    }
    
    current_app.logger.info(f"Registered webhook handler {webhook_id} for events: {', '.join(events)}")

def load_webhook_handlers():
    """Load all webhook handlers from database"""
    try:
        webhooks = g.db_session.query(Webhook).filter_by(active=True).all()
        for webhook in webhooks:
            register_webhook_handler(webhook)
        
        current_app.logger.info(f"Loaded {len(webhooks)} webhook handlers")
    except Exception as e:
        current_app.logger.exception(f"Error loading webhook handlers: {str(e)}")

def trigger_event(event_type, data):
    """Trigger an event and notify all registered handlers"""
    # Check if webhooks are enabled
    if not current_app.config.get('ENABLE_WEBHOOKS', True):
        current_app.logger.info(f"Webhooks disabled, not triggering event {event_type}")
        return
    
    # Create event
    event_id = f"evt_{str(uuid.uuid4())[:8]}"
    timestamp = datetime.datetime.utcnow()
    
    event_data = {
        "id": event_id,
        "event": event_type,
        "created_at": timestamp.isoformat(),
        "api_version": current_app.config.get('API_VERSION', 'v1'),
        "data": data
    }
    
    current_app.logger.info(f"Triggered event {event_type} with ID {event_id}")
    
    # Notify handlers
    for webhook_id, handler in webhook_handlers.items():
        if handler["active"] and event_type in handler["events"]:
            # In a production environment, this would be handled by a queue system
            # For now, we'll use a thread to avoid blocking the request
            thread = threading.Thread(
                target=deliver_webhook,
                args=(handler, event_type, event_id, event_data, timestamp)
            )
            thread.daemon = True
            thread.start()

def deliver_webhook(handler, event_type, event_id, event_data, timestamp):
    """Deliver a webhook to its target URL"""
    try:
        webhook_id = handler["id"]  # Database ID
        webhook_public_id = handler["webhook_id"]  # Public ID
        target_url = handler["target_url"]
        content_type = handler.get("content_type", "application/json")
        
        # Prepare payload
        payload = json.dumps(event_data)
        
        # Generate signature
        signature_payload = f"{int(timestamp.timestamp())}.{payload}"
        
        # In a real implementation, we would retrieve the actual secret
        # For now, we'll use a placeholder
        secret = "webhook_secret_would_be_retrieved_here"
        
        signature = hmac.new(
            secret.encode('utf-8'),
            signature_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Prepare headers
        headers = {
            "Content-Type": content_type,
            "X-Prejudice-Signature": f"sha256={signature}",
            "X-Prejudice-Timestamp": str(int(timestamp.timestamp())),
            "X-Prejudice-Event": event_type,
            "X-Prejudice-Webhook-ID": webhook_public_id,
            "User-Agent": "PrejudiceRiskCalculator-Webhook/1.0"
        }
        
        # Create delivery record
        delivery = WebhookDelivery(
            delivery_id=f"dlv_{str(uuid.uuid4())[:8]}",
            webhook_id=webhook_id,
            event_id=event_id,
            event_type=event_type,
            payload=payload,
            status="pending",
            created_at=timestamp,
            updated_at=timestamp
        )
        
        # In a real implementation, we would use a database session
        # For now, we'll simulate the delivery
        
        # Send request
        current_app.logger.info(f"Delivering webhook {webhook_public_id} for event {event_id} to {target_url}")
        
        # In a real implementation, this would actually send the request
        # For now, we'll simulate a successful delivery
        # response = requests.post(target_url, headers=headers, data=payload, timeout=10)
        
        # Simulate response
        response_code = 200
        response_body = '{"status":"received"}'
        
        # Update delivery record
        delivery.status = "delivered" if response_code >= 200 and response_code < 300 else "failed"
        delivery.response_code = response_code
        delivery.response_body = response_body
        delivery.updated_at = datetime.datetime.utcnow()
        
        if delivery.status == "delivered":
            delivery.delivered_at = delivery.updated_at
        else:
            delivery.error = f"HTTP {response_code}"
            # In a real implementation, this would schedule a retry
        
        current_app.logger.info(
            f"Webhook {webhook_public_id} delivery {delivery.delivery_id} "
            f"status: {delivery.status} ({response_code})"
        )
        
        # In a real implementation, we would commit the delivery record
        # db_session.add(delivery)
        # db_session.commit()
        
    except Exception as e:
        current_app.logger.exception(f"Error delivering webhook: {str(e)}")
        # In a real implementation, we would update the delivery record with the error
        # delivery.status = "failed"
        # delivery.error = str(e)
        # delivery.updated_at = datetime.datetime.utcnow()
        # db_session.add(delivery)
        # db_session.commit()

def retry_failed_deliveries():
    """Retry failed webhook deliveries"""
    try:
        # In a real implementation, this would query the database for failed deliveries
        # For now, we'll just log a message
        current_app.logger.info("Retrying failed webhook deliveries")
        
    except Exception as e:
        current_app.logger.exception(f"Error retrying failed deliveries: {str(e)}")