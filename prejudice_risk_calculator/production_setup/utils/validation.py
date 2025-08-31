"""
Validation utilities for request data
"""

def validate_assessment_data(data):
    """Validate assessment creation/update data"""
    errors = {}
    
    # Required fields
    required_fields = ["case_name", "judge_name", "assessor_name"]
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"{field} is required"
    
    # Field length validations
    if "case_name" in data and len(data["case_name"]) > 255:
        errors["case_name"] = "case_name must be 255 characters or less"
    
    if "judge_name" in data and len(data["judge_name"]) > 255:
        errors["judge_name"] = "judge_name must be 255 characters or less"
    
    if "assessor_name" in data and len(data["assessor_name"]) > 255:
        errors["assessor_name"] = "assessor_name must be 255 characters or less"
    
    # Date format validation
    if "assessment_date" in data:
        try:
            # Simple format check - a more robust implementation would use datetime.strptime
            parts = data["assessment_date"].split("-")
            if len(parts) != 3 or len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
                errors["assessment_date"] = "assessment_date must be in YYYY-MM-DD format"
        except:
            errors["assessment_date"] = "assessment_date must be in YYYY-MM-DD format"
    
    return errors

def validate_factor_data(data, require_id=True):
    """Validate factor data"""
    errors = {}
    
    # Required fields
    if require_id and ("id" not in data or not data["id"]):
        errors["id"] = "id is required"
    
    # Validate likelihood if present
    if "likelihood" in data:
        try:
            likelihood = int(data["likelihood"])
            if likelihood < 1 or likelihood > 5:
                errors["likelihood"] = "likelihood must be between 1 and 5"
        except:
            errors["likelihood"] = "likelihood must be an integer"
    
    # Validate impact if present
    if "impact" in data:
        try:
            impact = int(data["impact"])
            if impact < 1 or impact > 5:
                errors["impact"] = "impact must be between 1 and 5"
        except:
            errors["impact"] = "impact must be an integer"
    
    # Validate notes if present
    if "notes" in data and data["notes"] is not None and len(data["notes"]) > 10000:
        errors["notes"] = "notes must be 10000 characters or less"
    
    return errors

def validate_cms_link_data(data):
    """Validate CMS link data"""
    errors = {}
    
    # Required fields
    required_fields = ["cms_type", "case_id"]
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"{field} is required"
    
    # Field length validations
    if "cms_type" in data and len(data["cms_type"]) > 100:
        errors["cms_type"] = "cms_type must be 100 characters or less"
    
    if "case_id" in data and len(data["case_id"]) > 100:
        errors["case_id"] = "case_id must be 100 characters or less"
    
    if "matter_id" in data and data["matter_id"] and len(data["matter_id"]) > 100:
        errors["matter_id"] = "matter_id must be 100 characters or less"
    
    # Type validations
    if "sync_data" in data and not isinstance(data["sync_data"], bool):
        errors["sync_data"] = "sync_data must be a boolean"
    
    return errors

def validate_webhook_data(data):
    """Validate webhook data"""
    errors = {}
    
    # Required fields
    required_fields = ["target_url", "events", "secret"]
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"{field} is required"
    
    # URL validation
    if "target_url" in data:
        url = data["target_url"]
        if not url.startswith(("http://", "https://")):
            errors["target_url"] = "target_url must be a valid HTTP or HTTPS URL"
        elif len(url) > 255:
            errors["target_url"] = "target_url must be 255 characters or less"
    
    # Events validation
    if "events" in data:
        if not isinstance(data["events"], list):
            errors["events"] = "events must be an array"
        elif not data["events"]:
            errors["events"] = "events array cannot be empty"
        else:
            valid_events = [
                "assessment.created", "assessment.updated", "assessment.deleted",
                "factor.updated", "result.calculated", "risk_level.changed",
                "link.created", "link.updated", "link.deleted"
            ]
            invalid_events = [event for event in data["events"] if event not in valid_events]
            if invalid_events:
                errors["events"] = f"Invalid events: {', '.join(invalid_events)}"
    
    # Secret validation
    if "secret" in data:
        if len(data["secret"]) < 16:
            errors["secret"] = "secret must be at least 16 characters"
        elif len(data["secret"]) > 100:
            errors["secret"] = "secret must be 100 characters or less"
    
    # Content type validation
    if "content_type" in data:
        valid_content_types = ["application/json", "application/x-www-form-urlencoded"]
        if data["content_type"] not in valid_content_types:
            errors["content_type"] = f"content_type must be one of: {', '.join(valid_content_types)}"
    
    return errors