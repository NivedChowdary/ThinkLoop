import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

class JamieAgent:
    """
    Jamie - The Intake Specialist
    Helps create job descriptions from user requirements
    """
    
    def __init__(self):
        self.name = "Jamie"
        self.role = "Intake Specialist"
        
    def create_job_description(self, user_input):
        """
        Takes user input and generates a professional JD
        
        Args:
            user_input: What the recruiter wants (e.g., "Python dev, fintech, remote, $100k")
        
        Returns:
            A formatted job description
        """
        
        prompt = f"""You are Jamie, the Intake Specialist for ThinkLoop.

The recruiter just said: "{user_input}"

Your task: Create a professional, detailed job description based on their input.

Format the JD with these sections:
- **Job Title**
- **Role Summary** (2-3 sentences)
- **Key Responsibilities** (bullet points)
- **Required Qualifications** (bullet points)
- **Nice to Have** (bullet points)
- **Compensation & Benefits** (if mentioned)
- **Work Location** (if mentioned)

Make it professional but engaging. Fill in reasonable defaults if information is missing.

Output ONLY the job description, no meta-commentary."""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def refine_job_description(self, original_jd, feedback):
        """
        Takes an existing JD and user feedback, returns improved version
        """
        
        prompt = f"""You are Jamie, the Intake Specialist for ThinkLoop.

Here's the current job description:
{original_jd}

The recruiter's feedback: "{feedback}"

Update the job description based on their feedback. Keep the same format.

Output ONLY the updated job description."""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text


# Test function
if __name__ == "__main__":
    jamie = JamieAgent()
    
    print("🤖 Testing Jamie's JD Creation...")
    print("="*60)
    
    # Test 1: Create JD from scratch
    user_request = "I need a senior Python developer with Django experience, fintech background, remote work, salary $120-150k"
    
    print(f"\n📝 USER REQUEST: {user_request}\n")
    
    jd = jamie.create_job_description(user_request)
    
    print("🎉 JAMIE CREATED THIS JD:")
    print("="*60)
    print(jd)
    print("="*60)
    
    # Test 2: Refine JD
    print("\n\n🔧 Now testing refinement...")
    feedback = "Add more emphasis on AWS and microservices experience"
    
    print(f"\n📝 FEEDBACK: {feedback}\n")
    
    refined_jd = jamie.refine_job_description(jd, feedback)
    
    print("🎉 JAMIE REFINED THE JD:")
    print("="*60)
    print(refined_jd)
    print("="*60)

#------ Morgan -------

class MorganAgent:
    """
    Morgan - The Resume Hunter
    Scores and ranks candidates based on JD requirements
    """
    
    def __init__(self):
        self.name = "Morgan"
        self.role = "Resume Hunter"
    
    def score_resume(self, resume_text, job_description):
        """
        Scores a resume against a job description
        
        Args:
            resume_text: The candidate's resume as text
            job_description: The JD requirements
        
        Returns:
            Dictionary with score, analysis, and recommendation
        """
        
        prompt = f"""You are Morgan, the Resume Hunter for ThinkLoop.

Your task: Analyze this resume against the job requirements and provide a detailed scoring.

JOB DESCRIPTION:
{job_description}

CANDIDATE RESUME:
{resume_text}

Provide your analysis in this EXACT format:

SCORE: [0-100 number only]

MATCH ANALYSIS:
- Skills Match: [percentage and explanation]
- Experience Match: [years and relevance]
- Domain Match: [how well they fit the industry]
- Education Match: [relevant degrees/certifications]

STRENGTHS:
- [3-5 bullet points of what's strong]

WEAKNESSES/GAPS:
- [3-5 bullet points of what's missing or weak]

RED FLAGS:
- [Any concerns like job hopping, gaps, inconsistencies, or "NONE" if clean]

RECOMMENDATION:
[One of: STRONG MATCH - interview immediately | GOOD MATCH - consider for interview | WEAK MATCH - maybe as backup | REJECT - does not meet requirements]

RECRUITER NOTE:
[1-2 sentences summarizing your take]

Be honest and specific. Score rigorously - only exceptional candidates should score 90+."""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = message.content[0].text
        
        # Extract score from response
        score_line = [line for line in analysis.split('\n') if line.startswith('SCORE:')]
        score = int(score_line[0].replace('SCORE:', '').strip()) if score_line else 0
        
        return {
            'score': score,
            'analysis': analysis,
            'candidate_id': 'C-' + str(hash(resume_text))[:6]  # Simple ID generation
        }
    
    def batch_score_resumes(self, resumes_list, job_description):
        """
        Score multiple resumes and return ranked list
        
        Args:
            resumes_list: List of resume texts
            job_description: The JD to match against
        
        Returns:
            List of scored candidates, sorted by score (highest first)
        """
        
        print(f"\n🔍 Morgan is analyzing {len(resumes_list)} candidates...\n")
        
        scored_candidates = []
        
        for idx, resume in enumerate(resumes_list, 1):
            print(f"📄 Scoring candidate {idx}/{len(resumes_list)}...")
            result = self.score_resume(resume, job_description)
            result['resume_text'] = resume
            scored_candidates.append(result)
        
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n✅ Analysis complete! Candidates ranked.\n")
        
        return scored_candidates


