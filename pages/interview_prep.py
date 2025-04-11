import streamlit as st
import json
import sys
from pathlib import Path
# Initialize session state variables
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "current_role": "",
        "experience_years": 0,
        "skills": [],
        "industry": ""
    }


# Add the parent directory to Python path to allow imports from utils
try:
    from utils.openai_utils import get_interview_prep
except ImportError as e:
    st.error(f"Failed to import required modules: {str(e)}")
    st.stop()

def app():
    st.title("Interview Preparation")
    
    # Introduction section
    st.markdown("""
    Prepare for your upcoming interviews with personalized questions and guidance.
    Get common interview questions, technical questions, and behavioral questions
    tailored to your target position.
    """)
    
    # Job position input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Default to user's current role if available
        default_role = st.session_state.user_profile.get("current_role", "")
        job_position = st.text_input(
            "What position are you interviewing for?", 
            value=default_role
        )
    
    with col2:
        experience_level = st.selectbox(
            "Experience Level",
            ["Entry-level", "Mid-level", "Senior"],
            index=1
        )
    
    # Map the experience level to the format expected by the API
    exp_level_map = {
        "Entry-level": "beginner",
        "Mid-level": "mid",
        "Senior": "senior"
    }
    
    # Generate preparation content when user clicks the button
    if job_position and st.button("Generate Interview Preparation"):
        with st.spinner(f"Generating interview preparation for {job_position}..."):
            interview_content = get_interview_prep(
                job_position, 
                exp_level_map.get(experience_level, "mid")
            )
            
            if "error" in interview_content:
                st.error(interview_content["error"])
            else:
                display_interview_prep(interview_content)
    else:
        # Show general interview tips when no specific content is generated
        display_general_interview_tips()

def display_interview_prep(content):
    """
    Display the generated interview preparation content.
    
    Args:
        content (dict): The interview preparation content
    """
    st.header(f"Interview Preparation Guide")
    
    # General tips
    st.subheader("General Interview Tips")
    tips = content.get("general_tips", [])
    for tip in tips:
        st.markdown(f"✅ {tip}")
    
    # Common questions
    st.subheader("Common Interview Questions")
    common_questions = content.get("common_questions", [])
    
    for i, q in enumerate(common_questions, 1):
        with st.expander(f"Q{i}: {q.get('question', '')}"):
            st.markdown("**Tips for answering:**")
            st.write(q.get("answer_tips", "No tips available."))
            
            if "example_answer" in q and q["example_answer"]:
                st.markdown("**Example answer:**")
                st.info(q["example_answer"])
    
    # Technical questions
    st.subheader("Technical Questions")
    technical_questions = content.get("technical_questions", [])
    
    for i, q in enumerate(technical_questions, 1):
        with st.expander(f"Q{i}: {q.get('question', '')}"):
            st.markdown("**Tips for answering:**")
            st.write(q.get("answer_tips", "No tips available."))
    
    # Behavioral questions
    st.subheader("Behavioral Questions")
    behavioral_questions = content.get("behavioral_questions", [])
    
    for i, q in enumerate(behavioral_questions, 1):
        with st.expander(f"Q{i}: {q.get('question', '')}"):
            st.markdown("**Tips for answering:**")
            st.write(q.get("answer_tips", "No tips available."))
            
            if "example_approach" in q and q["example_approach"]:
                st.markdown("**Example approach (STAR method):**")
                st.info(q["example_approach"])
    
    # Questions to ask the interviewer
    st.subheader("Questions to Ask the Interviewer")
    questions_to_ask = content.get("questions_to_ask_interviewer", [])
    
    st.markdown("""
    Asking thoughtful questions demonstrates your interest in the role and company.
    Consider asking some of these questions:
    """)
    
    for question in questions_to_ask:
        st.markdown(f"- {question}")
    
    # Interview preparation checklist
    st.subheader("Interview Preparation Checklist")
    
    checklist_items = [
        "Research the company thoroughly",
        "Review the job description and requirements",
        "Prepare your STAR stories for behavioral questions",
        "Practice technical questions related to your field",
        "Prepare questions to ask the interviewer",
        "Plan your interview outfit",
        "Test your technology if it's a virtual interview",
        "Prepare copies of your resume and portfolio",
        "Plan your route to the interview location",
        "Practice with a friend or mentor"
    ]
    
    for item in checklist_items:
        st.checkbox(item, key=f"checklist_{item}")
    
    # Interview simulation option
    st.subheader("Practice with AI Interview Coach")
    st.markdown("""
    Would you like to practice your interview skills with an AI coach?
    Select a question type and click 'Start Practice Session' to begin.
    """)
    
    # Create options for practice
    practice_options = []
    
    if common_questions:
        practice_options.append("Common Questions")
    if technical_questions:
        practice_options.append("Technical Questions")
    if behavioral_questions:
        practice_options.append("Behavioral Questions")
    
    if practice_options:
        question_type = st.selectbox("Select question type to practice", practice_options)
        
        if st.button("Start Practice Session"):
            # Select questions based on type
            if question_type == "Common Questions":
                practice_questions = common_questions
            elif question_type == "Technical Questions":
                practice_questions = technical_questions
            else:  # Behavioral Questions
                practice_questions = behavioral_questions
            
            # Start practice session
            st.session_state.practice_mode = True
            st.session_state.practice_questions = practice_questions
            st.session_state.current_question_index = 0
            
            # Redirect to practice interface
            display_practice_interface()
    else:
        st.info("No practice questions available. Please generate interview preparation first.")

