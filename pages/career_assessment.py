# import streamlit as st
# import json
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from utils.openai_utils import get_openai_client, get_career_path_recommendations

# def app():
#     st.title("Career Assessment")
    
#     # Check if assessment has been completed
#     if "assessment_completed" not in st.session_state:
#         st.session_state.assessment_completed = False
    
#     if "assessment_results" not in st.session_state:
#         st.session_state.assessment_results = None
    
#     # Two options: take assessment or view results
#     if not st.session_state.assessment_completed:
#         st.header("Career Goals Assessment")
#         st.info("""
#         This assessment will help us understand your career goals, preferences, and strengths 
#         to provide personalized career recommendations. Please answer the following questions 
#         as honestly as possible.
#         """)
        
#         display_assessment_form()
#     else:
#         # Show tabs for results and retaking assessment
#         tab1, tab2 = st.tabs(["Assessment Results", "Retake Assessment"])
        
#         with tab1:
#             display_assessment_results()
        
#         with tab2:
#             if st.button("Start New Assessment"):
#                 st.session_state.assessment_completed = False
#                 st.rerun()

# def display_assessment_form():
#     """Display the career assessment questionnaire form."""
#     with st.form("career_assessment"):
#         st.subheader("About Your Career")
        
#         # Career satisfaction
#         satisfaction = st.slider(
#             "How satisfied are you with your current career? (1 = Not at all, 10 = Extremely satisfied)",
#             1, 10, 5
#         )
        
#         # Career goals
#         career_goals = st.text_area(
#             "What are your primary career goals for the next 3-5 years?",
#             placeholder="e.g., Advance to a management position, switch to a new field, etc."
#         )
        
#         st.subheader("Skills and Strengths")
        
#         # Technical skills
#         technical_skills = st.text_area(
#             "What technical skills do you possess? (Separate with commas)",
#             placeholder="e.g., Python, Excel, Data Analysis, Project Management, etc."
#         )
        
#         # Soft skills
#         SOFT_SKILL_OPTIONS = [
#             "Communication", "Leadership", "Teamwork", "Problem Solving", 
#             "Adaptability", "Time Management", "Creativity", "Critical Thinking",
#             "Emotional Intelligence", "Conflict Resolution", "Decision Making", 
#             "Networking", "Negotiation", "Public Speaking"
#         ]
        
#         soft_skills = st.multiselect(
#             "Select your strongest soft skills (choose up to 5):",
#             options=SOFT_SKILL_OPTIONS
#         )
        
#         # Work environment preferences
#         st.subheader("Work Environment Preferences")
        
#         work_environment = st.radio(
#             "What type of work environment do you prefer?",
#             ["Remote", "Office-based", "Hybrid", "No preference"]
#         )
        
#         work_structure = st.radio(
#             "Do you prefer structured work or more autonomous/flexible work?",
#             ["Highly structured", "Somewhat structured", "Balanced", "Mostly autonomous", "Completely autonomous"]
#         )
        
#         # Work values
#         st.subheader("Work Values")
        
#         WORK_VALUES = [
#             "High salary", "Work-life balance", "Creative freedom", 
#             "Job security", "Helping others", "Recognition", 
#             "Professional growth", "Challenging work", "Company culture",
#             "Authority/Leadership", "Independence", "Variety in work tasks"
#         ]
        
#         work_values = st.multiselect(
#             "Select the work values most important to you (choose up to 5):",
#             options=WORK_VALUES
#         )
        
#         # Additional information
#         st.subheader("Additional Information")
        
#         industries_interested = st.text_input(
#             "What industries are you interested in? (Separate with commas)",
#             placeholder="e.g., Technology, Healthcare, Finance, etc."
#         )
        
#         relocation = st.radio(
#             "Are you willing to relocate for career opportunities?",
#             ["Yes, anywhere", "Yes, but with limitations", "No"]
#         )
        
#         additional_info = st.text_area(
#             "Is there anything else you'd like to share about your career goals or preferences?",
#             placeholder="Any additional information that might help with recommendations"
#         )
        
#         # Submit button
#         submitted = st.form_submit_button("Submit Assessment")
        
#         if submitted:
#             # Process form data
#             assessment_data = {
#                 "satisfaction": satisfaction,
#                 "career_goals": career_goals,
#                 "technical_skills": [skill.strip() for skill in technical_skills.split(",") if skill.strip()],
#                 "soft_skills": soft_skills,
#                 "work_environment": work_environment,
#                 "work_structure": work_structure,
#                 "work_values": work_values,
#                 "industries_interested": [ind.strip() for ind in industries_interested.split(",") if ind.strip()],
#                 "relocation": relocation,
#                 "additional_info": additional_info
#             }
            
#             # Analyze results
#             with st.spinner("Analyzing your responses..."):
#                 results = analyze_assessment(assessment_data)
                
#                 # Store results in session state
#                 st.session_state.assessment_results = results
#                 st.session_state.assessment_completed = True
                