# Test Morgan
if __name__ == "__main__":
    
    # First test Jamie
    print("="*60)
    print("TESTING JAMIE...")
    print("="*60)
    
    jamie = JamieAgent()
    jd = jamie.create_job_description("Senior Python developer, Django, fintech, remote, $120-150k")
    print(jd)
    
    # Now test Morgan
    print("\n\n" + "="*60)
    print("TESTING MORGAN...")
    print("="*60)
    
    morgan = MorganAgent()
    
    # Sample resume 1 - STRONG match
    resume1 = """
    JOHN SMITH
    Senior Python Developer
    john.smith@email.com | (555) 123-4567
    
    EXPERIENCE:
    Senior Python Developer - JPMorgan Chase (2020-2025)
    - Built Django-based trading platforms handling $10B+ daily transactions
    - Led microservices migration to AWS (EC2, Lambda, RDS)
    - Implemented real-time fraud detection using Python and Redis
    - Mentored team of 5 junior developers
    
    Python Developer - Goldman Sachs (2017-2020)
    - Developed Django APIs for investment banking applications
    - Optimized PostgreSQL queries, reducing load times by 70%
    - Built automated testing framework with pytest
    
    SKILLS:
    - Python (8 years), Django (6 years), FastAPI (2 years)
    - AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes
    - PostgreSQL, Redis, Celery
    - REST APIs, Microservices
    
    EDUCATION:
    BS Computer Science - MIT (2017)
    AWS Solutions Architect Certified
    """
    
    # Sample resume 2 - MEDIUM match
    resume2 = """
    SARAH JONES
    Python Developer
    sarah.j@email.com | (555) 987-6543
    
    EXPERIENCE:
    Python Developer - Tech Startup (2022-2025)
    - Built Flask web applications for e-commerce platform
    - Created REST APIs and integrated payment systems (Stripe)
    - Worked with MySQL databases
    
    Junior Developer - Retail Corp (2020-2022)
    - Wrote Python scripts for data processing
    - Basic Django experience on internal tools
    
    SKILLS:
    - Python (4 years), Flask (3 years), Django (1 year)
    - MySQL, basic AWS (S3, EC2)
    - Git, Jenkins
    
    EDUCATION:
    BS Computer Science - State University (2020)
    """
    
    # Sample resume 3 - WEAK match
    resume3 = """
    MIKE JOHNSON
    Full Stack Developer
    mike@email.com
    
    EXPERIENCE:
    Full Stack Developer - Agency (2023-2025)
    - Built websites using React and Node.js
    - Some Python scripting for automation
    - Worked with MongoDB
    
    SKILLS:
    - JavaScript (4 years), React, Node.js
    - Python (1 year - basic)
    - MongoDB, Express
    
    EDUCATION:
    Bootcamp Graduate - Coding Academy (2023)
    """
    
    # Score all resumes
    resumes = [resume1, resume2, resume3]
    results = morgan.batch_score_resumes(resumes, jd)
    
    # Display ranked results
    print("\n" + "="*60)
    print("🏆 RANKED CANDIDATES:")
    print("="*60)
    
    for idx, candidate in enumerate(results, 1):
        print(f"\n#{idx} - Score: {candidate['score']}/100")
        print("-" * 60)
        print(candidate['analysis'])
        print("="*60)


