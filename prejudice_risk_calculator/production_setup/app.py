"""
Legal Prejudice Risk Calculator API Server
Main application file
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.exceptions import HTTPException
import logging
import uuid

from config import config
from models import Base, Assessment, Factor, Result, CMSLink, APIKey, Webhook, WebhookDelivery, FactorDefinition, RiskLevel

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Create and configure the Flask application"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[app.config['RATELIMIT_DEFAULT']],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # Initialize database
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    session_factory = sessionmaker(bind=engine)
    db_session = scoped_session(session_factory)
    
    # Initialize app-specific configuration
    if config_name == 'production':
        config[config_name].init_app(app)
    
    # Register error handlers
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle HTTP exceptions"""
        response = jsonify({
            'error': error.name,
            'message': error.description,
            'status_code': error.code
        })
        response.status_code = error.code
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle general exceptions"""
        logger.exception("Unhandled exception: %s", str(error))
        response = jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        })
        response.status_code = 500
        return response
    
    # Register middleware
    @app.before_request
    def before_request():
        """Execute before each request"""
        # Generate request ID for tracking
        request.request_id = str(uuid.uuid4())
        
        # Log request
        logger.info(
            "Request %s: %s %s",
            request.request_id,
            request.method,
            request.path
        )
    
    @app.after_request
    def after_request(response):
        """Execute after each request"""
        # Add request ID to response headers
        response.headers['X-Request-ID'] = request.request_id
        
        # Log response
        logger.info(
            "Response %s: %s %s - %s",
            request.request_id,
            request.method,
            request.path,
            response.status_code
        )
        
        return response
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Remove database session at the end of the request"""
        db_session.remove()
    
    # Import and register blueprints
    from routes.assessments import assessments_bp
    from routes.factors import factors_bp
    from routes.results import results_bp
    from routes.cms import cms_bp
    from routes.webhooks import webhooks_bp
    from routes.auth import auth_bp
    
    app.register_blueprint(assessments_bp, url_prefix=f"{app.config['API_PREFIX']}/assessments")
    app.register_blueprint(factors_bp, url_prefix=f"{app.config['API_PREFIX']}/factors")
    app.register_blueprint(results_bp, url_prefix=f"{app.config['API_PREFIX']}/results")
    app.register_blueprint(cms_bp, url_prefix=f"{app.config['API_PREFIX']}/cms")
    app.register_blueprint(webhooks_bp, url_prefix=f"{app.config['API_PREFIX']}/webhooks")
    app.register_blueprint(auth_bp, url_prefix=f"{app.config['API_PREFIX']}/auth")
    
    # Root route
    @app.route('/')
    def index():
        """API root endpoint"""
        return jsonify({
            'name': app.config['APP_NAME'],
            'version': app.config['API_VERSION'],
            'status': 'operational',
            'documentation': f"{request.url_root}{app.config['API_PREFIX']}/docs"
        })
    
    # Health check route
    @app.route('/health')
    @limiter.exempt
    def health():
        """Health check endpoint"""
        # Check database connection
        try:
            db_session.execute("SELECT 1")
            db_status = "connected"
        except Exception as e:
            logger.error("Database health check failed: %s", str(e))
            db_status = "disconnected"
        
        status = "healthy" if db_status == "connected" else "unhealthy"
        status_code = 200 if status == "healthy" else 503
        
        response = jsonify({
            'status': status,
            'database': db_status,
            'timestamp': datetime.datetime.utcnow().isoformat()
        })
        response.status_code = status_code
        return response
    
    # API documentation route
    @app.route(f"{app.config['API_PREFIX']}/docs")
    def api_docs():
        """API documentation endpoint"""
        return jsonify({
            'message': 'API documentation will be available here',
            'openapi_url': f"{request.url_root}{app.config['API_PREFIX']}/openapi.json"
        })
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))