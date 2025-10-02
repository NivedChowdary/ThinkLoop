from database import SessionLocal
from job_service import create_job_from_requirements, get_user_jobs
from user_service import get_user_by_email

def test_jamie_with_database():
    db = SessionLocal()
    
    # Get the test user we created earlier
    user = get_user_by_email(db, "test@thinkloop.com")
    
    if not user:
        print("User not found. Run test_users.py first.")
        return
    
    print(f"Creating job for user: {user.email}\n")
    
    # Create job using Jamie
    requirements = "Senior DevOps engineer, Kubernetes expert, AWS, remote, $140-160k"
    
    print("Jamie is creating the job description...")
    job = create_job_from_requirements(db, user.id, requirements)
    
    print(f"\nJob created and saved to database!")
    print(f"Job ID: {job.id}")
    print(f"Title: {job.title}")
    print(f"Status: {job.status}")
    print(f"Created: {job.created_at}")
    
    print("\n" + "="*60)
    print("FULL JOB DESCRIPTION:")
    print("="*60)
    print(job.job_description)
    print("="*60)
    
    # Fetch all jobs for this user
    print(f"\nAll jobs for {user.email}:")
    all_jobs = get_user_jobs(db, user.id)
    for j in all_jobs:
        print(f"- {j.title} ({j.status}) - {j.created_at}")
    
    db.close()
    print("\nJamie + Database integration working!")

if __name__ == "__main__":
    test_jamie_with_database()