#------- Riley ----------
class RileyAgent:
    """
    Riley - Job Distribution Manager
    Posts jobs to multiple boards and tracks performance
    """
    
    def __init__(self):
        self.name = "Riley"
        self.role = "Job Distribution Manager"
        # Simulated job board data (in production, these would be real APIs)
        self.job_boards = {
            'LinkedIn': {'base_reach': 5000, 'cost': 0, 'speed': 'fast'},
            'Dice': {'base_reach': 2000, 'cost': 0, 'speed': 'medium'},
            'Monster': {'base_reach': 1500, 'cost': 0, 'speed': 'medium'},
            'Indeed': {'base_reach': 8000, 'cost': 0, 'speed': 'fast'},
            'GitHub Jobs': {'base_reach': 1000, 'cost': 0, 'speed': 'slow'},
            'Stack Overflow': {'base_reach': 3000, 'cost': 0, 'speed': 'medium'}
        }
    
    def analyze_job_for_boards(self, job_description):
        """
        Analyzes JD and recommends best job boards
        """
        
        prompt = f"""You are Riley, the Job Distribution Manager for ThinkLoop.

Analyze this job description and recommend the best job boards to post to:

JOB DESCRIPTION:
{job_description}

Available job boards:
- LinkedIn (tech professionals, 5000 avg reach)
- Dice (IT/tech jobs, 2000 avg reach)
- Monster (general jobs, 1500 avg reach)
- Indeed (all industries, 8000 avg reach)
- GitHub Jobs (developers, 1000 avg reach)
- Stack Overflow (developers, 3000 avg reach)

Provide recommendations in this format:

TOP RECOMMENDATIONS:
1. [Board name] - [Why it's best for this role]
2. [Board name] - [Why it's best for this role]
3. [Board name] - [Why it's best for this role]

SKIP THESE:
- [Board name] - [Why not a good fit]

POSTING STRATEGY:
[1-2 sentences on best approach - timing, budget, etc.]

Be specific and strategic."""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def post_job(self, job_title, job_description, selected_boards=None):
        """
        Posts job to selected boards (simulated)
        """
        
        import random
        import time
        
        if selected_boards is None:
            # Default to top boards
            selected_boards = ['LinkedIn', 'Indeed', 'Dice', 'Stack Overflow']
        
        print(f"\n📤 Riley is posting '{job_title}' to job boards...\n")
        
        results = []
        
        for board in selected_boards:
            if board not in self.job_boards:
                print(f"⚠️  {board} not available, skipping...")
                continue
            
            print(f"📌 Posting to {board}...", end='')
            time.sleep(0.5)  # Simulate API call
            
            board_info = self.job_boards[board]
            
            # Simulate posting success with some randomness
            success = random.random() > 0.05  # 95% success rate
            
            if success:
                # Simulate initial views (random but realistic)
                initial_views = random.randint(5, 30)
                
                result = {
                    'board': board,
                    'status': 'posted',
                    'job_url': f"https://{board.lower().replace(' ', '')}.com/jobs/{random.randint(100000, 999999)}",
                    'views': initial_views,
                    'applications': 0,
                    'estimated_reach': board_info['base_reach'],
                    'posted_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                print(f" ✅ Posted! ({initial_views} views in first 5 min)")
                results.append(result)
            else:
                print(f" ❌ Failed to post")
                results.append({
                    'board': board,
                    'status': 'failed',
                    'error': 'API timeout'
                })
        
        print(f"\n✅ Posted to {len([r for r in results if r['status'] == 'posted'])}/{len(selected_boards)} boards successfully!\n")
        
        return results
    
    def generate_performance_report(self, posting_results):
        """
        Generates a performance summary with insights
        """
        
        # Calculate totals
        total_views = sum(r.get('views', 0) for r in posting_results if r['status'] == 'posted')
        total_applications = sum(r.get('applications', 0) for r in posting_results if r['status'] == 'posted')
        successful_posts = len([r for r in posting_results if r['status'] == 'posted'])
        
        # Create summary text for Claude to analyze
        summary = f"""
Posted to {successful_posts} job boards.

Results:
"""
        for result in posting_results:
            if result['status'] == 'posted':
                summary += f"- {result['board']}: {result['views']} views, {result['applications']} applications\n"
        
        prompt = f"""You are Riley, the Job Distribution Manager for ThinkLoop.

Here's the posting performance so far:

{summary}

Provide a brief, energetic performance summary with:
1. Quick stats overview
2. Which board is performing best so far
3. One actionable recommendation

Keep it short and upbeat - you're excited about the results!"""

        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def simulate_performance_update(self, posting_results, hours_elapsed=2):
        """
        Simulates performance after some time has passed
        """
        import random
        
        print(f"\n⏰ Performance Update ({hours_elapsed} hours after posting):\n")
        print("="*60)
        
        for result in posting_results:
            if result['status'] == 'posted':
                # Simulate growth
                new_views = random.randint(20, 100) * hours_elapsed
                new_applications = random.randint(0, 5) * hours_elapsed
                
                result['views'] += new_views
                result['applications'] += new_applications
                
                print(f"📊 {result['board']}:")
                print(f"   Views: {result['views']} (+{new_views})")
                print(f"   Applications: {result['applications']} (+{new_applications})")
                print(f"   Conversion: {(result['applications']/result['views']*100):.1f}%")
                print()
        
        print("="*60)
        
        return posting_results


# Test Riley
if __name__ == "__main__":
    
    print("="*60)
    print("TESTING RILEY - JOB DISTRIBUTION AGENT")
    print("="*60)
    
    # First, create a JD with Jamie
    print("\n📝 Step 1: Jamie creates the JD...\n")
    jamie = JamieAgent()
    jd = jamie.create_job_description("Senior DevOps Engineer, AWS, Kubernetes, $130-160k, remote")
    print(jd[:300] + "...\n")  # Print first 300 chars
    
    # Ask Riley to analyze best boards
    print("\n🤔 Step 2: Riley analyzes which job boards to use...\n")
    riley = RileyAgent()
    recommendations = riley.analyze_job_for_boards(jd)
    print(recommendations)
    
    # Post to recommended boards
    print("\n" + "="*60)
    print("📤 Step 3: Riley posts the job...")
    print("="*60)
    
    posting_results = riley.post_job(
        job_title="Senior DevOps Engineer",
        job_description=jd,
        selected_boards=['LinkedIn', 'Indeed', 'Stack Overflow', 'Dice']
    )
    
    # Show immediate performance
    print("\n📊 Immediate Performance Summary:")
    print("="*60)
    performance = riley.generate_performance_report(posting_results)
    print(performance)
    
    # Simulate 2 hours passing
    print("\n\n" + "="*60)
    print("⏰ SIMULATING 2 HOURS LATER...")
    print("="*60)
    
    updated_results = riley.simulate_performance_update(posting_results, hours_elapsed=2)
    
    # Final report
    print("\n📊 Updated Performance Report:")
    print("="*60)
    final_report = riley.generate_performance_report(updated_results)
    print(final_report)
    
    print("\n" + "="*60)
    print("✅ RILEY TEST COMPLETE!")
    print("="*60)