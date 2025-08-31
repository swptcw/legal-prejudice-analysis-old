"""
Routes for factor management
"""

import datetime
from flask import Blueprint, jsonify, request, current_app, g
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound, BadRequest
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from models import Assessment, Factor, FactorDefinition
from utils.auth import require_api_key
from utils.validation import validate_factor_data
from utils.events import trigger_event

# Create blueprint
factors_bp = Blueprint('factors', __name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

@factors_bp.route('/definitions', methods=['GET'])
@require_api_key
def get_factor_definitions():
    """Get all factor definitions"""
    try:
        # Query factor definitions
        definitions = g.db_session.query(FactorDefinition).all()
        
        # Organize by category
        categories = {}
        for definition in definitions:
            if definition.category not in categories:
                categories[definition.category] = {
                    "name": definition.category,
                    "factors": []
                }
            
            categories[definition.category]["factors"].append(definition.to_dict())
        
        return jsonify(categories), 200
        
    except Exception as e:
        current_app.logger.exception(f"Error retrieving factor definitions: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@factors_bp.route('/assessments/<assessment_id>/factors', methods=['POST'])
@require_api_key
def submit_factor_ratings(assessment_id):
    """Submit ratings for multiple factors"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Validate request data
        data = request.get_json()
        if not data or "factors" not in data or not isinstance(data["factors"], list):
            raise BadRequest("Invalid request format. Expected 'factors' array")
        
        # Process factors
        timestamp = datetime.datetime.utcnow()
        factors_updated = 0
        updated_factors = []
        
        for factor_data in data["factors"]:
            # Validate factor data
            errors = validate_factor_data(factor_data)
            if errors:
                continue
            
            factor_id = factor_data["id"]
            
            # Check if factor definition exists
            factor_def = g.db_session.query(FactorDefinition).filter_by(factor_id=factor_id).first()
            if not factor_def:
                continue
            
            # Check if factor already exists for this assessment
            factor = g.db_session.query(Factor).filter_by(
                assessment_id=assessment.id,
                factor_id=factor_id
            ).first()
            
            if not factor:
                # Create new factor
                factor = Factor(
                    assessment_id=assessment.id,
                    factor_id=factor_id,
                    category=factor_def.category,
                    created_at=timestamp,
                    updated_at=timestamp
                )
                g.db_session.add(factor)
            
            # Update factor data
            if "likelihood" in factor_data:
                factor.likelihood = factor_data["likelihood"]
            
            if "impact" in factor_data:
                factor.impact = factor_data["impact"]
            
            if "notes" in factor_data:
                factor.notes = factor_data["notes"]
            
            factor.updated_at = timestamp
            factors_updated += 1
            
            # Add to updated factors list for event
            updated_factors.append({
                "id": factor_id,
                "name": factor_def.name,
                "category": factor_def.category,
                "likelihood": factor.likelihood,
                "impact": factor.impact,
                "score": factor.likelihood * factor.impact if factor.likelihood and factor.impact else None
            })
        
        # Update assessment status
        if factors_updated > 0:
            assessment.status = "in_progress"
            assessment.updated_at = timestamp
        
        # Save changes
        g.db_session.commit()
        
        # Trigger event
        if factors_updated > 0:
            trigger_event('factor.updated', {
                'assessment_id': assessment_id,
                'factors_updated': updated_factors,
                'updated_at': timestamp.isoformat()
            })
        
        return jsonify({
            "status": "success",
            "factors_updated": factors_updated,
            "updated_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error submitting factor ratings: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error submitting factor ratings: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@factors_bp.route('/assessments/<assessment_id>/factors', methods=['GET'])
@require_api_key
def get_factor_ratings(assessment_id):
    """Retrieve all factor ratings for an assessment"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Query factors
        factors = g.db_session.query(Factor).filter_by(assessment_id=assessment.id).all()
        
        # Get factor definitions for names
        factor_defs = {fd.factor_id: fd for fd in g.db_session.query(FactorDefinition).all()}
        
        # Prepare factor list
        factor_list = []
        for factor in factors:
            factor_dict = factor.to_dict()
            
            # Add factor name from definition
            if factor.factor_id in factor_defs:
                factor_dict["name"] = factor_defs[factor.factor_id].name
            else:
                factor_dict["name"] = factor.factor_id
            
            factor_list.append(factor_dict)
        
        return jsonify({
            "assessment_id": assessment_id,
            "factors": factor_list
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception(f"Error retrieving factor ratings: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@factors_bp.route('/assessments/<assessment_id>/factors/<factor_id>', methods=['PUT'])
@require_api_key
def update_factor(assessment_id, factor_id):
    """Update a specific factor"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Check if factor definition exists
        factor_def = g.db_session.query(FactorDefinition).filter_by(factor_id=factor_id).first()
        if not factor_def:
            raise NotFound(f"Factor definition {factor_id} not found")
        
        # Get request data
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        # Validate factor data
        errors = validate_factor_data(data, require_id=False)
        if errors:
            return jsonify({"errors": errors}), 400
        
        # Query factor
        factor = g.db_session.query(Factor).filter_by(
            assessment_id=assessment.id,
            factor_id=factor_id
        ).first()
        
        timestamp = datetime.datetime.utcnow()
        
        if not factor:
            # Create new factor
            factor = Factor(
                assessment_id=assessment.id,
                factor_id=factor_id,
                category=factor_def.category,
                created_at=timestamp,
                updated_at=timestamp
            )
            g.db_session.add(factor)
        
        # Update factor data
        if "likelihood" in data:
            factor.likelihood = data["likelihood"]
        
        if "impact" in data:
            factor.impact = data["impact"]
        
        if "notes" in data:
            factor.notes = data["notes"]
        
        factor.updated_at = timestamp
        
        # Update assessment status
        assessment.status = "in_progress"
        assessment.updated_at = timestamp
        
        # Save changes
        g.db_session.commit()
        
        # Trigger event
        trigger_event('factor.updated', {
            'assessment_id': assessment_id,
            'factors_updated': [{
                "id": factor_id,
                "name": factor_def.name,
                "category": factor_def.category,
                "likelihood": factor.likelihood,
                "impact": factor.impact,
                "score": factor.likelihood * factor.impact if factor.likelihood and factor.impact else None
            }],
            'updated_at': timestamp.isoformat()
        })
        
        return jsonify({
            "status": "updated",
            "factor_id": factor_id,
            "updated_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error updating factor: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error updating factor: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500