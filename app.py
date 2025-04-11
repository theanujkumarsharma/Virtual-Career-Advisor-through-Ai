import streamlit as st
import os
from utils.openai_utils import get_ai_response
from utils.resume_parsar import extract_resume_text
from utils.data_analysis import get_skill_gap_analysis
import uuid
from PIL import Image
import requests
from io import BytesIO

# Setup page config
st.set_page_config(
    page_title="AI Career Advisor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
    
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
    
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "current_role": "",
        "experience_years": 0,
        "education": "",
        "skills": [],
        "career_goals": "",
        "industry": ""
    }
def load_image_from_url(url):
    """Load image from URL with error handling"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return Image.open(BytesIO(response.content))
    except Exception as e:
        st.warning(f"Couldn't load image from URL: {e}")
        return None

def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("AI Career Advisor")
        
        # Option 1: Use a local image file
        # image_path = os.path.join("images", "career_advisor.png")
        # if os.path.exists(image_path):
        #     st.image(image_path, width=150)
        # else:
        #     st.warning("Local image not found")
        
        # Option 2: Use a reliable URL
        image_url = "https://cdn-icons-png.flaticon.com/512/3281/3281289.png"  # Career advisor icon
        image = load_image_from_url(image_url)
        if image:
            st.image(image, width=150)
        else:
            # Fallback to emoji if image fails
            st.header("🚀 AI Career Advisor")
        
        # User profile section in sidebar
        st.subheader("Your Profile")
        if st.session_state.user_profile["current_role"]:
            st.info(f"Role: {st.session_state.user_profile['current_role']}")
            st.info(f"Experience: {st.session_state.user_profile['experience_years']} years")
            st.info(f"Industry: {st.session_state.user_profile['industry']}")
            
            if st.button("Edit Profile"):
                st.session_state.show_profile_editor = True
        else:
            st.warning("Complete your profile to get personalized advice")
            if st.button("Setup Profile"):
                st.session_state.show_profile_editor = True
        
        st.markdown("---")
        
        # Navigation options
        page = st.radio(
            "Navigate to:",
            ["Chat with AI Advisor", "Resume Analyzer", "Career Assessment", 
             "Job Market Insights", "Interview Preparation", "Job Search"]
        )
        
        st.markdown("---")
        st.caption("Powered by OpenAI and Streamlit")
    
    # Rest of your code remains the same...
    # Display the profile editor if requested
    if st.session_state.get("show_profile_editor", False):
        display_profile_editor()
    
    # Show the selected page content
    if page == "Chat with AI Advisor":
        display_chat_interface()
    elif page == "Resume Analyzer":
        st.switch_page("pages/resume_analyzer.py")
    elif page == "Career Assessment":
        st.switch_page("pages/career_assessment.py")
    elif page == "Job Market Insights":
        st.switch_page("pages/job_market_insights.py")
    elif page == "Interview Preparation":
        st.switch_page("pages/interview_prep.py")
    elif page == "Job Search":
        st.switch_page("pages/job_search.py")

# Rest of your functions remain unchanged...

def display_profile_editor():
    st.header("Set Up Your Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_role = st.text_input("Current Role", 
                                    value=st.session_state.user_profile["current_role"])
        experience = st.number_input("Years of Experience", 
                                    min_value=0, max_value=50, 
                                    value=st.session_state.user_profile["experience_years"])
        education = st.selectbox("Highest Education", 
                                ["High School", "Associate's Degree", "Bachelor's Degree", 
                                 "Master's Degree", "PhD", "Other"],
                                index=2 if not st.session_state.user_profile["education"] else 0)
    
    with col2:
        industry = st.selectbox("Industry", 
                               ["Technology", "Healthcare", "Finance", "Education", 
                                "Manufacturing", "Retail", "Other"],
                               index=0 if not st.session_state.user_profile["industry"] else 0)
        skills = st.text_area("Skills (comma separated)", 
                             value=",".join(st.session_state.user_profile["skills"]) if st.session_state.user_profile["skills"] else "")
        career_goals = st.text_area("Career Goals", 
                                  value=st.session_state.user_profile["career_goals"])
    
    if st.button("Save Profile"):
        st.session_state.user_profile = {
            "current_role": current_role,
            "experience_years": experience,
            "education": education,
            "skills": [skill.strip() for skill in skills.split(",") if skill.strip()],
            "career_goals": career_goals,
            "industry": industry
        }
        st.session_state.show_profile_editor = False
        st.success("Profile updated successfully!")
        st.rerun()
    
    if st.button("Cancel"):
        st.session_state.show_profile_editor = False
        st.rerun()

def display_chat_interface():
    st.header("Chat with Your AI Career Advisor")
    
    # Display welcome message if no messages yet
    if not st.session_state.messages:
        st.info("""
        👋 Welcome to your AI Career Advisor! I'm here to help you with:
        - Career guidance and planning
        - Resume improvement suggestions
        - Industry insights and trends
        - Skill development recommendations
        - Interview preparation
        - Job search strategies
        
        Just type your question or request below to get started!
        """)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input for new message
    if prompt := st.chat_input("Ask your career advisor..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Get AI response with user context
            context = {
                "profile": st.session_state.user_profile,
                "resume_text": st.session_state.resume_text,
                "chat_history": st.session_state.messages[:-1]  # Exclude the current message
            }
            
            response = get_ai_response(prompt, context)
            
            # Show the response with a typing effect
            for chunk in response.split():
                full_response += chunk + " "
                message_placeholder.markdown(full_response + "▌")
                import time
                time.sleep(0.01)
            
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
