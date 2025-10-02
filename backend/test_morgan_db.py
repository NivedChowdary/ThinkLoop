from database import SessionLocal
from candidate_service import add_and_score_candidate, get_job_candidates
from job_service import get_user_jobs
from user_service import get_user_by_email

def test_morgan_with_database():
    db = SessionLocal()
    
    # Get test user and their job
    user = get_user_by_email(db, "test@thinkloop.com")
    jobs = get_user_jobs(db, user.id)
    
    if not jobs:
        print("No jobs found. Run test_jamie_db.py first.")
        return
    
    job = jobs[0]
    print(f"Scoring candidates for job: {job.title}\n")
    
    # Sample resume
    resume = """
    SARAH JOHNSON
    DevOps Engineer
    sarah.j@email.com | (555) 123-4567
    
    EXPERIENCE:
    Senior DevOps Engineer - Tech Corp (2020-2025)
    - Managed Kubernetes clusters (50+ nodes) on AWS EKS
    - Built CI/CD pipelines with GitHub Actions and ArgoCD
    - Reduced infrastructure costs by 40% through optimization
    - Led migration from EC2 to containerized architecture
    
    DevOps Engineer - Startup Inc (2018-2020)
    - Maintained AWS infrastructure (EC2, S3, RDS)
    - Implemented monitoring with Prometheus and Grafana
    - Automated deployments using Terraform
    
    SKILLS:
    Kubernetes (5 years), AWS (7 years), Docker, Terraform, Python, Bash
    CI/CD, Prometheus, Grafana, Jenkins, ArgoCD
    
    CERTIFICATIONS:
    - AWS Solutions Architect Professional
    - Certified Kubernetes Administrator (CKA)
    """
    
    print("Morgan is scoring the candidate...")
    candidate, error = add_and_score_candidate(
        db=db,
        job_id=job.id,
        resume_text=resume,
        candidate_name="Sarah Johnson",
        candidate_email="sarah.j@email.com",
        candidate_phone="555-123-4567"
    )
    
    if error:
        print(f"Error: {error}")
        return
    
    print(f"\nCandidate scored and saved!")
    print(f"Name: {candidate.full_name}")
    print(f"Score: {candidate.score}/100")
    print(f"Recommendation: {candidate.recommendation}")
    print(f"Status: {candidate.status}")
    
    print("\n" + "="*60)
    print("MORGAN'S FULL ANALYSIS:")
    print("="*60)
    print(candidate.analysis)
    
    # Show all candidates for this job
    print("\n" + "="*60)
    print(f"All candidates for '{job.title}':")
    print("="*60)
    all_candidates = get_job_candidates(db, job.id)
    for c in all_candidates:
        print(f"- {c.full_name}: {c.score}/100 ({c.recommendation})")
    
    db.close()
    print("\nMorgan + Database integration working!")

if __name__ == "__main__":
    test_morgan_with_database()