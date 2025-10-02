from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """User accounts - recruiters using ThinkLoop"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    company_name = Column(String)
    plan = Column(String, default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"


class Job(Base):
    """Job postings created by users"""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    title = Column(String, nullable=False)
    job_description = Column(Text, nullable=False)
    requirements = Column(Text)
    status = Column(String, default="draft")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="jobs")
    candidates = relationship("Candidate", back_populates="job")
    postings = relationship("JobPosting", back_populates="job")
    
    def __repr__(self):
        return f"<Job {self.title}>"


class Candidate(Base):
    """Candidates who applied for jobs"""
    __tablename__ = "candidates"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    
    resume_text = Column(Text, nullable=False)
    resume_file_url = Column(String)
    
    score = Column(Integer, default=0)
    analysis = Column(Text)
    recommendation = Column(String)
    
    status = Column(String, default="new")
    
    applied_at = Column(DateTime, default=datetime.utcnow)
    screened_at = Column(DateTime)
    
    job = relationship("Job", back_populates="candidates")
    interviews = relationship("Interview", back_populates="candidate")


class Interview(Base):
    """AI interviews"""
    __tablename__ = "interviews"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    candidate_id = Column(String, ForeignKey("candidates.id"), nullable=False)
    
    status = Column(String, default="scheduled")
    questions = Column(JSON)
    responses = Column(JSON)
    transcript = Column(Text)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    candidate = relationship("Candidate", back_populates="interviews")


class JobPosting(Base):
    """Job board postings"""
    __tablename__ = "job_postings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    
    board = Column(String, nullable=False)
    job_url = Column(String)
    
    views = Column(Integer, default=0)
    applications = Column(Integer, default=0)
    
    posted_at = Column(DateTime, default=datetime.utcnow)
    
    job = relationship("Job", back_populates="postings")


class AuditLog(Base):
    """Compliance tracking"""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    
    action = Column(String, nullable=False)
    entity_type = Column(String)
    entity_id = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)


def init_database(engine):
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")