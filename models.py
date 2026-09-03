from datetime import datetime
from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("sqlite:///reclaim.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class CaseState(str, Enum):
    DETECTED = "DETECTED"
    DIAGNOSING = "DIAGNOSING"
    INTERVENTION_SCHEDULED = "INTERVENTION_SCHEDULED"
    INTERVENTION_SENT = "INTERVENTION_SENT"
    AWAITING_OUTCOME = "AWAITING_OUTCOME"
    RECOVERED = "RECOVERED"
    ESCALATED = "ESCALATED"
    ABANDONED = "ABANDONED"

class FailureCategory(str, Enum):
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"
    AUTH_FAILED = "AUTH_FAILED"
    CARD_EXPIRED = "CARD_EXPIRED"
    MANDATE_REVOKED = "MANDATE_REVOKED"
    UNKNOWN = "UNKNOWN"

class RecoveryCase(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, default="cust_default")
    amount_paise = Column(Integer, nullable=False)
    state = Column(String, default=CaseState.DETECTED.value)
    category = Column(String, default=FailureCategory.UNKNOWN.value)
    error_reason = Column(String, nullable=True)
    
    attempts = Column(Integer, default=0)
    pre_debit_notice_sent = Column(Boolean, default=False)
    pre_debit_notice_time = Column(DateTime, nullable=True)
    last_attempt_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    recovered_at = Column(DateTime, nullable=True)

class DecisionRecord(Base):
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    actor = Column(String)  # e.g., "compliance_guard", "policy", or "engine"
    rule_name = Column(String, nullable=True)
    allowed = Column(Boolean)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("RecoveryCase", backref="decisions")

Base.metadata.create_all(bind=engine)