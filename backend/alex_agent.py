"""
Alex - The Interview Coordinator
Conducts AI-powered screening interviews with candidates
"""
import anthropic
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

class AlexAgent:
    """
    Alex - Interview Coordinator
    Conducts structured screening interviews via text or voice
    """
    
    def __init__(self):
        self.name = "Alex"
        self.role = "Interview Coordinator"
    
    def generate_interview_questions(self, job_description, num_questions=10):
        """
        Generate tailored interview questions based on JD
        
        Args:
            job_description: The job requirements
            num_questions: Number of questions to generate (default 10)
        
        Returns:
            List of interview questions with evaluation criteria
        """
        
        prompt = f"""You are Alex, the Interview Coordinator for ThinkLoop.

Generate {num_questions} screening interview questions for this role:

JOB DESCRIPTION:
{job_description}

Create a mix of:
- Technical questions (40%)
- Behavioral questions (30%)
- Situational questions (20%)
- Culture fit questions (10%)

For each question, provide:
1. The question itself
2. What you're looking for in a good answer
3. Red flags to watch for

Format as JSON array:
[
  {{
    "question": "...",
    "type": "technical/behavioral/situational/culture",
    "looking_for": "...",
    "red_flags": "..."
  }},
  ...
]

Make questions specific to the role, not generic."""

        try:
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response
            response_text = message.content[0].text
            
            # Try to parse JSON
            # Claude might wrap it in markdown, so extract it
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            questions = json.loads(json_str)
            return questions
            
        except Exception as e:
            print(f"Evaluating Q{i}...")
        
        eval_result = alex.evaluate_answer(question, answer)
        evaluations.append({
            "question": question['question'],
            "answer": answer,
            "score": eval_result['score'],
            "assessment": eval_result['assessment']
        })
        
        print(f"Score: {eval_result['score']}/10")
        print(f"Assessment: {eval_result['assessment']}")
        print()
    
    print("\n" + "="*60)
    print("📊 Step 4: Alex generates overall summary...")
    print("="*60)
    
    # Calculate overall score
    avg_score = sum(e['score'] for e in evaluations) / len(evaluations)
    overall_score = round(avg_score * 10)
    
    interview_data = {
        "overall_score": overall_score,
        "evaluations": evaluations,
        "recommendation": alex._get_recommendation(avg_score)
    }
    
    summary = alex.generate_interview_summary(interview_data)
    
    print(f"\nOVERALL SCORE: {overall_score}/100")
    print("="*60)
    print(summary)
    print("="*60)
    
    print("\n✅ ALEX TEST COMPLETE!")
    print("\nAlex can now:")
    print("- Generate custom interview questions for any role")
    print("- Evaluate candidate answers in real-time")
    print("- Provide detailed feedback and recommendations")
    print("- Conduct complete screening interviews")
