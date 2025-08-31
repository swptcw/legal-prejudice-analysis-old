"""
Configuration settings for the Legal Prejudice Risk Calculator API Server
"""

import os
from datetime import timedelta

# Load environment variables from .env file if present
from dotenv import load_dotenv
load_dotenv()

class Config:
    """Base configuration class"""
    # Application settings
    APP_NAME = "Legal Prejudice Risk Calculator API"
    API_VERSION = "v1"
    API_PREFIX = f"/api/{API_VERSION}"
    
    # Security settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-key-please-change-in-production"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS settings
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging settings
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = os.environ.get("REDIS_URL", "memory://")
    
    # Webhook settings
    WEBHOOK_RETRY_ATTEMPTS = 6
    WEBHOOK_RETRY_DELAYS = [60, 300, 900, 1800, 3600, 10800]  # in seconds
    
    # Feature flags
    ENABLE_WEBHOOKS = os.environ.get("ENABLE_WEBHOOKS", "true").lower() == "true"
    ENABLE_METRICS = os.environ.get("ENABLE_METRICS", "true").lower() == "true"
    
    # Monitoring
    SENTRY_DSN = os.environ.get("SENTRY_DSN", None)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///dev.db"
    
    # Override rate limiting for development
    RATELIMIT_DEFAULT = "1000 per minute"
    
    # Disable certain security features in development
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False
    
    # Use faster hashing for tests
    BCRYPT_LOG_ROUNDS = 4
    
    # Disable webhooks in tests by default
    ENABLE_WEBHOOKS = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Ensure these are set in production
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    
    # Stricter security settings
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")
    
    # Enable SSL if not behind proxy
    SSL_REDIRECT = os.environ.get("SSL_REDIRECT", "false").lower() == "true"
    
    # Production logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARNING")
    
    # Production rate limiting
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "100 per minute")
    
    @classmethod
    def init_app(cls, app):
        """Initialize production application"""
        # Log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Enable ProxyFix if behind proxy
        if os.environ.get("BEHIND_PROXY", "false").lower() == "true":
            from werkzeug.middleware.proxy_fix import ProxyFix
            app.wsgi_app = ProxyFix(
                app.wsgi_app, 
                x_for=int(os.environ.get("PROXY_X_FOR", 1)),
                x_proto=int(os.environ.get("PROXY_X_PROTO", 1)),
                x_host=int(os.environ.get("PROXY_X_HOST", 0)),
                x_port=int(os.environ.get("PROXY_X_PORT", 0)),
                x_prefix=int(os.environ.get("PROXY_X_PREFIX", 0))
            )
        
        # Enable Sentry if configured
        if cls.SENTRY_DSN:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=cls.SENTRY_DSN,
                integrations=[FlaskIntegration()],
                traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", 0.1)),
                environment=os.environ.get("ENVIRONMENT", "production")
            )


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}