#                 # Reload the page to show results
#                 st.rerun()

# def analyze_assessment(assessment_data):
#     """
#     Analyze assessment data and generate personalized career recommendations.
    
#     Args:
#         assessment_data (dict): User's assessment responses
    
#     Returns:
#         dict: Analysis results and recommendations
#     """
#     client = get_openai_client()
    
#     # Convert assessment data to a formatted string
#     assessment_str = json.dumps(assessment_data, indent=2)
    
#     prompt = f"""
#     Analyze the following career assessment data and provide personalized career recommendations:
    
#     {assessment_str}
    
#     Please provide a JSON response with the following structure:
#     {{
#         "summary": "Brief summary of the assessment",
#         "strengths": ["Strength 1", "Strength 2", ...],
#         "work_style": "Description of the person's work style",
#         "career_recommendations": [
#             {{
#                 "title": "Career path title",
#                 "description": "Why this is a good fit",
#                 "match_score": 0-100,
#                 "required_skills": ["Skill 1", "Skill 2", ...],
#                 "skill_gaps": ["Skill 1", "Skill 2", ...],
#                 "next_steps": ["Step 1", "Step 2", ...]
#             }},
#             ...
#         ],
#         "development_areas": ["Area 1", "Area 2", ...],
#         "action_plan": ["Action 1", "Action 2", ...]
#     }}
    
#     Recommend 3-5 career paths that match their skills, values, and preferences.
#     """
    
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": "You are a career counselor with expertise in matching people with suitable careers."},
#                 {"role": "user", "content": prompt}
#             ],
#             response_format={"type": "json_object"},
#             temperature=0.7
#         )
        
#         results = json.loads(response.choices[0].message.content)
#         return results
#     except Exception as e:
#         return {
#             "error": f"Failed to analyze assessment: {str(e)}",
#             "summary": "Assessment analysis failed. Please try again.",
#             "strengths": [],
#             "work_style": "",
#             "career_recommendations": [],
#             "development_areas": [],
#             "action_plan": ["Try taking the assessment again."]
#         }

# def display_assessment_results():
#     """Display the results of the career assessment."""
#     results = st.session_state.assessment_results
    
#     if not results:
#         st.error("No assessment results found. Please complete the assessment first.")
#         return
    
#     if "error" in results:
#         st.error(results["error"])
#         return
    
#     # Summary section
#     st.header("Your Career Assessment Results")
#     st.subheader("Summary")
#     st.write(results.get("summary", "No summary available."))
    
#     # Strengths and work style
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Your Strengths")
#         strengths = results.get("strengths", [])
#         for strength in strengths:
#             st.markdown(f"✅ {strength}")
    
#     with col2:
#         st.subheader("Your Work Style")
#         st.write(results.get("work_style", "No work style information available."))
    
#     # Career recommendations
#     st.subheader("Recommended Career Paths")
    
#     recommendations = results.get("career_recommendations", [])
    
#     if not recommendations:
#         st.info("No specific career recommendations available.")
#     else:
#         # Create match score visualization
#         scores = [rec.get("match_score", 0) for rec in recommendations]
#         titles = [rec.get("title", "Unknown") for rec in recommendations]
        
#         match_df = pd.DataFrame({
#             "Career Path": titles,
#             "Match Score": scores
#         })
        
#         fig = px.bar(
#             match_df,
#             x="Career Path",
#             y="Match Score",
#             color="Match Score",
#             color_continuous_scale="Blues",
#             title="Career Path Match Scores",
#             range_y=[0, 100]
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
        
#         # Display detailed recommendations
#         for i, rec in enumerate(recommendations, 1):
#             with st.expander(f"{i}. {rec.get('title', 'Career Path')} - {rec.get('match_score', 0)}% Match"):
#                 st.markdown(f"**Why this fits you:** {rec.get('description', 'No description available.')}")
                
#                 # Required skills vs. skill gaps
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.markdown("**Required Skills:**")
#                     for skill in rec.get("required_skills", []):
#                         st.markdown(f"- {skill}")
                
#                 with col2:
#                     st.markdown("**Skills to Develop:**")
#                     for skill in rec.get("skill_gaps", []):
#                         st.markdown(f"- {skill}")
                
#                 # Next steps
#                 st.markdown("**Next Steps:**")
#                 for step in rec.get("next_steps", []):
#                     st.markdown(f"- {step}")
    
#     # Development areas
#     st.subheader("Areas for Development")
#     dev_areas = results.get("development_areas", [])
#     for area in dev_areas:
#         st.markdown(f"- {area}")
    
#     # Action plan
#     st.subheader("Recommended Action Plan")
#     action_plan = results.get("action_plan", [])
#     for i, action in enumerate(action_plan, 1):
#         st.markdown(f"{i}. {action}")
    
#     # Option to get career paths based on profile
#     st.header("Explore Additional Career Paths")
    
#     if st.button("Get More Career Path Suggestions"):
#         with st.spinner("Generating additional suggestions..."):
#             # Get profile info from session state
#             profile = st.session_state.user_profile
            
