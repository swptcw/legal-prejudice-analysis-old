"""
Database models for the Legal Prejudice Risk Calculator API
"""

from datetime import datetime
import uuid
import json
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class RiskLevel(enum.Enum):
    """Risk level enumeration"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Assessment(Base):
    """Assessment model"""
    __tablename__ = 'assessments'
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(String(20), unique=True, nullable=False, index=True)
    case_name = Column(String(255), nullable=False)
    judge_name = Column(String(255), nullable=False)
    assessor_name = Column(String(255), nullable=False)
    assessment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    case_id = Column(String(100), nullable=True)
    case_management_system_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default='created')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    factors = relationship("Factor", back_populates="assessment", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="assessment", cascade="all, delete-orphan")
    cms_links = relationship("CMSLink", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment {self.assessment_id}: {self.case_name}>"
    
    @property
    def latest_result(self):
        """Get the latest result for this assessment"""
        if not self.results:
            return None
        return max(self.results, key=lambda r: r.calculated_at)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'assessment_id': self.assessment_id,
            'case_name': self.case_name,
            'judge_name': self.judge_name,
            'assessor_name': self.assessor_name,
            'assessment_date': self.assessment_date.isoformat(),
            'case_id': self.case_id,
            'case_management_system_id': self.case_management_system_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Factor(Base):
    """Factor model for storing factor ratings"""
    __tablename__ = 'factors'
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    factor_id = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    likelihood = Column(Integer, nullable=True)
    impact = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="factors")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('assessment_id', 'factor_id', name='uix_factor_assessment'),
    )
    
    def __repr__(self):
        return f"<Factor {self.factor_id} for Assessment {self.assessment.assessment_id}>"
    
    @property
    def score(self):
        """Calculate factor score"""
        if self.likelihood is None or self.impact is None:
            return None
        return self.likelihood * self.impact
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.factor_id,
            'category': self.category,
            'likelihood': self.likelihood,
            'impact': self.impact,
            'score': self.score,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Result(Base):
    """Result model for storing risk calculation results"""
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    overall_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    category_scores = Column(JSON, nullable=False)
    high_risk_factors = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    calculated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="results")
    
    def __repr__(self):
        return f"<Result for Assessment {self.assessment.assessment_id}: {self.risk_level.value}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'assessment_id': self.assessment.assessment_id,
            'overall_score': self.overall_score,
            'risk_level': self.risk_level.value,
            'category_scores': json.loads(self.category_scores) if isinstance(self.category_scores, str) else self.category_scores,
            'high_risk_factors': json.loads(self.high_risk_factors) if isinstance(self.high_risk_factors, str) else self.high_risk_factors,
            'recommendations': json.loads(self.recommendations) if isinstance(self.recommendations, str) else self.recommendations,
            'calculated_at': self.calculated_at.isoformat()
        }


class CMSLink(Base):
    """CMS Link model for storing connections to case management systems"""
    __tablename__ = 'cms_links'
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False)
    cms_type = Column(String(100), nullable=False)
    cms_case_id = Column(String(100), nullable=False)
    cms_matter_id = Column(String(100), nullable=True)
    sync_data = Column(Boolean, nullable=False, default=False)
    linked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="cms_links")
    
    def __repr__(self):
        return f"<CMSLink {self.cms_type} for Assessment {self.assessment.assessment_id}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'assessment_id': self.assessment.assessment_id,
            'cms_type': self.cms_type,
            'cms_case_id': self.cms_case_id,
            'cms_matter_id': self.cms_matter_id,
            'sync_data': self.sync_data,
            'linked_at': self.linked_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class APIKey(Base):
    """API Key model for authentication"""
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    key_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    key_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<APIKey {self.key_id}: {self.name}>"


class Webhook(Base):
    """Webhook model for storing webhook configurations"""
    __tablename__ = 'webhooks'
    
    id = Column(Integer, primary_key=True)
    webhook_id = Column(String(36), unique=True, nullable=False, default=lambda: f"wh_{str(uuid.uuid4())[:8]}")
    target_url = Column(String(255), nullable=False)
    events = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    secret_hash = Column(String(255), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    content_type = Column(String(100), nullable=False, default='application/json')
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deliveries = relationship("WebhookDelivery", back_populates="webhook", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Webhook {self.webhook_id}: {self.target_url}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'webhook_id': self.webhook_id,
            'target_url': self.target_url,
            'events': json.loads(self.events) if isinstance(self.events, str) else self.events,
            'description': self.description,
            'active': self.active,
            'content_type': self.content_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class WebhookDelivery(Base):
    """Webhook Delivery model for tracking webhook deliveries"""
    __tablename__ = 'webhook_deliveries'
    
    id = Column(Integer, primary_key=True)
    delivery_id = Column(String(36), unique=True, nullable=False, default=lambda: f"dlv_{str(uuid.uuid4())[:8]}")
    webhook_id = Column(Integer, ForeignKey('webhooks.id'), nullable=False)
    event_id = Column(String(36), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(50), nullable=False, default='pending')
    response_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    next_retry_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    
    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries")
    
    def __repr__(self):
        return f"<WebhookDelivery {self.delivery_id}: {self.status}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'delivery_id': self.delivery_id,
            'webhook_id': self.webhook.webhook_id,
            'event_id': self.event_id,
            'event_type': self.event_type,
            'status': self.status,
            'response_code': self.response_code,
            'response_body': self.response_body,
            'error': self.error,
            'retry_count': self.retry_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }


class FactorDefinition(Base):
    """Factor Definition model for storing factor definitions"""
    __tablename__ = 'factor_definitions'
    
    id = Column(Integer, primary_key=True)
    factor_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    guidance = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FactorDefinition {self.factor_id}: {self.name}>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.factor_id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'guidance': self.guidance
        }