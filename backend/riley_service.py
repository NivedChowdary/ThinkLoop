from sqlalchemy.orm import Session
from models import JobPosting
from agents import RileyAgent
import uuid
from datetime import datetime

riley = RileyAgent()

def post_job_with_riley(db: Session, job_id: str, job_title: str, job_description: str, boards: list = None):
    """Post job using Riley and save posting records"""
    
    if boards is None:
        boards = ['LinkedIn', 'Indeed', 'Dice', 'Stack Overflow']
    
    # Riley posts (simulated for now)
    posting_results = riley.post_job(job_title, job_description, boards)
    
    # Save each posting to database
    saved_postings = []
    for result in posting_results:
        if result['status'] == 'posted':
            posting = JobPosting(
                id=str(uuid.uuid4()),
                job_id=job_id,
                board=result['board'],
                job_url=result['job_url'],
                views=result['views'],
                applications=result['applications'],
                posted_at=datetime.utcnow()
            )
            db.add(posting)
            saved_postings.append(posting)
    
    db.commit()
    return saved_postings

def get_job_posting_stats(db: Session, job_id: str):
    """Get posting performance for a job"""
    postings = db.query(JobPosting).filter(JobPosting.job_id == job_id).all()
    
    total_views = sum(p.views for p in postings)
    total_applications = sum(p.applications for p in postings)
    
    return {
        'postings': [
            {
                'board': p.board,
                'views': p.views,
                'applications': p.applications,
                'url': p.job_url,
                'posted_at': str(p.posted_at)
            }
            for p in postings
        ],
        'total_views': total_views,
        'total_applications': total_applications
    }