from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("sqlite:///reclaim.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class CaseState(Enum):
    DETECTED = "DETECTED"
    DIAGNOSING = "DIAGNOSING"
    ESCALATED = "ESCALATED"

class FailureCategory(Enum):
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    UNKNOWN = "UNKNOWN"

class RecoveryCase(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, default=CaseState.DETECTED.value)
    category = Column(String, nullable=True)
    amount_paise = Column(Integer)

class DecisionRecord(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    actor = Column(String) # e.g., "compliance_guard" or "policy"
    allowed = Column(Boolean)
    reason = Column(String)
    
    # This links the record back to the specific case
    case = relationship("RecoveryCase", backref="decisions")

Base.metadata.create_all(bind=engine)