def display_practice_interface():
    """Display the interview practice interface."""
    st.subheader("Interview Practice Session")
    
    questions = st.session_state.practice_questions
    current_index = st.session_state.current_question_index
    
    if current_index < len(questions):
        question = questions[current_index]
        
        # Display current question
        st.markdown(f"**Question {current_index + 1}:** {question.get('question', '')}")
        
        # Input for user's answer
        user_answer = st.text_area("Your answer:", height=150)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Submit Answer"):
                if user_answer:
                    st.session_state.last_answer = user_answer
                    st.session_state.show_feedback = True
                else:
                    st.warning("Please provide an answer before submitting.")
        
        with col2:
            if st.button("Skip Question"):
                st.session_state.current_question_index += 1
                st.rerun()
        
        # Show feedback if requested
        if st.session_state.get("show_feedback", False):
            st.subheader("Feedback")
            
            # Show tips from the question
            st.markdown("**Key points to include:**")
            st.info(question.get("answer_tips", "No tips available."))
            
            if "example_answer" in question and question["example_answer"]:
                st.markdown("**Example good answer:**")
                st.success(question["example_answer"])
            elif "example_approach" in question and question["example_approach"]:
                st.markdown("**Example approach:**")
                st.success(question["example_approach"])
            
            # Option to continue
            if st.button("Next Question"):
                st.session_state.current_question_index += 1
                st.session_state.show_feedback = False
                st.rerun()
    else:
        # End of practice session
        st.success("You've completed the practice session!")
        
        if st.button("Start New Practice Session"):
            st.session_state.practice_mode = False
            st.rerun()

def display_general_interview_tips():
    """Display general interview tips when no specific content is generated."""
    st.header("General Interview Tips")
    
    # Before the interview tips
    st.subheader("Before the Interview")
    
    before_tips = [
        "Research the company's mission, values, products, and recent news",
        "Review the job description and prepare examples that showcase relevant skills",
        "Practice common interview questions using the STAR method (Situation, Task, Action, Result)",
        "Prepare thoughtful questions to ask the interviewer",
        "Plan your interview outfit - dress professionally and slightly more formal than the company dress code",
        "Test your technology and internet connection for virtual interviews",
        "Plan your route to the interview location and aim to arrive 10-15 minutes early"
    ]
    
    for tip in before_tips:
        st.markdown(f"✅ {tip}")
    
    # During the interview tips
    st.subheader("During the Interview")
    
    during_tips = [
        "Make a strong first impression with a firm handshake and confident introduction",
        "Maintain good posture and appropriate eye contact",
        "Listen actively and ask for clarification if needed",
        "Use the STAR method to structure your answers to behavioral questions",
        "Be specific with examples rather than speaking in generalities",
        "Show enthusiasm for the role and company",
        "Be authentic - it's okay to briefly pause to collect your thoughts",
        "When discussing weaknesses, include how you're working to improve them"
    ]
    
    for tip in during_tips:
        st.markdown(f"✅ {tip}")
    
    # After the interview tips
    st.subheader("After the Interview")
    
    after_tips = [
        "Send a personalized thank-you email within 24 hours",
        "Reference specific topics discussed in the interview",
        "Follow up if you haven't heard back within the timeframe they provided",
        "Reflect on the interview to identify areas for improvement",
        "Continue your job search until you have a formal offer"
    ]
    
    for tip in after_tips:
        st.markdown(f"✅ {tip}")
    
    # STAR method explanation
    with st.expander("The STAR Method Explained"):
        st.markdown("""
        The STAR method is a structured way to respond to behavioral interview questions:
        
        - **Situation**: Describe the context or background
        - **Task**: Explain your responsibility or challenge
        - **Action**: Detail the specific steps you took
        - **Result**: Share the outcomes and what you learned
        
        Example STAR response for "Tell me about a time you faced a challenge":
        
        **Situation**: "At my previous company, we experienced a critical system outage during our peak business period."
        
        **Task**: "As the lead developer, I needed to identify the cause and restore service while minimizing impact."
        
        **Action**: "I quickly organized the team into two groups - one to implement our backup system for temporary service restoration, and another to diagnose the root cause. I personally led the diagnostic team, methodically isolating components until we identified a database connection issue."
        
        **Result**: "We restored full service within 3 hours, reducing the estimated financial impact by 70%. Afterward, I implemented new monitoring protocols that have prevented similar issues. This experience improved our team's emergency response procedures and led to more robust systems."
        """)
    
    # Get started button
    st.info("Enter your target position above and click 'Generate Interview Preparation' to get tailored questions and advice.")

if __name__ == "__main__":
    app()
