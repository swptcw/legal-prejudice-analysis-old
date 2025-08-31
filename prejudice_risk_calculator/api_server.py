#!/usr/bin/env python3
"""
API Server for Legal Prejudice Risk Calculator
This provides a RESTful API for integrating the calculator with case management systems
"""

from flask import Flask, request, jsonify
import uuid
import datetime
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Data storage (in-memory for demo purposes)
# In a production environment, this would be a database
assessments = {}
factors_data = {}

# Load factor definitions
FACTOR_DEFINITIONS = {
    "relationship": {
        "name": "Relationship-Based",
        "factors": [
            {"id": "financial-direct", "name": "Direct financial interest"},
            {"id": "financial-indirect", "name": "Indirect financial interest"},
            {"id": "relationship-family", "name": "Family relationship"},
            {"id": "relationship-social", "name": "Social/professional relationship"},
            {"id": "political-contributions", "name": "Political contributions"},
            {"id": "ideological-advocacy", "name": "Prior advocacy on disputed issue"}
        ]
    },
    "conduct": {
        "name": "Conduct-Based",
        "factors": [
            {"id": "statements-disparaging", "name": "Disparaging remarks"},
            {"id": "statements-prejudgment", "name": "Expressions indicating prejudgment"},
            {"id": "rulings-onesided", "name": "One-sided evidentiary rulings"},
            {"id": "rulings-unequal", "name": "Unequal allocation of time/resources"},
            {"id": "extrajudicial-public", "name": "Public comments on pending case"},
            {"id": "extrajudicial-media", "name": "Media interviews/social media posts"}
        ]
    },
    "contextual": {
        "name": "Contextual",
        "factors": [
            {"id": "historical-consistent", "name": "Consistent rulings favoring similar parties"},
            {"id": "historical-prior", "name": "Prior reversal for bias"},
            {"id": "procedural-deviation", "name": "Deviation from standard procedures"},
            {"id": "procedural-reasoning", "name": "Failure to provide reasoning"},
            {"id": "external-public", "name": "High-profile case with public pressure"},
            {"id": "external-political", "name": "Political implications for judge"}
        ]
    }
}

# Helper functions
def generate_assessment_id():
    """Generate a unique assessment ID"""
    year = datetime.datetime.now().year
    count = len(assessments) + 1
    return f"PRF-{year}-{count:04d}"

def generate_token():
    """Generate a simple access token"""
    # In a real implementation, this would be a proper JWT
    return str(uuid.uuid4())

def get_timestamp():
    """Get current timestamp in ISO format"""
    return datetime.datetime.utcnow().isoformat() + "Z"