Error generating questions: {e}")
            # Fallback questions
            return [
                {
                    "question": "Tell me about your relevant experience for this role.",
                    "type": "behavioral",
                    "looking_for": "Specific examples, relevant skills, measurable achievements",
                    "red_flags": "Vague answers, lack of specifics, irrelevant experience"
                },
                {
                    "question": "Describe a challenging project you worked on and how you overcame obstacles.",
                    "type": "behavioral",
                    "looking_for": "Problem-solving skills, persistence, learning from failures",
                    "red_flags": "Blaming others, giving up easily, no lessons learned"
                }
            ]
    
    def evaluate_answer(self, question_data, candidate_answer, context=""):
        """
        Evaluate a candidate's answer to an interview question
        
        Args:
            question_data: Dict with question, type, looking_for, red_flags
            candidate_answer: The candidate's response
            context: Previous conversation context (optional)
        
        Returns:
            Evaluation dict with score and feedback
        """
        
        prompt = f"""You are Alex, the Interview Coordinator for ThinkLoop.

You asked: "{question_data['question']}"

What you're looking for: {question_data['looking_for']}
Red flags: {question_data['red_flags']}

Candidate's answer:
"{candidate_answer}"

Evaluate this answer and provide:
1. Score (0-10)
2. Brief assessment
3. Follow-up question (if needed)

Format your response as JSON:
{{
  "score": [0-10],
  "assessment": "...",
  "follow_up": "..." or null
}}

Be fair but rigorous. A score of 7-8 is good, 9-10 is exceptional."""

        try:
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            evaluation = json.loads(json_str)
            return evaluation
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return {
                "score": 5,
                "assessment": "Unable to evaluate answer automatically.",
                "follow_up": None
            }
    
    def conduct_text_interview(self, job_description, candidate_responses):
        """
        Conduct a complete text-based interview
        
        Args:
            job_description: The job requirements
            candidate_responses: List of candidate's answers to questions
        
        Returns:
            Complete interview evaluation
        """
        
        # Generate questions
        questions = self.generate_interview_questions(job_description, num_questions=8)
        
        # Evaluate each response
        evaluations = []
        for i, (question, answer) in enumerate(zip(questions, candidate_responses)):
            eval_result = self.evaluate_answer(question, answer)
            evaluations.append({
                "question": question['question'],
                "answer": answer,
                "score": eval_result['score'],
                "assessment": eval_result['assessment']
            })
        
        # Generate overall summary
        avg_score = sum(e['score'] for e in evaluations) / len(evaluations)
        
        return {
            "overall_score": round(avg_score * 10),  # Scale to 0-100
            "evaluations": evaluations,
            "recommendation": self._get_recommendation(avg_score)
        }
    
    def generate_interview_summary(self, interview_data):
        """
        Generate a human-readable interview summary
        
        Args:
            interview_data: Complete interview evaluation
        
        Returns:
            Formatted summary text
        """
        
        evaluations_text = "\n\n".join([
            f"Q: {e['question']}\nA: {e['answer']}\nScore: {e['score']}/10 - {e['assessment']}"
            for e in interview_data['evaluations']
        ])
        
        prompt = f"""You are Alex, the Interview Coordinator for ThinkLoop.

Here's the complete interview:

{evaluations_text}

Overall Score: {interview_data['overall_score']}/100

Write a concise summary for the recruiter with:
1. Overall impression (2-3 sentences)
2. Key strengths (3-4 bullet points)
3. Areas of concern (2-3 bullet points)
4. Final recommendation (STRONG PASS / PASS / MAYBE / FAIL)

Keep it professional but conversational - you're talking to the recruiter."""

        try:
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"Interview completed with score {interview_data['overall_score']}/100. Recommendation: {interview_data['recommendation']}"
    
    def _get_recommendation(self, avg_score):
        """Convert average score to recommendation"""
        if avg_score >= 8.5:
            return "STRONG PASS - Excellent candidate, move to finals immediately"
        elif avg_score >= 7.0:
            return "PASS - Good candidate, proceed to next round"
        elif avg_score >= 5.5:
            return "MAYBE - Decent candidate, consider as backup"
        else:
            return "FAIL - Does not meet requirements"


# Test Alex
if __name__ == "__main__":
    
    print("="*60)
    print("TESTING ALEX - INTERVIEW AGENT")
    print("="*60)
    
    alex = AlexAgent()
    
    # Sample JD
    jd = """
    Senior Python Developer
    
    We're looking for an experienced Python developer with:
    - 5+ years Python experience
    - Strong Django/Flask skills
    - Experience with AWS
    - RESTful API design
    - Team collaboration skills
    """
    
    print("\n📋 Step 1: Alex generates interview questions...\n")
    questions = alex.generate_interview_questions(jd, num_questions=5)
    
    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q['question']}")
        print(f"    Type: {q['type']}")
        print()
    
    print("\n" + "="*60)
    print("💬 Step 2: Simulating candidate answers...")
    print("="*60)
    
    # Simulate candidate answers
    sample_answers = [
        "I have 6 years of Python experience, primarily working with Django. At my last company, I built a RESTful API that handled 10,000 requests per second. I used Django Rest Framework and optimized database queries to achieve this performance.",
        
        "I've deployed several applications on AWS. I typically use EC2 for compute, RDS for databases, and S3 for static files. I also have experience with Lambda for serverless functions and CloudWatch for monitoring.",
        
        "In my last project, we faced a major performance issue where our API was timing out. I profiled the code, identified the bottleneck was in our database queries, added proper indexing, and implemented caching with Redis. This reduced response time from 5 seconds to 200ms.",
        
        "I believe in clean, maintainable code. I follow PEP 8 standards, write comprehensive tests, and document my code well. I also believe in code reviews and pair programming to maintain quality.",
        
        "I work well in teams. I'm comfortable with Agile methodologies, participate actively in stand-ups and retrospectives, and I mentor junior developers. Communication is key - I make sure everyone understands the technical decisions we make."
    ]
    
    print("\n🤖 Step 3: Alex evaluates each answer...\n")
    
    # Evaluate each answer
    evaluations = []
    for i, (question, answer) in enumerate(zip(questions, sample_answers), 1):
        print(f"