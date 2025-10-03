from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from user_service import create_user, authenticate_user
from job_service import create_job_from_requirements, get_user_jobs
from candidate_service import add_and_score_candidate, get_job_candidates
from auth import create_access_token, verify_token
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from resume_parser import parse_resume_file
from riley_service import post_job_with_riley, get_job_posting_stats

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
    full_name: str = None
    company_name: str = None

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
    candidate_phone: str = None

# Auth dependency
def get_current_user(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    from user_service import get_user_by_email
    user = get_user_by_email(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Routes
@app.get("/")
def root():
    return {"message": "ThinkLoop API is running"}

@app.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    user, error = create_user(db, request.email, request.password, 
                              request.full_name, request.company_name)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    token = create_access_token({"sub": user.email})
    return {"user": {"email": user.email, "id": user.id}, "token": token}

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.email})
    return {"user": {"email": user.email, "id": user.id}, "token": token}

@app.post("/jobs")
def create_job(request: CreateJobRequest, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    job = create_job_from_requirements(db, user.id, request.requirements)
    return {"job": {"id": job.id, "title": job.title, "jd": job.job_description}}

@app.get("/jobs")
def list_jobs(token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    jobs = get_user_jobs(db, user.id)
    return {"jobs": [{"id": j.id, "title": j.title, "status": j.status, 
                      "created_at": str(j.created_at)} for j in jobs]}

@app.post("/candidates")
def add_candidate(request: AddCandidateRequest, token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    candidate, error = add_and_score_candidate(
        db, request.job_id, request.resume_text, 
        request.candidate_name, request.candidate_email, request.candidate_phone
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {"candidate": {
        "id": candidate.id,
        "name": candidate.full_name,
        "score": candidate.score,
        "recommendation": candidate.recommendation
    }}

@app.get("/jobs/{job_id}/candidates")
def list_candidates(job_id: str, token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    candidates = get_job_candidates(db, job_id)
    return {"candidates": [{"id": c.id, "name": c.full_name, "score": c.score,
                           "recommendation": c.recommendation} for c in candidates]}

@app.post("/candidates/upload")
async def upload_candidate_resume(
    job_id: str = Form(...),
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    candidate_phone: str = Form(None),
    resume_file: UploadFile = File(...),
    token: str = Form(...),
    db: Session = Depends(get_db)
):
    get_current_user(token, db)
    
    # Read file
    file_bytes = await resume_file.read()
    
    # Parse resume
    resume_text = parse_resume_file(resume_file.filename, file_bytes)
    
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not parse resume file")
    
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
            "score": candidate.score,
            "recommendation": candidate.recommendation,
            "resume_preview": resume_text[:200] + "..."
        }
    }

@app.post("/jobs/{job_id}/post")
def post_job_to_boards(job_id: str, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
        
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
        
    return {"message": "Job posted successfully", "postings": len(postings)}

@app.get("/jobs/{job_id}/stats")
def get_posting_stats(job_id: str, token: str, db: Session = Depends(get_db)):
    user = get_current_user(token, db)
        
    # Verify job belongs to user
    from models import Job
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    stats = get_job_posting_stats(db, job_id)
    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)