def calculate_risk_score(factor_ratings):
    """Calculate risk scores based on factor ratings"""
    category_scores = {}
    total_score = 0
    factor_count = 0
    
    # Calculate scores for each category
    for category, category_data in FACTOR_DEFINITIONS.items():
        category_total = 0
        category_count = 0
        
        for factor in category_data["factors"]:
            factor_id = factor["id"]
            if factor_id in factor_ratings and "likelihood" in factor_ratings[factor_id] and "impact" in factor_ratings[factor_id]:
                likelihood = factor_ratings[factor_id]["likelihood"]
                impact = factor_ratings[factor_id]["impact"]
                score = likelihood * impact
                
                category_total += score
                category_count += 1
                
                total_score += score
                factor_count += 1
        
        if category_count > 0:
            category_scores[category] = round(category_total / category_count)
    
    # Calculate overall score
    overall_score = round(total_score / factor_count) if factor_count > 0 else 0
    
    # Determine risk level
    if overall_score >= 20:
        risk_level = "Critical"
    elif overall_score >= 15:
        risk_level = "High"
    elif overall_score >= 8:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    # Get high risk factors
    high_risk_factors = []
    for category, category_data in FACTOR_DEFINITIONS.items():
        for factor in category_data["factors"]:
            factor_id = factor["id"]
            if factor_id in factor_ratings and "likelihood" in factor_ratings[factor_id] and "impact" in factor_ratings[factor_id]:
                likelihood = factor_ratings[factor_id]["likelihood"]
                impact = factor_ratings[factor_id]["impact"]
                score = likelihood * impact
                
                if score >= 15:
                    high_risk_factors.append({
                        "id": factor_id,
                        "name": factor["name"],
                        "category": category_data["name"],
                        "score": score
                    })
    
    # Sort high risk factors by score (highest first)
    high_risk_factors.sort(key=lambda x: x["score"], reverse=True)
    
    # Generate recommendations based on risk level
    recommendations = []
    if risk_level == "Critical":
        recommendations = [
            "File a formal motion to recuse/disqualify immediately",
            "Consider motion to stay proceedings pending resolution",
            "Prepare detailed affidavit documenting all prejudice factors",
            "Consult with appellate counsel regarding potential mandamus relief",
            "Implement comprehensive documentation protocol for all interactions"
        ]
    elif risk_level == "High":
        recommendations = [
            "File a motion to recuse/disqualify or for disclosure of potential conflicts",
            "Consider requesting a hearing on prejudice concerns",
            "Develop detailed documentation of all prejudice indicators",
            "Implement strategic adjustments to case presentation",
            "Prepare record for potential appeal on prejudice grounds"
        ]
    elif risk_level == "Medium":
        recommendations = [
            "Enhance documentation of potential prejudice indicators",
            "Consider strategic motion practice to test for bias",
            "Modify case presentation approach to mitigate prejudice impact",
            "Request written rulings for significant decisions",
            "Preserve all procedural objections related to potential prejudice"
        ]
    else:  # Low
        recommendations = [
            "Document potential prejudice indicators as they arise",
            "Track rulings for emerging patterns",
            "Compare treatment with opposing party",
            "Maintain professional conduct to avoid escalation",
            "Reassess risk level periodically throughout proceedings"
        ]
    
    return {
        "overall_score": overall_score,
        "risk_level": risk_level,
        "category_scores": category_scores,
        "high_risk_factors": high_risk_factors,
        "recommendations": recommendations,
        "calculated_at": get_timestamp()
    }

# API Authentication middleware
def authenticate_request():
    """Simple API key authentication"""
    api_key = request.headers.get('Authorization')
    if not api_key or not api_key.startswith('ApiKey '):
        return False
    
    # In a real implementation, this would validate against stored API keys
    # For demo purposes, accept any key that starts with "TEST_"
    key = api_key.replace('ApiKey ', '')
    return key.startswith('TEST_')

