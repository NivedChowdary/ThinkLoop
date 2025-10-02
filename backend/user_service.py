from sqlalchemy.orm import Session
from models import User
from auth import hash_password, verify_password
import uuid

def create_user(db: Session, email: str, password: str, full_name: str = None, company_name: str = None):
    """Create new user"""
    # Check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return None, "Email already registered"
    
    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        company_name=company_name,
        plan="free"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user, None

def authenticate_user(db: Session, email: str, password: str):
    """Login user"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()