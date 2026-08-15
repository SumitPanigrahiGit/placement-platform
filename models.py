from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    skills = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(150), nullable=False)
    role_title = Column(String(150), nullable=False)
    required_skills = Column(String, nullable=True)
    source_url = Column(String(300), nullable=True)
    posted_at = Column(DateTime(timezone=True), server_default=func.now())

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    status = Column(String(50), default="applied")
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="applications")
    posting = relationship("JobPosting", backref="applications")