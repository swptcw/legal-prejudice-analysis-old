# API Integration Plan for Legal Prejudice Risk Calculator

## Overview

This document outlines the plan for developing API endpoints that will allow the Legal Prejudice Risk Calculator to integrate with case management systems and other legal software. The API will enable seamless data exchange, remote assessment creation, and result retrieval.

## Core API Endpoints

### 1. Assessment Management

#### Create Assessment
- **Endpoint**: `/api/v1/assessments`
- **Method**: POST
- **Purpose**: Create a new prejudice risk assessment
- **Request Body**:
  ```json
  {
    "case_name": "Smith v. Jones",
    "judge_name": "Hon. Robert Williams",
    "assessor_name": "Jane Attorney",
    "assessment_date": "2025-08-29",
    "case_id": "CASE-2025-0429",
    "case_management_system_id": "CMS-12345"
  }
  ```
- **Response**:
  ```json
  {
    "assessment_id": "PRF-2025-0001",
    "status": "created",
    "created_at": "2025-08-29T14:30:00Z",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

#### Retrieve Assessment
- **Endpoint**: `/api/v1/assessments/{assessment_id}`
- **Method**: GET
- **Purpose**: Retrieve an existing assessment
- **Response**:
  ```json
  {
    "assessment_id": "PRF-2025-0001",
    "case_name": "Smith v. Jones",
    "judge_name": "Hon. Robert Williams",
    "assessor_name": "Jane Attorney",
    "assessment_date": "2025-08-29",
    "status": "in_progress",
    "created_at": "2025-08-29T14:30:00Z",
    "updated_at": "2025-08-29T15:45:00Z",
    "factors": [...],
    "results": {...}
  }
  ```

#### Update Assessment
- **Endpoint**: `/api/v1/assessments/{assessment_id}`
- **Method**: PUT
- **Purpose**: Update an existing assessment
- **Request Body**:
  ```json
  {
    "case_name": "Smith v. Jones Corp.",
    "factors": [...]
  }
  ```
- **Response**:
  ```json
  {
    "assessment_id": "PRF-2025-0001",
    "status": "updated",
    "updated_at": "2025-08-29T16:15:00Z"
  }
  ```

#### Delete Assessment
- **Endpoint**: `/api/v1/assessments/{assessment_id}`
- **Method**: DELETE
- **Purpose**: Delete an assessment
- **Response**:
  ```json
  {
    "status": "deleted",
    "deleted_at": "2025-08-29T17:00:00Z"
  }
  ```

### 2. Factor Management

#### Submit Factor Ratings
- **Endpoint**: `/api/v1/assessments/{assessment_id}/factors`
- **Method**: POST
- **Purpose**: Submit ratings for multiple factors
- **Request Body**:
  ```json
  {
    "factors": [
      {
        "id": "financial-direct",
        "likelihood": 4,
        "impact": 5,
        "notes": "Judge owns 1000 shares in defendant corporation"
      },
      {
        "id": "relationship-family",
        "likelihood": 3,
        "impact": 4,
        "notes": "Judge's cousin is married to plaintiff's sister"
      }
    ]
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "factors_updated": 2,
    "updated_at": "2025-08-29T16:30:00Z"
  }
  ```

#### Get Factor Ratings
- **Endpoint**: `/api/v1/assessments/{assessment_id}/factors`
- **Method**: GET
- **Purpose**: Retrieve all factor ratings for an assessment
- **Response**:
  ```json
  {
    "assessment_id": "PRF-2025-0001",
    "factors": [
      {
        "id": "financial-direct",
        "name": "Direct financial interest",
        "category": "relationship",
        "likelihood": 4,
        "impact": 5,
        "score": 20,
        "notes": "Judge owns 1000 shares in defendant corporation"
      },
      ...
    ]
  }
  ```

### 3. Results and Analysis

#### Calculate Results
- **Endpoint**: `/api/v1/assessments/{assessment_id}/calculate`
- **Method**: POST
- **Purpose**: Calculate risk scores based on current factor ratings
- **Response**:
  ```json
  {
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
      },
      ...
    ],
    "recommendations": [
      "File a motion to recuse/disqualify or for disclosure of potential conflicts",
      ...
    ],
    "calculated_at": "2025-08-29T16:45:00Z"
  }
  ```

#### Export Results
- **Endpoint**: `/api/v1/assessments/{assessment_id}/export`
- **Method**: GET
- **Query Parameters**: `format=pdf|json|csv|docx`
- **Purpose**: Export assessment results in various formats
- **Response**: Binary file or JSON data depending on format

### 4. Case Management System Integration

#### Link to Case
- **Endpoint**: `/api/v1/assessments/{assessment_id}/link`
- **Method**: POST
- **Purpose**: Link assessment to a case in external case management system
- **Request Body**:
  ```json
  {
    "cms_type": "Clio",
    "case_id": "CLIO-12345",
    "matter_id": "MATTER-6789",
    "sync_data": true
  }
  ```
- **Response**:
  ```json
  {
    "status": "linked",
    "cms_type": "Clio",
    "case_id": "CLIO-12345",
    "linked_at": "2025-08-29T17:15:00Z"
  }
  ```

#### Sync Case Data
- **Endpoint**: `/api/v1/assessments/{assessment_id}/sync`
- **Method**: POST
- **Purpose**: Sync data between assessment and case management system
- **Response**:
  ```json
  {
    "status": "synced",
    "synced_fields": ["case_name", "judge_name", "dates"],
    "synced_at": "2025-08-29T17:30:00Z"
  }
  ```

### 5. Webhook Notifications

#### Register Webhook
- **Endpoint**: `/api/v1/webhooks`
- **Method**: POST
- **Purpose**: Register a webhook to receive notifications about assessment changes
- **Request Body**:
  ```json
  {
    "target_url": "https://lawfirm.example.com/webhooks/prejudice-calculator",
    "events": ["assessment.created", "assessment.updated", "risk_level.changed"],
    "secret": "webhook_signing_secret"
  }
  ```
- **Response**:
  ```json
  {
    "webhook_id": "wh-12345",
    "status": "active",
    "created_at": "2025-08-29T18:00:00Z"
  }
  ```

## Authentication and Security

### Authentication Methods
1. **API Key Authentication**
   - Header-based API key for simple integrations
   - Example: `Authorization: ApiKey YOUR_API_KEY`

2. **OAuth 2.0**
   - For more secure integrations with case management systems
   - Support for authorization code and client credentials flows
   - Endpoint: `/api/v1/oauth/token`

### Security Measures
1. **Rate Limiting**
   - 100 requests per minute per API key
   - Status endpoint: `/api/v1/rate_limit`

2. **Data Encryption**
   - All API endpoints require HTTPS
   - Sensitive data encrypted at rest

3. **Audit Logging**
   - All API access logged for compliance
   - Logs available via: `/api/v1/audit_logs`

## Integration Partners

### Supported Case Management Systems
1. **Clio**
   - Two-way sync of case details
   - Document attachment support
   - Calendar integration

2. **Practice Panther**
   - Matter linking
   - Contact synchronization
   - Billing integration

3. **MyCase**
   - Document generation
   - Task creation based on risk level
   - Client portal integration

4. **Rocket Matter**
   - Matter linking
   - Calendar integration
   - Billing codes for prejudice-related work

### Document Management Systems
1. **NetDocuments**
   - Assessment storage in matter workspace
   - Version control
   - Permission management

2. **iManage**
   - Workspace integration
   - Document classification
   - Search integration

## Implementation Phases

### Phase 1: Core API (Months 1-2)
- Assessment CRUD operations
- Factor management
- Basic authentication

### Phase 2: Results and Export (Months 2-3)
- Results calculation
- PDF/JSON/CSV export
- Enhanced security

### Phase 3: CMS Integration (Months 3-5)
- Clio integration
- Practice Panther integration
- Webhook system

### Phase 4: Advanced Features (Months 5-6)
- OAuth implementation
- Additional CMS integrations
- Advanced analytics API

## Technical Specifications

### API Technology Stack
- Backend: Node.js with Express or Python with FastAPI
- Database: PostgreSQL
- Authentication: JWT, OAuth 2.0
- Documentation: OpenAPI/Swagger

### Data Models
1. **Assessment**
   - Core assessment metadata
   - Linked case information
   - Status tracking

2. **Factor**
   - Factor definitions
   - Rating data
   - Notes and evidence

3. **Result**
   - Calculated scores
   - Risk levels
   - Recommendations

4. **Integration**
   - CMS connection details
   - Sync status
   - Mapping information

## Documentation and Support

### Developer Resources
- Interactive API documentation (Swagger UI)
- SDK libraries for common languages (JavaScript, Python, PHP)
- Sample code for common integration scenarios
- Postman collection for testing

### Support Channels
- Developer forum
- Integration support email
- Office hours for implementation assistance
- Bug reporting system

## Conclusion

This API integration plan provides a comprehensive roadmap for connecting the Legal Prejudice Risk Calculator with case management systems and other legal software. By implementing these endpoints and following the phased approach, we can create a powerful ecosystem that enhances the utility of the risk calculator in real-world legal practice.