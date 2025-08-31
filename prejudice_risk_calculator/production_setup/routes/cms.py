"""
Routes for CMS integration
"""

import datetime
from flask import Blueprint, jsonify, request, current_app, g
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound, BadRequest
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from models import Assessment, CMSLink
from utils.auth import require_api_key
from utils.validation import validate_cms_link_data
from utils.events import trigger_event

# Create blueprint
cms_bp = Blueprint('cms', __name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

@cms_bp.route('/assessments/<assessment_id>/link', methods=['POST'])
@require_api_key
def link_to_case(assessment_id):
    """Link assessment to a case in external case management system"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Validate request data
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")
        
        errors = validate_cms_link_data(data)
        if errors:
            return jsonify({"errors": errors}), 400
        
        timestamp = datetime.datetime.utcnow()
        
        # Check if link already exists
        existing_link = g.db_session.query(CMSLink).filter_by(
            assessment_id=assessment.id,
            cms_type=data["cms_type"]
        ).first()
        
        if existing_link:
            # Update existing link
            existing_link.cms_case_id = data["case_id"]
            existing_link.cms_matter_id = data.get("matter_id", "")
            existing_link.sync_data = data.get("sync_data", False)
            existing_link.updated_at = timestamp
            link = existing_link
        else:
            # Create new link
            link = CMSLink(
                assessment_id=assessment.id,
                cms_type=data["cms_type"],
                cms_case_id=data["case_id"],
                cms_matter_id=data.get("matter_id", ""),
                sync_data=data.get("sync_data", False),
                linked_at=timestamp,
                updated_at=timestamp
            )
            g.db_session.add(link)
        
        # Update assessment
        assessment.updated_at = timestamp
        
        # Save changes
        g.db_session.commit()
        
        # Trigger event
        event_type = 'link.created' if not existing_link else 'link.updated'
        trigger_event(event_type, {
            'assessment_id': assessment_id,
            'cms_type': link.cms_type,
            'cms_case_id': link.cms_case_id,
            'cms_matter_id': link.cms_matter_id,
            'sync_data': link.sync_data,
            'timestamp': timestamp.isoformat()
        })
        
        return jsonify({
            "status": "linked" if not existing_link else "updated",
            "cms_type": link.cms_type,
            "case_id": link.cms_case_id,
            "linked_at": link.linked_at.isoformat(),
            "updated_at": link.updated_at.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error linking assessment to case: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error linking assessment to case: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@cms_bp.route('/assessments/<assessment_id>/links', methods=['GET'])
@require_api_key
def get_cms_links(assessment_id):
    """Get all CMS links for an assessment"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Query links
        links = g.db_session.query(CMSLink).filter_by(assessment_id=assessment.id).all()
        
        # Convert to dictionaries
        link_list = [link.to_dict() for link in links]
        
        return jsonify({
            "assessment_id": assessment_id,
            "links": link_list
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        current_app.logger.exception(f"Error retrieving CMS links: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@cms_bp.route('/assessments/<assessment_id>/links/<cms_type>', methods=['DELETE'])
@require_api_key
def delete_cms_link(assessment_id, cms_type):
    """Delete a CMS link"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Query link
        link = g.db_session.query(CMSLink).filter_by(
            assessment_id=assessment.id,
            cms_type=cms_type
        ).first()
        
        if not link:
            raise NotFound(f"No link found for CMS type {cms_type}")
        
        # Delete link
        timestamp = datetime.datetime.utcnow()
        
        # Trigger event before deletion
        trigger_event('link.deleted', {
            'assessment_id': assessment_id,
            'cms_type': link.cms_type,
            'cms_case_id': link.cms_case_id,
            'deleted_at': timestamp.isoformat()
        })
        
        g.db_session.delete(link)
        
        # Update assessment
        assessment.updated_at = timestamp
        
        # Save changes
        g.db_session.commit()
        
        return jsonify({
            "status": "deleted",
            "cms_type": cms_type,
            "deleted_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error deleting CMS link: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error deleting CMS link: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@cms_bp.route('/assessments/<assessment_id>/sync', methods=['POST'])
@require_api_key
def sync_case_data(assessment_id):
    """Sync data between assessment and case management system"""
    try:
        # Query assessment
        assessment = g.db_session.query(Assessment).filter_by(assessment_id=assessment_id).first()
        if not assessment:
            raise NotFound(f"Assessment {assessment_id} not found")
        
        # Query links
        links = g.db_session.query(CMSLink).filter_by(assessment_id=assessment.id).all()
        
        if not links:
            raise BadRequest(f"Assessment {assessment_id} is not linked to any CMS")
        
        # In a real implementation, this would connect to the CMS APIs
        # For now, we'll simulate a successful sync
        timestamp = datetime.datetime.utcnow()
        
        synced_fields = ["case_name", "judge_name", "dates"]
        synced_cms = [link.cms_type for link in links if link.sync_data]
        
        if not synced_cms:
            return jsonify({
                "status": "no_sync",
                "message": "No CMS links are configured for data synchronization"
            }), 200
        
        # Update assessment timestamp
        assessment.updated_at = timestamp
        g.db_session.commit()
        
        return jsonify({
            "status": "synced",
            "synced_fields": synced_fields,
            "synced_cms": synced_cms,
            "synced_at": timestamp.isoformat()
        }), 200
        
    except NotFound as e:
        return jsonify({"error": str(e)}), 404
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        g.db_session.rollback()
        current_app.logger.error(f"Database error syncing case data: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        g.db_session.rollback()
        current_app.logger.exception(f"Error syncing case data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@cms_bp.route('/systems', methods=['GET'])
@require_api_key
def list_cms_systems():
    """List supported case management systems"""
    try:
        # In a real implementation, this would be dynamic or database-driven
        cms_systems = [
            {
                "id": "clio",
                "name": "Clio",
                "description": "Clio is a cloud-based legal practice management software.",
                "features": ["Two-way sync", "Document attachment", "Calendar integration"],
                "documentation_url": "https://api.prejudicerisk.example.com/docs/cms/clio"
            },
            {
                "id": "practice_panther",
                "name": "Practice Panther",
                "description": "Practice Panther is a legal management software for law firms.",
                "features": ["Matter linking", "Contact synchronization", "Billing integration"],
                "documentation_url": "https://api.prejudicerisk.example.com/docs/cms/practice_panther"
            },
            {
                "id": "mycase",
                "name": "MyCase",
                "description": "MyCase is a web-based legal practice management software.",
                "features": ["Document generation", "Task creation", "Client portal integration"],
                "documentation_url": "https://api.prejudicerisk.example.com/docs/cms/mycase"
            },
            {
                "id": "rocket_matter",
                "name": "Rocket Matter",
                "description": "Rocket Matter is a cloud-based legal practice management software.",
                "features": ["Matter linking", "Calendar integration", "Billing codes"],
                "documentation_url": "https://api.prejudicerisk.example.com/docs/cms/rocket_matter"
            }
        ]
        
        return jsonify({
            "cms_systems": cms_systems
        }), 200
        
    except Exception as e:
        current_app.logger.exception(f"Error listing CMS systems: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500