from agents import JamieAgent

def interactive_jamie():
    """
    Interactive demo where you can talk to Jamie
    """
    jamie = JamieAgent()
    
    print("\n" + "="*60)
    print("🎉 WELCOME TO THINKLOOP!")
    print("="*60)
    print("\nJamie (Intake Specialist) is ready to help you!")
    print("Commands:")
    print("  - Type your JD requirements (e.g., 'Python dev, remote, $100k')")
    print("  - Type 'refine: [feedback]' to improve the current JD")
    print("  - Type 'quit' to exit")
    print("="*60 + "\n")
    
    current_jd = None
    
    while True:
        user_input = input("YOU: ").strip()
        
        if user_input.lower() == 'quit':
            print("\n👋 Thanks for using ThinkLoop! See you soon!")
            break
        
        if not user_input:
            continue
        
        # Check if user wants to refine existing JD
        if user_input.lower().startswith('refine:'):
            if current_jd is None:
                print("\nJAMIE: I don't have a JD to refine yet! Please create one first.\n")
                continue
            
            feedback = user_input[7:].strip()  # Remove 'refine:' prefix
            
            print("\nJAMIE: Let me refine that for you...\n")
            current_jd = jamie.refine_job_description(current_jd, feedback)
            
            print("="*60)
            print(current_jd)
            print("="*60 + "\n")
        
        else:
            # Create new JD
            print("\nJAMIE: Got it! Creating your job description...\n")
            current_jd = jamie.create_job_description(user_input)
            
            print("="*60)
            print(current_jd)
            print("="*60 + "\n")

if __name__ == "__main__":
    interactive_jamie()