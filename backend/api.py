from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from user_service import create_user, authenticate_user, get_user_by_email
from job_service import create_job_from_requirements, get_user_jobs
from candidate_service import add_and_score_candidate, get_job_candidates
from auth import create_access_token, verify_token
from resume_parser import parse_resume_file
from riley_service import post_job_with_riley, get_job_posting_stats
from rate_limiter import signup_limiter, login_limiter, job_limiter, candidate_limiter
from typing import Optional

app = FastAPI(title="ThinkLoop API")

# Create tables on startup
@app.on_event("startup") 
def startup_event():
    from database import engine
    from models import Base
    Base.metadata.create_all(bind=engine)

# CORS - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://think-loop.vercel.app",
        "https://getthinkloop.com",
        "https://www.getthinkloop.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class CreateJobRequest(BaseModel):
    requirements: str

class AddCandidateRequest(BaseModel):
    job_id: str
    resume_text: str
    candidate_name: str
    candidate_email: str
    candidate_phone: Optional[str] = None

# Auth dependency - Fixed to use headers
def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Support both "Bearer token" and just "token" for backward compatibility
    token = authorization.replace('Bearer ', '') if authorization.startswith('Bearer ') else authorization
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = get_user_by_email(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Routes
@app.get("/")
def root():
    return {
        "message": "ThinkLoop API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/signup")
def signup(
    request_data: SignupRequest, 
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(signup_limiter)
):
    try:
        user, error = create_user(db, request_data.email, request_data.password, 
                                  request_data.full_name, request_data.company_name)
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        token = create_access_token({"sub": user.email})
        return {
            "user": {
                "email": user.email, 
                "id": user.id,
                "full_name": user.full_name,
                "company_name": user.company_name
            }, 
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/login")
def login(
    request_data: LoginRequest, 
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(login_limiter)
):
    try:
        user = authenticate_user(db, request_data.email, request_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_access_token({"sub": user.email})
        return {
            "user": {
                "email": user.email, 
                "id": user.id,
                "full_name": user.full_name,
                "company_name": user.company_name
            }, 
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/jobs")
def create_job(
    request_data: CreateJobRequest,
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    _: None = Depends(job_limiter)
):
    try:
        job = create_job_from_requirements(db, user.id, request_data.requirements)
        return {
            "job": {
                "id": job.id, 
                "title": job.title, 
                "jd": job.job_description,
                "status": job.status,
                "created_at": str(job.created_at)
            }
        }
    except Exception as e:
        print(f"Job creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Job creation failed: {str(e)}")

@app.get("/jobs")
def list_jobs(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        jobs = get_user_jobs(db, user.id)
        return {
            "jobs": [
                {
                    "id": j.id, 
                    "title": j.title, 
                    "status": j.status, 
                    "created_at": str(j.created_at)
                } 
                for j in jobs
            ]
        }
    except Exception as e:
        print(f"List jobs error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load jobs: {str(e)}")

@app.get("/jobs/{job_id}")
def get_job_details(
    job_id: str,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    from models import Job
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job": {
            "id": job.id,
            "title": job.title,
            "job_description": job.job_description,
            "requirements": job.requirements,
            "status": job.status,
            "created_at": str(job.created_at)
        }
    }

@app.post("/candidates")
def add_candidate(
    request_data: AddCandidateRequest,
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    _: None = Depends(candidate_limiter)
):
    try:
        # Verify job belongs to user
        from models import Job
        job = db.query(Job).filter(Job.id == request_data.job_id, Job.user_id == user.id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        candidate, error = add_and_score_candidate(
            db, request_data.job_id, request_data.resume_text, 
            request_data.candidate_name, request_data.candidate_email, request_data.candidate_phone
        )
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "candidate": {
                "id": candidate.id,
                "name": candidate.full_name,
                "email": candidate.email,
                "score": candidate.score,
                "recommendation": candidate.recommendation,
                "analysis": candidate.analysis,  # ← ADD THIS
                "status": candidate.status
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Add candidate error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add candidate: {str(e)}")

@app.get("/jobs/{job_id}/candidates")
def list_candidates(
    job_id: str,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        # Verify job belongs to user
        from models import Job
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        candidates = get_job_candidates(db, job_id)
        return {
            "candidates": [
                {
                    "id": c.id, 
                    "name": c.full_name,
                    "email": c.email,
                    "score": c.score,
                    "recommendation": c.recommendation,
                    "status": c.status,
                    "applied_at": str(c.applied_at)
                } 
                for c in candidates
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"List candidates error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load candidates: {str(e)}")

@app.post("/candidates/upload")
async def upload_candidate_resume(
    job_id: str = Form(...),
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    candidate_phone: Optional[str] = Form(None),
    resume_file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    _: None = Depends(candidate_limiter)
):
    try:
        # Verify job belongs to user
        from models import Job
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check file size (max 10MB)
        file_bytes = await resume_file.read()
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Parse resume
        resume_text = parse_resume_file(resume_file.filename, file_bytes)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not parse resume file. Please ensure it's a valid PDF or DOCX.")
        
        # Score with Morgan
        candidate, error = add_and_score_candidate(
            db, job_id, resume_text, 
            candidate_name, candidate_email, candidate_phone
        )
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "candidate": {
                "id": candidate.id,
                "name": candidate.full_name,
                "email": candidate.email,
                "score": candidate.score,
                "recommendation": candidate.recommendation,
                "resume_preview": resume_text[:200] + "..." if len(resume_text) > 200 else resume_text
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/jobs/{job_id}/post")
def post_job_to_boards(
    job_id: str,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        # Get the job
        from models import Job
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Post with Riley
        postings = post_job_with_riley(db, job.id, job.title, job.job_description)
        
        # Update job status
        job.status = "posted"
        db.commit()
        
        return {
            "message": "Job posted successfully by Riley",
            "postings": len(postings),
            "boards": [p.board for p in postings]
        }
    except Exception as e:
        print(f"Post job error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to post job: {str(e)}")

@app.get("/jobs/{job_id}/stats")
def get_posting_stats(
    job_id: str,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    try:
        # Verify job belongs to user
        from models import Job
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        stats = get_job_posting_stats(db, job_id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)