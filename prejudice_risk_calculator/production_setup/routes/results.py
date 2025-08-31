"""
Routes for risk calculation results
"""

import datetime
import json
from flask import Blueprint, jsonify, request, current_app, g
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound, BadRequest
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from models import Assessment, Factor, Result, RiskLevel, FactorDefinition
from utils.auth import require_api_key
from utils.events import trigger_event

# Create blueprint
results_bp = Blueprint('results', __name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def calculate_risk_score(assessment):
    """Calculate risk scores based on factor ratings"""
    # Get all factors for this assessment
    factors = g.db_session.query(Factor).filter_by(assessment_id=assessment.id).all()
    
    # Get factor definitions for names
    factor_defs = {fd.factor_id: fd for fd in g.db_session.query(FactorDefinition).all()}
    
    # Calculate scores for each category
    category_scores = {}
    category_counts = {}
    total_score = 0
    factor_count = 0
    
    for factor in factors:
        if factor.likelihood is None or factor.impact is None:
            continue
        
        score = factor.likelihood * factor.impact
        category = factor.category
        
        if category not in category_scores:
            category_scores[category] = 0
            category_counts[category] = 0
        
        category_scores[category] += score
        category_counts[category] += 1
        total_score += score
        factor_count += 1
    
    # Calculate average scores
    for category in category_scores:
        if category_counts[category] > 0:
            category_scores[category] = round(category_scores[category] / category_counts[category])
    
    # Calculate overall score
    overall_score = round(total_score / factor_count) if factor_count > 0 else 0
    
    # Determine risk level
    if overall_score >= 20:
        risk_level = RiskLevel.CRITICAL
    elif overall_score >= 15:
        risk_level = RiskLevel.HIGH
    elif overall_score >= 8:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW
    
    # Get high risk factors
    high_risk_factors = []
    for factor in factors:
        if factor.likelihood is None or factor.impact is None:
            continue
        
        score = factor.likelihood * factor.impact
        if score >= 15:
            factor_name = factor_defs[factor.factor_id].name if factor.factor_id in factor_defs else factor.factor_id
            high_risk_factors.append({
                "id": factor.factor_id,
                "name": factor_name,
                "category": factor.category,
                "score": score
            })
    
    # Sort high risk factors by score (highest first)
    high_risk_factors.sort(key=lambda x: x["score"], reverse=True)
    
    # Generate recommendations based on risk level
    recommendations = []
    if risk_level == RiskLevel.CRITICAL:
        recommendations = [
            "File a formal motion to recuse/disqualify immediately",
            "Consider motion to stay proceedings pending resolution",
            "Prepare detailed affidavit documenting all prejudice factors",
            "Consult with appellate counsel regarding potential mandamus relief",
            "Implement comprehensive documentation protocol for all interactions"
        ]
    elif risk_level == RiskLevel.HIGH:
        recommendations = [
            "File a motion to recuse/disqualify or for disclosure of potential conflicts",
            "Consider requesting a hearing on prejudice concerns",
            "Develop detailed documentation of all prejudice indicators",
            "Implement strategic adjustments to case presentation",
            "Prepare record for potential appeal on prejudice grounds"
        ]
    elif risk_level == RiskLevel.MEDIUM:
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
        "recommendations": recommendations
    }

