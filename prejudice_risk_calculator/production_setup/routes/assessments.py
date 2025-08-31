"""
Routes for assessment management
"""

import datetime
import uuid
from flask import Blueprint, jsonify, request, current_app, g
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound, BadRequest
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from models import Assessment, Factor, Result
from utils.auth import require_api_key
from utils.validation import validate_assessment_data
from utils.events import trigger_event

# Create blueprint
assessments_bp = Blueprint('assessments', __name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def generate_assessment_id():
    """Generate a unique assessment ID"""
    year = datetime.datetime.now().year
    # Get the count of assessments for this year
    count = g.db_session.query(Assessment).filter(
        Assessment.assessment_id.like(f"PRF-{year}-%")
    ).count() + 1
    return f"PRF-{year}-{count:04d}"

@assessments_bp.route('', methods=['POST'])
@require_api_key
@limiter.limit("60 per minute")
def create_assessment():
    """Create a new prejudice risk assessment"""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        errors = validate_assessment_data(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        # Generate assessment ID
        assessment_id = generate_assessment_id()
        timestamp = datetime.datetime.utcnow()
        
        # Create assessment record
        assessment = Assessment(
            assessment_id=assessment_id,
            case_name=data["case_name"],
            judge_name=data["judge_name"],
            assessor_name=data["assessor_name"],
            assessment_date=datetime.datetime.strptime(data.get("assessment_date", timestamp.strftime("%Y-%m-%d")), "%Y-%m-%d"),
            case_id=data.get("case_id", ""),
            case_management_system_id=data.get("case_management_system_id", ""),
            status="created",
            created_at=timestamp,
            updated_at=timestamp
        )
        
        # Save to database
        g.db_session.add(assessment)
        g.db_session.commit()
        
        # Generate access token (in a real app, this would be a JWT)
        access_token = str(uuid.uuid4())
        
        # Trigger event
        trigger_event('assessment.created', {
            'assessment_id': assessment_id,
            'case_name': assessment.case_name,
            'judge_name': assessment.judge_name,
            'assessor_name': assessment.assessor_name,
            'assessment_date': assessment.assessment_date.isoformat(),
            'case_id': assessment.case_id,
            'case_management_system_id': assessment.case_management_system_id,
            'status': assessment.status
        })
        
        # Return response
        return jsonify({
            "assessment_id": assessment_id,
            "status": "created",
            "created_at": timestamp.isoformat(),
            "access_token": access_token
        }), 201
        
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error creating assessment: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error creating assessment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@assessments_bp.route('/<assessment_id>', methods=['GET'])
@require_api_key
def get_assessment(assessment_id):
    """Retrieve an existing assessment"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Convert to dictionary
        assessment_dict = assessment.to_dict()
        
        # Add factors if available
        factors = g.db_session.query(Factor).filter_by(assessment_id=assessment.id).all()
        if factors:
            factor_list = [factor.to_dict() for factor in factors]
            assessment_dict["factors"] = factor_list
        
        # Add latest result if available
        latest_result = assessment.latest_result
        if latest_result:
            assessment_dict["results"] = latest_result.to_dict()
        
        return jsonify(assessment_dict), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception(f"Error retrieving assessment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@assessments_bp.route('/<assessment_id>', methods=['PUT'])
@require_api_key
def update_assessment(assessment_id):
    """Update an existing assessment"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Get request data
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        # Update assessment fields
        timestamp = datetime.datetime.utcnow()
        updated = False
        
        for field in ["case_name", "judge_name", "assessor_name", "case_id", "case_management_system_id"]:
            if field in data:
                setattr(assessment, field, data[field])
                updated = True
        
        if "assessment_date" in data:
            try:
                assessment.assessment_date = datetime.datetime.strptime(data["assessment_date"], "%Y-%m-%d")
                updated = True
            except ValueError:
                raise BadRequest("Invalid assessment_date format. Use YYYY-MM-DD")
        
        if updated:
            assessment.updated_at = timestamp
            assessment.status = "updated"
            g.db_session.commit()
            
            # Trigger event
            trigger_event('assessment.updated', {
                'assessment_id': assessment_id,
                'case_name': assessment.case_name,
                'judge_name': assessment.judge_name,
                'assessor_name': assessment.assessor_name,
                'assessment_date': assessment.assessment_date.isoformat(),
                'case_id': assessment.case_id,
                'case_management_system_id': assessment.case_management_system_id,
                'status': assessment.status
            })
        
        return jsonify({
            "assessment_id": assessment_id,
            "status": "updated",
            "updated_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error updating assessment: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error updating assessment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@assessments_bp.route('/<assessment_id>', methods=['DELETE'])
@require_api_key
def delete_assessment(assessment_id):
    """Delete an assessment"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Delete assessment
        timestamp = datetime.datetime.utcnow()
        
        # Trigger event before deletion
        trigger_event('assessment.deleted', {
            'assessment_id': assessment_id,
            'deleted_at': timestamp.isoformat()
        })
        
        g.db_session.delete(assessment)
        g.db_session.commit()
        
        return jsonify({
            "status": "deleted",
            "deleted_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error deleting assessment: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error deleting assessment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@assessments_bp.route('', methods=['GET'])
@require_api_key
@limiter.limit("30 per minute")
def list_assessments():
    """List assessments with filtering options"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)  # Limit to 100 items per page
        case_name = request.args.get('case_name')
        judge_name = request.args.get('judge_name')
        status = request.args.get('status')
        
        # Build query
        query = g.db_session.query(Assessment)
        
        # Apply filters
        if case_name:
            query = query.filter(Assessment.case_name.ilike(f"%{case_name}%"))
        if judge_name:
            query = query.filter(Assessment.judge_name.ilike(f"%{judge_name}%"))
        if status:
            query = query.filter(Assessment.status == status)
        
        # Count total
        total = query.count()
        
        # Paginate
        query = query.order_by(Assessment.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        
        # Execute query
        assessments = query.all()
        
        # Convert to dictionaries
        assessment_list = [assessment.to_dict() for assessment in assessments]
        
        return jsonify({
            "assessments": assessment_list,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page  # Ceiling division
        }), 200
        
    except ValueError as e:
        return jsonify({"error": "Invalid pagination parameters"}), 400
    except Exception as e:
        current_app.logger.exception(f"Error listing assessments: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500