from database import SessionLocal
from user_service import create_user, authenticate_user

def test_user_system():
    db = SessionLocal()
    
    print("Testing user registration...")
    
    # Create test user
    user, error = create_user(
        db=db,
        email="test@thinkloop.com",
        password="testpass123",
        full_name="Test User",
        company_name="ThinkLoop Demo"
    )
    
    if error:
        print(f"Error: {error}")
        db.close()
        return
    
    print(f"User created: {user.email}")
    print(f"ID: {user.id}")
    print(f"Plan: {user.plan}")
    
    print("\nTesting authentication...")
    
    # Test login with correct password
    auth_user = authenticate_user(db, "test@thinkloop.com", "testpass123")
    if auth_user:
        print("Login successful!")
    else:
        print("Login failed")
    
    # Test login with wrong password
    auth_user = authenticate_user(db, "test@thinkloop.com", "wrongpass")
    if auth_user:
        print("ERROR: Wrong password worked!")
    else:
        print("Correctly rejected wrong password")
    
    db.close()
    print("\nUser system working!")

if __name__ == "__main__":
    test_user_system()