@results_bp.route('/assessments/<assessment_id>/calculate', methods=['POST'])
@require_api_key
def calculate_results(assessment_id):
    """Calculate risk scores based on current factor ratings"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Check if factors exist
        factors = g.db_session.query(Factor).filter_by(assessment_id=assessment.id).all()
        if not factors:
            raise BadRequest("No factor ratings found for this assessment")
        
        # Calculate risk scores
        timestamp = datetime.datetime.utcnow()
        calculation = calculate_risk_score(assessment)
        
        # Create result record
        result = Result(
            assessment_id=assessment.id,
            overall_score=calculation["overall_score"],
            risk_level=calculation["risk_level"],
            category_scores=json.dumps(calculation["category_scores"]),
            high_risk_factors=json.dumps(calculation["high_risk_factors"]),
            recommendations=json.dumps(calculation["recommendations"]),
            calculated_at=timestamp
        )
        
        # Check if risk level has changed
        previous_result = assessment.latest_result
        risk_level_changed = False
        previous_level = None
        previous_score = None
        
        if previous_result:
            previous_level = previous_result.risk_level
            previous_score = previous_result.overall_score
            risk_level_changed = previous_result.risk_level != calculation["risk_level"]
        
        # Save result
        g.db_session.add(result)
        
        # Update assessment status
        assessment.status = "calculated"
        assessment.updated_at = timestamp
        
        g.db_session.commit()
        
        # Prepare response
        response_data = {
            "assessment_id": assessment_id,
            "overall_score": calculation["overall_score"],
            "risk_level": calculation["risk_level"].value,
            "category_scores": calculation["category_scores"],
            "high_risk_factors": calculation["high_risk_factors"],
            "recommendations": calculation["recommendations"],
            "calculated_at": timestamp.isoformat()
        }
        
        # Trigger result.calculated event
        trigger_event('result.calculated', response_data)
        
        # Trigger risk_level.changed event if applicable
        if risk_level_changed:
            # Find factors that changed significantly
            changed_factors = []
            if previous_result:
                # This would require more complex logic to compare factors
                # For now, we'll just note the overall change
                changed_factors = [{
                    "id": "overall",
                    "previous_score": previous_score,
                    "new_score": calculation["overall_score"]
                }]
            
            trigger_event('risk_level.changed', {
                'assessment_id': assessment_id,
                'previous_level': previous_level.value if previous_level else None,
                'new_level': calculation["risk_level"].value,
                'previous_score': previous_score,
                'new_score': calculation["overall_score"],
                'changed_factors': changed_factors,
                'changed_at': timestamp.isoformat()
            })
        
        return jsonify(response_data), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error calculating results: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error calculating results: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@results_bp.route('/assessments/<assessment_id>/results', methods=['GET'])
@require_api_key
def get_results(assessment_id):
    """Get all calculation results for an assessment"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Query results
        results = g.db_session.query(Result).filter_by(assessment_id=assessment.id).order_by(Result.calculated_at.desc()).all()
        
        # Convert to dictionaries
        result_list = [result.to_dict() for result in results]
        
        return jsonify({
            "assessment_id": assessment_id,
            "results": result_list
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception(f"Error retrieving results: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@results_bp.route('/assessments/<assessment_id>/results/latest', methods=['GET'])
@require_api_key
def get_latest_result(assessment_id):
    """Get the latest calculation result for an assessment"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Get latest result
        latest_result = assessment.latest_result
        if not latest_result:
            return jsonify({
                "assessment_id": assessment_id,
                "message": "No calculation results found for this assessment"
            }), 404
        
        return jsonify(latest_result.to_dict()), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception(f"Error retrieving latest result: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@results_bp.route('/assessments/<assessment_id>/export', methods=['GET'])
@require_api_key
def export_results(assessment_id):
    """Export assessment results in various formats"""
    try:
        # Get requested format
        export_format = request.args.get('format', 'json').lower()
        
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Get latest result
        latest_result = assessment.latest_result
        if not latest_result:
            return jsonify({
                "error": "No calculation results found for this assessment"
            }), 404
        
        # Get factors
        factors = g.db_session.query(Factor).filter_by(assessment_id=assessment.id).all()
        
        # Get factor definitions for names
        factor_defs = {fd.factor_id: fd for fd in g.db_session.query(FactorDefinition).all()}
        
        # Prepare export data
        export_data = {
            "assessment": assessment.to_dict(),
            "result": latest_result.to_dict(),
            "factors": [
                {
                    "id": factor.factor_id,
                    "name": factor_defs[factor.factor_id].name if factor.factor_id in factor_defs else factor.factor_id,
                    "category": factor.category,
                    "likelihood": factor.likelihood,
                    "impact": factor.impact,
                    "score": factor.likelihood * factor.impact if factor.likelihood and factor.impact else None,
                    "notes": factor.notes
                }
                for factor in factors
            ],
            "export_date": datetime.datetime.utcnow().isoformat()
        }
        
        # Return based on requested format
        if export_format == 'json':
            return jsonify(export_data), 200
        elif export_format == 'pdf':
            # In a real implementation, this would generate a PDF
            return jsonify({
                "error": "PDF export not implemented in this version",
                "message": "Please use JSON format for now"
            }), 501
        elif export_format == 'csv':
            # In a real implementation, this would generate CSV files
            return jsonify({
                "error": "CSV export not implemented in this version",
                "message": "Please use JSON format for now"
            }), 501
        else:
            return jsonify({
                "error": "Unsupported export format",
                "message": "Supported formats: json, pdf, csv"
            }), 400
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception(f"Error exporting results: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500