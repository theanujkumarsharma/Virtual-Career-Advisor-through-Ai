import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Optional, Union

# Load environment variables from .env file
load_dotenv()

# Configuration
MODEL = "gpt-4o"  # Default to GPT-4o model
MAX_RETRIES = 3  # Number of retry attempts for API calls
TIMEOUT = 30  # Timeout in seconds

def get_openai_client() -> OpenAI:
    """
    Get the OpenAI client instance with proper API key configuration.
    
    Returns:
        OpenAI: Authenticated OpenAI client instance
        
    Raises:
        ValueError: If API key is not properly configured
    """
    # Try multiple potential sources for the API key
    api_key = (
"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")
    
    if not api_key or api_key == "your-api-key-here":
        raise ValueError(
            "OpenAI API key not found. Please:\n"
            "1. Create a .env file with OPENAI_API_KEY=your_key\n"
            "2. Or set environment variable: export OPENAI_API_KEY=your_key\n"
            "3. Or replace 'your-api-key-here' with your actual key (not recommended for production)"
        )
    
    return OpenAI(
        api_key=api_key,
        timeout=TIMEOUT
    )
def get_career_path_recommendations(profile: Dict) -> Dict:
    """
    Generate career path recommendations based on user profile
    
    Args:
        profile: User profile including skills, experience, etc.
        
    Returns:
        dict: {
            "career_paths": [
                {
                    "title": "Career Path Name",
                    "rationale": "Why this fits",
                    "potential_roles": [],
                    "next_steps": []
                }
            ]
        }
    """
    client = get_openai_client()
    
    prompt = f"""Analyze this career profile and suggest suitable career paths:
    {json.dumps(profile, indent=2)}
    
    For each recommended path include:
    1. Title
    2. Rationale (why it fits)
    3. Potential roles
    4. Concrete next steps
    
    Return as JSON with 'career_paths' key containing a list of recommendations.
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert career counselor providing personalized career advice."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "error": f"Failed to generate recommendations: {str(e)}",
            "career_paths": []
        }

def get_interview_prep(job_title: str, experience_level: str) -> Dict:
    """
    Generate comprehensive interview preparation content
    
    Args:
        job_title: Position being interviewed for        experience_level: 'beginner', 'mid', or 'senior'
    
    Returns:
        dict: Structured preparation content or error message
    """
    client = get_openai_client()
    
    prompt = f"""Generate interview preparation for a {experience_level} level {job_title} position.
    Include these sections in JSON format:
    1. general_tips: List of general interview tips
    2. common_questions: List of common questions with:
       - question: text
       - answer_tips: text
       - example_answer: text (optional)
    3. technical_questions: List of technical questions with:
       - question: text  
       - answer_tips: text
    4. behavioral_questions: List of behavioral questions with:
       - question: text
       - answer_tips: text
       - example_approach: STAR method example
    5. questions_to_ask_interviewer: List of questions
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert career coach providing interview preparation."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "error": f"Failed to generate content: {str(e)}",
            "general_tips": ["Error occurred while generating content"],
            "common_questions": [],
            "technical_questions": [],
            "behavioral_questions": [],
            "questions_to_ask_interviewer": []
        }
def get_ai_response(user_prompt: str, context: Optional[Dict] = None) -> str:
    """
    Get a response from the OpenAI API with robust error handling.
    
    Args:
        user_prompt: The user's question or prompt
        context: Optional context information
        
    Returns:
        str: The AI-generated response or error message
    """
    client = get_openai_client()
    
    # Build system message with context
    system_message = """You are an AI Career Advisor providing professional career guidance.
    Be supportive, informative, and provide specific, actionable advice."""
    
    if context:
        if context.get("profile"):
            profile = context["profile"]
            system_message += f"\nUser Profile:\n- Role: {profile.get('current_role')}\n- Experience: {profile.get('experience_years')} years\n- Skills: {', '.join(profile.get('skills', []))}"
        
        if context.get("resume_text"):
            system_message += "\nUser has uploaded a resume (summary available)."
    
    messages = [
        {"role": "system", "content": system_message},
    ]
    
    # Add chat history if available
    if context and context.get("chat_history"):
        messages.extend(context["chat_history"][-5:])  # Last 5 messages
    
    messages.append({"role": "user", "content": user_prompt})
    
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt == MAX_RETRIES - 1:  # Last attempt failed
                return f"I encountered an error: {str(e)}. Please try again later."
            continue

def analyze_resume(resume_text: str) -> Dict:
    """
    Analyze a resume with comprehensive error handling.
    
    Args:
        resume_text: Text content of the resume
        
    Returns:
        dict: Analysis results or error information
    """
    client = get_openai_client()
    
    prompt = f"""
    Analyze this resume and provide structured JSON feedback:
    {resume_text[:15000]}  # Truncate to avoid token limits
    
    Include:
    - strengths
    - weaknesses 
    - improvement_suggestions
    - skills_analysis (present/missing)
    - ats_compatibility_score (1-10)
    - content_overview
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert resume analyst."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        return {
            "error": f"Resume analysis failed: {str(e)}",
            "strengths": ["Analysis unavailable"],
            "weaknesses": ["Could not analyze resume"],
            "improvement_suggestions": ["Try again later"],
            "skills_analysis": {"present": [], "missing": []},
            "ats_compatibility_score": 0,
            "content_overview": "Analysis failed"
        }

# [Keep your existing get_career_path_recommendations and get_interview_prep functions]
# [Add any other existing functions here with similar error handling]