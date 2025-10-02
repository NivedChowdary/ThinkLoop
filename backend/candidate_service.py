from sqlalchemy.orm import Session
from models import Candidate
from agents import MorganAgent
import uuid

morgan = MorganAgent()

def add_and_score_candidate(db: Session, job_id: str, resume_text: str, 
                           candidate_name: str, candidate_email: str, 
                           candidate_phone: str = None):
    """Add candidate and get Morgan's score"""
    
    # Get the job
    from models import Job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None, "Job not found"
    
    # Morgan scores the resume
    result = morgan.score_resume(resume_text, job.job_description)
    
    # Save candidate to database
    candidate = Candidate(
        id=str(uuid.uuid4()),
        job_id=job_id,
        full_name=candidate_name,
        email=candidate_email,
        phone=candidate_phone,
        resume_text=resume_text,
        score=result['score'],
        analysis=result['analysis'],
        recommendation=extract_recommendation(result['analysis']),
        status="screened"
    )
    
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    
    return candidate, None

def extract_recommendation(analysis: str):
    """Extract recommendation from Morgan's analysis"""
    if "STRONG MATCH" in analysis:
        return "STRONG MATCH"
    elif "GOOD MATCH" in analysis:
        return "GOOD MATCH"
    elif "WEAK MATCH" in analysis:
        return "WEAK MATCH"
    else:
        return "REJECT"

def get_job_candidates(db: Session, job_id: str, min_score: int = 0):
    """Get all candidates for a job, sorted by score"""
    return db.query(Candidate)\
        .filter(Candidate.job_id == job_id)\
        .filter(Candidate.score >= min_score)\
        .order_by(Candidate.score.desc())\
        .all()