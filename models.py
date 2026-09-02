from enum import Enum
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

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

Base.metadata.create_all(bind=engine)