# API Routes
@app.route('/api/v1/assessments', methods=['POST'])
def create_assessment():
    """Create a new prejudice risk assessment"""
    if not authenticate_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ["case_name", "judge_name", "assessor_name"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Generate assessment ID and token
        assessment_id = generate_assessment_id()
        access_token = generate_token()
        timestamp = get_timestamp()
        
        # Create assessment record
        assessment = {
            "assessment_id": assessment_id,
            "case_name": data["case_name"],
            "judge_name": data["judge_name"],
            "assessor_name": data["assessor_name"],
            "assessment_date": data.get("assessment_date", timestamp.split("T")[0]),
            "case_id": data.get("case_id", ""),
            "case_management_system_id": data.get("case_management_system_id", ""),
            "status": "created",
            "created_at": timestamp,
            "updated_at": timestamp,
            "access_token": access_token
        }
        
        # Store assessment
        assessments[assessment_id] = assessment
        factors_data[assessment_id] = {}
        
        # Log creation
        logger.info(f"Assessment created: {assessment_id}")
        
        # Return response
        return jsonify({
            "assessment_id": assessment_id,
            "status": "created",
            "created_at": timestamp,
            "access_token": access_token
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating assessment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/assessments/<assessment_id>', methods=['GET'])
def get_assessment(assessment_id):
    """Retrieve an existing assessment"""
    if not authenticate_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Check if assessment exists
        if assessment_id not in assessments:
            return jsonify({"error": "Assessment not found"}), 404
        
        # Get assessment data
        assessment = assessments[assessment_id].copy()
        
        # Remove access token from response
        if "access_token" in assessment:
            del assessment["access_token"]
        
        # Add factors if available
        if assessment_id in factors_data:
            factor_list = []
            for factor_id, factor_data in factors_data[assessment_id].items():
                # Find factor name and category
                factor_name = ""
                factor_category = ""
                for category, category_data in FACTOR_DEFINITIONS.items():
                    for factor in category_data["factors"]:
                        if factor["id"] == factor_id:
                            factor_name = factor["name"]
                            factor_category = category_data["name"]
                            break
                
                # Calculate score if likelihood and impact are available
                score = 0
                if "likelihood" in factor_data and "impact" in factor_data:
                    score = factor_data["likelihood"] * factor_data["impact"]
                
                factor_list.append({
                    "id": factor_id,
                    "name": factor_name,
                    "category": factor_category,
                    "likelihood": factor_data.get("likelihood", 0),
                    "impact": factor_data.get("impact", 0),
                    "score": score,
                    "notes": factor_data.get("notes", "")
                })
            
            assessment["factors"] = factor_list
        
        # Log retrieval
        logger.info(f"Assessment retrieved: {assessment_id}")
        
        return jsonify(assessment), 200
        
    except Exception as e:
        logger.error(f"Error retrieving assessment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/assessments/<assessment_id>', methods=['PUT'])
def update_assessment(assessment_id):
    """Update an existing assessment"""
    if not authenticate_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Check if assessment exists
        if assessment_id not in assessments:
            return jsonify({"error": "Assessment not found"}), 404
        
        data = request.json
        timestamp = get_timestamp()
        
        # Update assessment fields
        for field in ["case_name", "judge_name", "assessor_name", "assessment_date", "case_id", "case_management_system_id"]:
            if field in data:
                assessments[assessment_id][field] = data[field]
        
        # Update timestamp
        assessments[assessment_id]["updated_at"] = timestamp
        assessments[assessment_id]["status"] = "updated"
        
        # Log update
        logger.info(f"Assessment updated: {assessment_id}")
        
        return jsonify({
            "assessment_id": assessment_id,
            "status": "updated",
            "updated_at": timestamp
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating assessment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/assessments/<assessment_id>', methods=['DELETE'])
def delete_assessment(assessment_id):
    """Delete an assessment"""
    if not authenticate_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Check if assessment exists
        if assessment_id not in assessments:
            return jsonify({"error": "Assessment not found"}), 404
        
        timestamp = get_timestamp()
        
        # Delete assessment and factors
        del assessments[assessment_id]
        if assessment_id in factors_data:
            del factors_data[assessment_id]
        
        # Log deletion
        logger.info(f"Assessment deleted: {assessment_id}")
        
        return jsonify({
            "status": "deleted",
            "deleted_at": timestamp
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting assessment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/assessments/<assessment_id>/factors', methods=['POST'])
def submit_factor_ratings(assessment_id):
    """Submit ratings for multiple factors"""
    if not authenticate_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Check if assessment exists
        if assessment_id not in assessments:
            return jsonify({"error": "Assessment not found"}), 404
        
        data = request.json
        timestamp = get_timestamp()
        
        # Validate request
        if "factors" not in data or not isinstance(data["factors"], list):
            return jsonify({"error": "Invalid request format"}), 400
        
        # Initialize factors data if not exists
        if assessment_id not in factors_data:
            factors_data[assessment_id] = {}
        
        # Process factors
        factors_updated = 0
        for factor in data["factors"]:
            # Validate factor data
            if "id" not in factor:
                continue
            
            factor_id = factor["id"]
            
            # Check if factor exists in definitions
            factor_exists = False
            for category, category_data in FACTOR_DEFINITIONS.items():
                for def_factor in category_data["factors"]:
                    if def_factor["id"] == factor_id:
                        factor_exists = True
                        break
                if factor_exists:
                    break
            
            if not factor_exists:
                continue
            
            # Initialize factor data if not exists
            if factor_id not in factors_data[assessment_id]:
                factors_data[assessment_id][factor_id] = {}
            
            # Update factor data
            for field in ["likelihood", "impact", "notes"]:
                if field in factor:
                    factors_data[assessment_id][factor_id][field] = factor[field]
            
            factors_updated += 1
        
        # Update assessment status
        assessments[assessment_id]["status"] = "in_progress"
        assessments[assessment_id]["updated_at"] = timestamp
        
        # Log update
        logger.info(f"Factor ratings submitted for assessment {assessment_id}: {factors_updated} factors updated")
        
        return jsonify({
            "status": "success",
            "factors_updated": factors_updated,
            "updated_at": timestamp
        }), 200
        
    except Exception as e:
        logger.error(f"Error submitting factor ratings: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/assessments/<assessment_id>/factors', methods=['GET'])
def get_factor_ratings(assessment_id):
    """Retrieve all factor ratings for an assessment"""
    if not authenticate_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Check if assessment exists
        if assessment_id not in assessments:
            return jsonify({"error": "Assessment not found"}), 404
        
        # Check if factors exist
        if assessment_id not in factors_data:
            return jsonify({
                "assessment_id": assessment_id,
                "factors": []
            }), 200
        
        # Prepare factor list
        factor_list = []
        for factor_id, factor_data in factors_data[assessment_id].items():
            # Find factor name and category
            factor_name = ""
            factor_category = ""
            category_name = ""
            for category, category_data in FACTOR_DEFINITIONS.items():
                for factor in category_data["factors"]:
                    if factor["id"] == factor_id:
                        factor_name = factor["name"]
                        factor_category = category
                        category_name = category_data["name"]
                        break
            
            # Calculate score if likelihood and impact are available
            score = 0
            if "likelihood" in factor_data and "impact" in factor_data:
                score = factor_data["likelihood"] * factor_data["impact"]
            
            factor_list.append({
                "id": factor_id,
                "name": factor_name,
                "category": category_name,
                "category_id": factor_category,
                "likelihood": factor_data.get("likelihood", 0),
                "impact": factor_data.get("impact", 0),
                "score": score,
                "notes": factor_data.get("notes", "")
            })
        
        # Log retrieval
        logger.info(f"Factor ratings retrieved for assessment {assessment_id}")
        
        return jsonify({
            "assessment_id": assessment_id,
            "factors": factor_list
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving factor ratings: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/assessments/<assessment_id>/calculate', methods=['POST'])
def calculate_results(assessment_id):
    """Calculate risk scores based on current factor ratings"""
    if not authenticate_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Check if assessment exists
        if assessment_id not in assessments:
            return jsonify({"error": "Assessment not found"}), 404
        
        # Check if factors exist
        if assessment_id not in factors_data or not factors_data[assessment_id]:
            return jsonify({"error": "No factor ratings found"}), 400
        
        # Calculate risk scores
        results = calculate_risk_score(factors_data[assessment_id])
        
        # Update assessment status
        timestamp = get_timestamp()
        assessments[assessment_id]["status"] = "calculated"
        assessments[assessment_id]["updated_at"] = timestamp
        
        # Store results
        assessments[assessment_id]["results"] = results
        
        # Add assessment ID to results
        results["assessment_id"] = assessment_id
        
        # Log calculation
        logger.info(f"Results calculated for assessment {assessment_id}: Risk level {results['risk_level']}")
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Error calculating results: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/assessments/<assessment_id>/link', methods=['POST'])
def link_to_case(assessment_id):
    """Link assessment to a case in external case management system"""
    if not authenticate_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Check if assessment exists
        if assessment_id not in assessments:
            return jsonify({"error": "Assessment not found"}), 404
        
        data = request.json
        timestamp = get_timestamp()
        
        # Validate required fields
        required_fields = ["cms_type", "case_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Update assessment with CMS information
        assessments[assessment_id]["cms_type"] = data["cms_type"]
        assessments[assessment_id]["cms_case_id"] = data["case_id"]
        assessments[assessment_id]["cms_matter_id"] = data.get("matter_id", "")
        assessments[assessment_id]["cms_sync_data"] = data.get("sync_data", False)
        assessments[assessment_id]["cms_linked_at"] = timestamp
        assessments[assessment_id]["updated_at"] = timestamp
        
        # Log linking
        logger.info(f"Assessment {assessment_id} linked to {data['cms_type']} case {data['case_id']}")
        
        return jsonify({
            "status": "linked",
            "cms_type": data["cms_type"],
            "case_id": data["case_id"],
            "linked_at": timestamp
        }), 200
        
    except Exception as e:
        logger.error(f"Error linking assessment to case: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/factor_definitions', methods=['GET'])
def get_factor_definitions():
    """Get all factor definitions"""
    if not authenticate_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        return jsonify(FACTOR_DEFINITIONS), 200
        
    except Exception as e:
        logger.error(f"Error retrieving factor definitions: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/status', methods=['GET'])
def get_api_status():
    """Get API status"""
    return jsonify({
        "status": "operational",
        "version": "1.0.0",
        "timestamp": get_timestamp(),
        "assessments_count": len(assessments)
    }), 200

# Main entry point
if __name__ == '__main__':
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=True)