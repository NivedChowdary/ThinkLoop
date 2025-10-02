from sqlalchemy.orm import Session
from models import Job
from agents import JamieAgent
import uuid

jamie = JamieAgent()

def create_job_from_requirements(db: Session, user_id: str, requirements: str):
    """Create job using Jamie and save to database"""
    
    # Jamie generates JD
    jd = jamie.create_job_description(requirements)
    
    # Extract title (first line of JD usually has title)
    lines = jd.split('\n')
    title = lines[0].replace('#', '').strip() if lines else "Untitled Job"
    
    # Save to database
    job = Job(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        job_description=jd,
        requirements=requirements,
        status="draft"
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return job

def get_user_jobs(db: Session, user_id: str):
    """Get all jobs for a user"""
    return db.query(Job).filter(Job.user_id == user_id).order_by(Job.created_at.desc()).all()

def get_job_by_id(db: Session, job_id: str):
    """Get single job"""
    return db.query(Job).filter(Job.id == job_id).first()