#             # Add assessment data to enrich the profile
#             if "technical_skills" in results:
#                 profile["skills"] = list(set(profile.get("skills", []) + results["technical_skills"]))
            
#             # Get career path recommendations
#             career_paths = get_career_path_recommendations(profile)
            
#             if "error" in career_paths:
#                 st.error(career_paths["error"])
#             else:
#                 # Display career paths
#                 paths = career_paths.get("career_paths", [])
                
#                 for path in paths:
#                     with st.expander(f"{path.get('title', 'Career Path')}"):
#                         st.markdown(f"**Why this could be a good fit:** {path.get('rationale', 'No rationale available.')}")
                        
#                         st.markdown("**Potential Roles:**")
#                         for role in path.get("potential_roles", []):
#                             st.markdown(f"- {role}")
                        
#                         st.markdown("**Next Steps:**")
#                         for step in path.get("next_steps", []):
#                             st.markdown(f"- {step}")

# if __name__ == "__main__":
#     app()




import streamlit as st
import json
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.openai_utils import get_openai_client, get_career_path_recommendations
except ImportError as e:
    st.error(f"Failed to import required modules: {str(e)}")
    st.stop()

def app():
    st.title("Career Assessment")
    
    # Initialize session state
    if "assessment_completed" not in st.session_state:
        st.session_state.assessment_completed = False
    if "assessment_results" not in st.session_state:
        st.session_state.assessment_results = None
    
    if not st.session_state.assessment_completed:
        display_assessment_form()
    else:
        display_assessment_results()

def display_assessment_form():
    """Display the career assessment questionnaire"""
    with st.form("career_assessment"):
        st.header("Career Goals Assessment")
        
        # [Keep your existing form fields]
        # ...
        
        if st.form_submit_button("Submit Assessment"):
            assessment_data = {
                # [Your existing data collection]
            }
            
            with st.spinner("Analyzing your responses..."):
                try:
                    results = analyze_assessment(assessment_data)
                    st.session_state.assessment_results = results
                    st.session_state.assessment_completed = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error analyzing assessment: {str(e)}")

def analyze_assessment(assessment_data: Dict) -> Dict:
    """Analyze assessment data using OpenAI"""
    client = get_openai_client()
    
    prompt = f"""Analyze this career assessment data and provide recommendations:
    {json.dumps(assessment_data, indent=2)}
    
    Include in JSON response:
    - summary: Brief assessment summary
    - strengths: List of key strengths
    - work_style: Description of work style
    - career_recommendations: List of career paths with:
      - title: Career path name
      - description: Why it fits
      - match_score: 0-100
      - required_skills: List
      - skill_gaps: List
      - next_steps: List
    - development_areas: List of areas to improve
    - action_plan: List of recommended actions
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert career counselor."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "error": str(e),
            "summary": "Analysis failed",
            "strengths": [],
            "work_style": "",
            "career_recommendations": [],
            "development_areas": [],
            "action_plan": ["Please try again later"]
        }

def display_assessment_results():
    """Display assessment results and recommendations"""
    results = st.session_state.assessment_results
    
    if not results:
        st.error("No assessment results found")
        return
    
    if "error" in results:
        st.error(results["error"])
        return
    
    # [Keep your existing results display code]
    # ...
    
    # Add career path recommendations section
    st.header("Explore Career Paths")
    if st.button("Get Personalized Career Paths"):
        with st.spinner("Generating career path recommendations..."):
            profile = {
                **st.session_state.user_profile,
                **results  # Include assessment insights
            }
            
            try:
                recommendations = get_career_path_recommendations(profile)
                
                if "error" in recommendations:
                    st.error(recommendations["error"])
                else:
                    display_career_paths(recommendations["career_paths"])
            except Exception as e:
                st.error(f"Failed to get recommendations: {str(e)}")

def display_career_paths(paths: list[Dict]):
    """Display career path recommendations"""
    if not paths:
        st.info("No specific career paths recommended")
        return
    
    st.subheader("Recommended Career Paths")
    
    # Create visualization
    df = pd.DataFrame([{
        "Path": p["title"],
        "Match Score": p.get("match_score", 0)
    } for p in paths])
    
    if not df.empty:
        fig = px.bar(
            df,
            x="Path",
            y="Match Score",
            color="Match Score",
            title="Career Path Recommendations"
        )
        st.plotly_chart(fig)
    
    # Display detailed paths
    for path in paths:
        with st.expander(f"{path['title']} ({path.get('match_score', 'N/A')}% match)"):
            st.markdown(f"**Why this fits:** {path.get('rationale', '')}")
            
            st.markdown("**Potential Roles:**")
            for role in path.get("potential_roles", []):
                st.markdown(f"- {role}")
            
            st.markdown("**Next Steps:**")
            for step in path.get("next_steps", []):
                st.markdown(f"- {step}")

if __name__ == "__main__":
    app()