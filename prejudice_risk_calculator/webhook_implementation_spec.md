# Legal Prejudice Risk Calculator
## Webhook Implementation Specification

This document provides technical specifications for implementing webhooks in the Legal Prejudice Risk Calculator API. Webhooks enable real-time communication between the Calculator and integrated case management systems, ensuring that both systems remain synchronized.

## Table of Contents

1. [Overview](#overview)
2. [Webhook Architecture](#webhook-architecture)
3. [Event Types](#event-types)
4. [Webhook Registration](#webhook-registration)
5. [Payload Format](#payload-format)
6. [Security Considerations](#security-considerations)
7. [Retry Logic](#retry-logic)
8. [Webhook Management](#webhook-management)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Testing Guidelines](#testing-guidelines)

## Overview

Webhooks provide a mechanism for the Legal Prejudice Risk Calculator to notify external systems about events in real-time. When an event occurs (such as an assessment being updated), the Calculator sends an HTTP POST request to a pre-configured URL with information about the event.

### Key Benefits

- **Real-time Updates**: Case management systems receive immediate notifications about changes
- **Reduced Polling**: Eliminates the need for frequent API polling to check for updates
- **Workflow Automation**: Enables automated workflows based on assessment events
- **Data Consistency**: Ensures CMS data remains synchronized with assessment data
- **User Experience**: Provides immediate feedback to users when changes occur

## Webhook Architecture

```
┌─────────────────────┐                  ┌─────────────────────┐
│                     │                  │                     │
│  Legal Prejudice    │  HTTP POST       │  Case Management    │
│  Risk Calculator    ├─────────────────►│  System             │
│                     │                  │                     │
└─────────────────────┘                  └─────────────────────┘
         │                                        │
         │                                        │
         ▼                                        ▼
┌─────────────────────┐                  ┌─────────────────────┐
│                     │                  │                     │
│  Event Tracking     │                  │  Webhook Handler    │
│  System             │                  │                     │
│                     │                  │                     │
└─────────────────────┘                  └─────────────────────┘
         │                                        │
         │                                        │
         ▼                                        ▼
┌─────────────────────┐                  ┌─────────────────────┐
│                     │                  │                     │
│  Delivery           │                  │  Business Logic     │
│  Management         │                  │  Processing         │
│                     │                  │                     │
└─────────────────────┘                  └─────────────────────┘
```

### Components

1. **Event Tracking System**: Monitors and captures events within the Calculator
2. **Delivery Management**: Handles webhook delivery, retries, and logging
3. **Webhook Handler**: Receives and processes webhook payloads in the CMS
4. **Business Logic Processing**: Takes action based on webhook events in the CMS

## Event Types

The following event types will be supported by the webhook system:

| Event Type | Description | Trigger |
|------------|-------------|---------|
| `assessment.created` | New assessment created | When a new assessment is created |
| `assessment.updated` | Assessment details updated | When assessment metadata is changed |
| `assessment.deleted` | Assessment deleted | When an assessment is deleted |
| `factor.updated` | Factor ratings changed | When factor ratings are submitted or modified |
| `result.calculated` | Risk scores calculated | When risk calculation is performed |
| `risk_level.changed` | Risk level changed | When risk level changes (e.g., Medium to High) |
| `link.created` | CMS link established | When assessment is linked to a CMS case |
| `link.updated` | CMS link updated | When CMS link details are updated |
| `link.deleted` | CMS link removed | When assessment is unlinked from a CMS case |

## Webhook Registration

### Registration Endpoint

```
POST /api/v1/webhooks
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target_url` | String | Yes | URL where webhook payloads will be sent |
| `events` | Array | Yes | Array of event types to subscribe to |
| `description` | String | No | Human-readable description of the webhook |
| `secret` | String | Yes | Secret used to sign webhook payloads |
| `active` | Boolean | No | Whether the webhook is active (default: true) |
| `content_type` | String | No | Preferred content type (default: application/json) |

### Example Request

```json
{
  "target_url": "https://cms.example.com/webhooks/prejudice-calculator",
  "events": ["assessment.created", "result.calculated", "risk_level.changed"],
  "description": "Production webhook for Clio integration",
  "secret": "whsec_8fhsi2uehf28h38hd82h38hd82h3",
  "active": true,
  "content_type": "application/json"
}
```

### Example Response

```json
{
  "webhook_id": "wh_1234567890",
  "target_url": "https://cms.example.com/webhooks/prejudice-calculator",
  "events": ["assessment.created", "result.calculated", "risk_level.changed"],
  "description": "Production webhook for Clio integration",
  "active": true,
  "content_type": "application/json",
  "created_at": "2025-08-29T18:00:00Z"
}
```

## Payload Format

### Common Fields

All webhook payloads include the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Unique identifier for the webhook event |
| `event` | String | Type of event that occurred |
| `created_at` | String | ISO 8601 timestamp when the event occurred |
| `data` | Object | Event-specific data payload |
| `api_version` | String | Version of the API that generated the event |

### Event-Specific Payloads

#### assessment.created

```json
{
  "id": "evt_1234567890",
  "event": "assessment.created",
  "created_at": "2025-08-29T18:00:00Z",
  "api_version": "v1",
  "data": {
    "assessment_id": "PRF-2025-0001",
    "case_name": "Smith v. Jones Corporation",
    "judge_name": "Hon. Robert Williams",
    "assessor_name": "Jane Attorney",
    "assessment_date": "2025-08-29",
    "case_id": "CASE-2025-0429",
    "case_management_system_id": "CMS-12345",
    "status": "created"
  }
}
```

#### factor.updated

```json
{
  "id": "evt_1234567891",
  "event": "factor.updated",
  "created_at": "2025-08-29T18:15:00Z",
  "api_version": "v1",
  "data": {
    "assessment_id": "PRF-2025-0001",
    "factors_updated": [
      {
        "id": "financial-direct",
        "name": "Direct financial interest",
        "category": "Relationship-Based",
        "likelihood": 4,
        "impact": 5,
        "score": 20
      },
      {
        "id": "relationship-family",
        "name": "Family relationship",
        "category": "Relationship-Based",
        "likelihood": 3,
        "impact": 4,
        "score": 12
      }
    ],
    "updated_by": "Jane Attorney"
  }
}
```

#### result.calculated

```json
{
  "id": "evt_1234567892",
  "event": "result.calculated",
  "created_at": "2025-08-29T18:30:00Z",
  "api_version": "v1",
  "data": {
    "assessment_id": "PRF-2025-0001",
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
    "calculated_by": "Jane Attorney"
  }
}
```

#### risk_level.changed

```json
{
  "id": "evt_1234567893",
  "event": "risk_level.changed",
  "created_at": "2025-08-29T18:30:00Z",
  "api_version": "v1",
  "data": {
    "assessment_id": "PRF-2025-0001",
    "previous_level": "Medium",
    "new_level": "High",
    "previous_score": 14,
    "new_score": 18,
    "changed_factors": [
      {
        "id": "financial-direct",
        "previous_score": 12,
        "new_score": 20
      }
    ]
  }
}
```

## Security Considerations

### Payload Signing

All webhook payloads are signed using HMAC-SHA256 to verify their authenticity. The signature is included in the `X-Prejudice-Signature` header.

#### Signature Generation

1. The Calculator concatenates the timestamp and the JSON payload: `{timestamp}.{payload}`
2. The Calculator generates an HMAC-SHA256 signature using the webhook secret
3. The signature is added to the request headers

#### Signature Verification

```python
import hmac
import hashlib

def verify_signature(payload_body, timestamp, signature, secret):
    """Verify webhook signature"""
    # Concatenate timestamp and payload
    signed_payload = f"{timestamp}.{payload_body}"
    
    # Generate expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures using constant-time comparison
    return hmac.compare_digest(expected_signature, signature)
```

### Additional Security Headers

| Header | Description |
|--------|-------------|
| `X-Prejudice-Signature` | HMAC-SHA256 signature of the payload |
| `X-Prejudice-Timestamp` | Timestamp when the webhook was sent |
| `X-Prejudice-Event` | Type of event that triggered the webhook |
| `X-Prejudice-Webhook-ID` | ID of the webhook configuration |
| `User-Agent` | Set to "PrejudiceRiskCalculator-Webhook/1.0" |

### Security Best Practices

1. **Validate Signatures**: Always verify webhook signatures before processing
2. **Check Timestamp**: Reject webhooks with timestamps older than 5 minutes
3. **Use HTTPS**: Only accept webhooks over HTTPS connections
4. **Implement Timeouts**: Set reasonable timeouts for webhook processing
5. **Rate Limiting**: Implement rate limiting to prevent abuse
6. **IP Filtering**: Consider restricting webhooks to known IP ranges
7. **Idempotency**: Process webhooks idempotently to handle duplicates
8. **Secure Secrets**: Store webhook secrets securely and rotate regularly

## Retry Logic

### Retry Schedule

If a webhook delivery fails (non-2xx response), the system will retry with exponential backoff:

1. Initial retry: 1 minute after failure
2. Second retry: 5 minutes after first retry
3. Third retry: 15 minutes after second retry
4. Fourth retry: 30 minutes after third retry
5. Fifth retry: 1 hour after fourth retry
6. Final retry: 3 hours after fifth retry

After all retries are exhausted, the webhook will be marked as failed and require manual intervention.

### Retry Headers

Each retry includes additional headers:

| Header | Description |
|--------|-------------|
| `X-Prejudice-Retry-Count` | Number of retry attempts (starting at 1) |
| `X-Prejudice-Retry-Reason` | Reason for the retry (e.g., "timeout", "server_error") |
| `X-Prejudice-Original-Timestamp` | Timestamp of the original webhook attempt |

### Webhook Logs

All webhook delivery attempts are logged and accessible via the API:

```
GET /api/v1/webhooks/{webhook_id}/deliveries
```

Example response:

```json
{
  "webhook_id": "wh_1234567890",
  "deliveries": [
    {
      "id": "dlv_1234567890",
      "event_id": "evt_1234567890",
      "event_type": "assessment.created",
      "target_url": "https://cms.example.com/webhooks/prejudice-calculator",
      "status": "delivered",
      "response_code": 200,
      "response_body": "{&quot;status&quot;:&quot;received&quot;}",
      "created_at": "2025-08-29T18:00:00Z",
      "delivered_at": "2025-08-29T18:00:01Z"
    },
    {
      "id": "dlv_1234567891",
      "event_id": "evt_1234567891",
      "event_type": "factor.updated",
      "target_url": "https://cms.example.com/webhooks/prejudice-calculator",
      "status": "failed",
      "response_code": 500,
      "error": "Internal Server Error",
      "retry_count": 6,
      "created_at": "2025-08-29T18:15:00Z",
      "last_attempt_at": "2025-08-29T22:50:00Z"
    }
  ]
}
```

## Webhook Management

### Listing Webhooks

```
GET /api/v1/webhooks
```

Example response:

```json
{
  "webhooks": [
    {
      "webhook_id": "wh_1234567890",
      "target_url": "https://cms.example.com/webhooks/prejudice-calculator",
      "events": ["assessment.created", "result.calculated", "risk_level.changed"],
      "description": "Production webhook for Clio integration",
      "active": true,
      "created_at": "2025-08-29T18:00:00Z"
    },
    {
      "webhook_id": "wh_1234567891",
      "target_url": "https://cms.example.com/webhooks/test",
      "events": ["assessment.created"],
      "description": "Test webhook",
      "active": false,
      "created_at": "2025-08-28T12:00:00Z"
    }
  ]
}
```

### Retrieving a Webhook

```
GET /api/v1/webhooks/{webhook_id}
```

Example response:

```json
{
  "webhook_id": "wh_1234567890",
  "target_url": "https://cms.example.com/webhooks/prejudice-calculator",
  "events": ["assessment.created", "result.calculated", "risk_level.changed"],
  "description": "Production webhook for Clio integration",
  "active": true,
  "content_type": "application/json",
  "created_at": "2025-08-29T18:00:00Z",
  "updated_at": "2025-08-29T18:00:00Z",
  "last_successful_delivery": "2025-08-29T18:30:01Z",
  "delivery_success_rate": 0.95
}
```

### Updating a Webhook

```
PUT /api/v1/webhooks/{webhook_id}
```

Example request:

```json
{
  "events": ["assessment.created", "assessment.updated", "result.calculated", "risk_level.changed"],
  "description": "Updated production webhook for Clio integration",
  "active": true
}
```

Example response:

```json
{
  "webhook_id": "wh_1234567890",
  "target_url": "https://cms.example.com/webhooks/prejudice-calculator",
  "events": ["assessment.created", "assessment.updated", "result.calculated", "risk_level.changed"],
  "description": "Updated production webhook for Clio integration",
  "active": true,
  "content_type": "application/json",
  "created_at": "2025-08-29T18:00:00Z",
  "updated_at": "2025-08-29T19:00:00Z"
}
```

### Deleting a Webhook

```
DELETE /api/v1/webhooks/{webhook_id}
```

Example response:

```json
{
  "webhook_id": "wh_1234567890",
  "deleted": true,
  "deleted_at": "2025-08-29T20:00:00Z"
}
```

## Implementation Roadmap

### Phase 1: Core Webhook Infrastructure (Months 1-2)

1. **Webhook Registration API**
   - Implement webhook registration endpoints
   - Create webhook database schema
   - Develop webhook configuration management

2. **Event Tracking System**
   - Implement event listeners for core events
   - Create event queue system
   - Develop event filtering based on subscriptions

3. **Basic Delivery System**
   - Implement webhook delivery mechanism
   - Create signature generation
   - Develop basic retry logic

### Phase 2: Enhanced Features (Months 2-3)

1. **Advanced Retry Logic**
   - Implement exponential backoff
   - Create delivery status tracking
   - Develop manual retry functionality

2. **Webhook Logs**
   - Implement delivery logging
   - Create log retrieval API
   - Develop log retention policies

3. **Security Enhancements**
   - Implement IP filtering
   - Create webhook secret rotation
   - Develop rate limiting

### Phase 3: Management & Monitoring (Months 3-4)

1. **Webhook Dashboard**
   - Create webhook management UI
   - Implement delivery monitoring
   - Develop performance analytics

2. **Alerting System**
   - Implement failure alerting
   - Create delivery performance monitoring
   - Develop anomaly detection

3. **Documentation & Examples**
   - Create implementation guides for CMS vendors
   - Develop example webhook handlers
   - Create testing tools

## Testing Guidelines

### Webhook Testing Endpoint

A dedicated testing endpoint is available for webhook development and testing:

```
POST /api/v1/webhooks/test
```

Example request:

```json
{
  "target_url": "https://requestbin.com/r/your-test-endpoint",
  "event": "assessment.created",
  "include_sample_data": true
}
```

Example response:

```json
{
  "test_id": "test_1234567890",
  "target_url": "https://requestbin.com/r/your-test-endpoint",
  "event": "assessment.created",
  "status": "delivered",
  "response_code": 200,
  "response_body": "{&quot;status&quot;:&quot;received&quot;}",
  "request_headers": {
    "X-Prejudice-Signature": "sha256=...",
    "X-Prejudice-Timestamp": "2025-08-29T18:00:00Z",
    "X-Prejudice-Event": "assessment.created",
    "Content-Type": "application/json"
  },
  "request_body": "{&quot;id&quot;:&quot;evt_test&quot;,&quot;event&quot;:&quot;assessment.created&quot;,...}",
  "created_at": "2025-08-29T18:00:00Z",
  "delivered_at": "2025-08-29T18:00:01Z"
}
```

### Testing Best Practices

1. **Use Test Mode**: Register webhooks in test mode during development
2. **Verify Signatures**: Implement signature verification from the start
3. **Handle Duplicates**: Design handlers to be idempotent
4. **Log Payloads**: Store raw webhook payloads for debugging
5. **Implement Timeouts**: Set appropriate timeouts for webhook processing
6. **Test Failure Scenarios**: Verify retry behavior by simulating failures
7. **Load Testing**: Test webhook handler performance under load
8. **Monitor Deliveries**: Track webhook delivery success rates

### Sample Webhook Handler

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import time
import json

app = Flask(__name__)

# Your webhook secret
WEBHOOK_SECRET = "whsec_8fhsi2uehf28h38hd82h38hd82h3"

@app.route('/webhooks/prejudice-calculator', methods=['POST'])
def handle_webhook():
    # Get the signature and timestamp from headers
    signature = request.headers.get('X-Prejudice-Signature', '')
    timestamp = request.headers.get('X-Prejudice-Timestamp', '')
    event_type = request.headers.get('X-Prejudice-Event', '')
    
    # Get the raw request body
    payload_body = request.data.decode('utf-8')
    
    # Verify the signature
    if not verify_signature(payload_body, timestamp, signature, WEBHOOK_SECRET):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Check timestamp to prevent replay attacks
    current_time = time.time()
    webhook_time = int(timestamp)
    if current_time - webhook_time > 300:  # 5 minutes
        return jsonify({"error": "Webhook too old"}), 400
    
    # Parse the payload
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400
    
    # Process the webhook based on event type
    if event_type == 'assessment.created':
        process_assessment_created(payload)
    elif event_type == 'result.calculated':
        process_result_calculated(payload)
    elif event_type == 'risk_level.changed':
        process_risk_level_changed(payload)
    else:
        # Log unknown event type but return success
        print(f"Unknown event type: {event_type}")
    
    # Return success response
    return jsonify({"status": "received"}), 200

def verify_signature(payload_body, timestamp, signature, secret):
    """Verify webhook signature"""
    # Concatenate timestamp and payload
    signed_payload = f"{timestamp}.{payload_body}"
    
    # Generate expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures using constant-time comparison
    return hmac.compare_digest(expected_signature, signature)

def process_assessment_created(payload):
    """Process assessment.created event"""
    assessment_id = payload['data']['assessment_id']
    case_name = payload['data']['case_name']
    judge_name = payload['data']['judge_name']
    
    print(f"New assessment created: {assessment_id} for case {case_name} with judge {judge_name}")
    # Add your business logic here

def process_result_calculated(payload):
    """Process result.calculated event"""
    assessment_id = payload['data']['assessment_id']
    risk_level = payload['data']['risk_level']
    overall_score = payload['data']['overall_score']
    
    print(f"Results calculated for assessment {assessment_id}: {risk_level} (score: {overall_score})")
    # Add your business logic here

def process_risk_level_changed(payload):
    """Process risk_level.changed event"""
    assessment_id = payload['data']['assessment_id']
    previous_level = payload['data']['previous_level']
    new_level = payload['data']['new_level']
    
    print(f"Risk level changed for assessment {assessment_id}: {previous_level} -> {new_level}")
    # Add your business logic here

if __name__ == '__main__':
    app.run(port=5000)
```

## Conclusion

This webhook implementation specification provides a comprehensive guide for implementing real-time event notifications between the Legal Prejudice Risk Calculator and integrated case management systems. By following these guidelines, developers can create robust, secure, and efficient webhook integrations that enhance the user experience and ensure data consistency across systems.

For additional assistance or custom integration needs, contact our integration team at integration-support@prejudicerisk.example.com.