# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import plotly.express as px
# from utils.resume_parsar import extract_resume_text, extract_skills
# from utils.openai_utils import analyze_resume
# from utils.nlp_utils import extract_keywords, extract_action_verbs
# import base64

# def app():
#     st.title("Resume Analyzer")
    
#     # Resume upload section
#     st.header("Upload Your Resume")
#     uploaded_file = st.file_uploader("Choose a resume file (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    
#     if uploaded_file is not None:
#         with st.spinner("Analyzing your resume..."):
#             # Extract text from the uploaded resume
#             resume_text = extract_resume_text(uploaded_file)
            
#             if not resume_text:
#                 st.error("Could not extract text from the uploaded file. Please try another file.")
#                 return
            
#             # Store in session state for other pages to use
#             st.session_state.resume_text = resume_text
            
#             # Display the extracted text with option to expand/collapse
#             with st.expander("View Extracted Text"):
#                 st.text_area("Resume Content", resume_text, height=300)
            
#             # Analyze the resume using OpenAI
#             analysis = analyze_resume(resume_text)
            
#             if "error" in analysis:
#                 st.error(analysis["error"])
#                 return
            
#             # Display analysis results
#             display_analysis_results(analysis, resume_text)
            
#     else:
#         if st.session_state.resume_text:
#             # If resume was previously uploaded
#             st.info("Using previously uploaded resume.")
#             resume_text = st.session_state.resume_text
            
#             if st.button("Re-analyze Resume"):
#                 with st.spinner("Re-analyzing your resume..."):
#                     analysis = analyze_resume(resume_text)
#                     display_analysis_results(analysis, resume_text)
#         else:
#             st.info("Please upload your resume to get a detailed analysis with improvement suggestions.")

# def display_analysis_results(analysis, resume_text):
#     # Overview section
#     st.header("Resume Analysis")
#     st.subheader("Overview")
#     st.write(analysis.get("content_overview", "No overview available"))
    
#     # ATS Compatibility Score
#     ats_score = analysis.get("ats_compatibility_score", 0)
#     st.subheader("ATS Compatibility Score")
    
#     # Create a gauge chart for the ATS score
#     fig = create_gauge_chart(ats_score, "ATS Compatibility", 0, 10)
#     st.plotly_chart(fig)
    
#     # Add explanation for ATS score
#     if ats_score < 4:
#         st.error("Your resume may not pass through Applicant Tracking Systems effectively.")
#     elif ats_score < 7:
#         st.warning("Your resume could be improved for better ATS compatibility.")
#     else:
#         st.success("Your resume is well-optimized for Applicant Tracking Systems.")
    
#     # Strengths and weaknesses
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("Strengths")
#         strengths = analysis.get("strengths", [])
#         for strength in strengths:
#             st.markdown(f"✅ {strength}")
    
#     with col2:
#         st.subheader("Areas for Improvement")
#         weaknesses = analysis.get("weaknesses", [])
#         for weakness in weaknesses:
#             st.markdown(f"⚠️ {weakness}")
    
#     # Skills analysis
#     st.subheader("Skills Analysis")
    
#     # Extracted vs. recognized skills
#     extracted_skills = extract_skills(resume_text)
#     recognized_skills = analysis.get("skills_analysis", {}).get("present", [])
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("**Skills Found in Your Resume:**")
#         if recognized_skills:
#             for skill in recognized_skills:
#                 st.markdown(f"- {skill}")
#         else:
#             st.info("No specific skills were recognized.")
    
#     with col2:
#         st.markdown("**Recommended Skills to Add:**")
#         missing_skills = analysis.get("skills_analysis", {}).get("missing", [])
#         if missing_skills:
#             for skill in missing_skills:
#                 st.markdown(f"- {skill}")
#         else:
#             st.success("Your skills section appears comprehensive!")
    
#     # Word usage analysis
#     st.subheader("Word Usage Analysis")
    
#     # Extract action verbs
#     action_verbs = extract_action_verbs(resume_text)
#     keywords = extract_keywords(resume_text, 15)
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("**Top Keywords:**")
        
#         # Create a DataFrame for the keywords
#         if keywords:
#             df = pd.DataFrame(keywords, columns=["Word", "Frequency"])
            
#             # Create a bar chart
#             fig = px.bar(df, x="Word", y="Frequency", title="Top Keywords in Your Resume")
#             st.plotly_chart(fig)
#         else:
#             st.info("No significant keywords found.")
    
#     with col2:
#         st.markdown("**Action Verbs Used:**")
#         if action_verbs:
#             for verb in action_verbs:
#                 st.markdown(f"- {verb}")
#         else:
#             st.warning("No common action verbs detected. Consider adding more achievement-oriented language.")
    
#     # Improvement suggestions
#     st.subheader("Improvement Suggestions")
#     suggestions = analysis.get("improvement_suggestions", [])
    
#     for i, suggestion in enumerate(suggestions, 1):
#         st.markdown(f"**{i}. {suggestion}**")
    
#     # Download improved resume template (placeholder)
#     st.subheader("Get Improvement Help")
#     if st.button("Generate Improvement Report"):
#         # Generate report as a simple text file
#         report = generate_improvement_report(analysis, resume_text)
        
#         # Create a download link
#         b64 = base64.b64encode(report.encode()).decode()
#         href = f'<a href="data:file/txt;base64,{b64}" download="resume_improvement_report.txt">Download Improvement Report</a>'
#         st.markdown(href, unsafe_allow_html=True)

# def create_gauge_chart(value, title, min_val, max_val):
#     """Create a gauge chart for visualizing scores."""
#     fig = px.pie(
#         values=[value, max_val - value],
#         names=["Score", ""],
#         hole=0.7,
#         color_discrete_sequence=["#0283C7", "#EEEEEE"]
#     )
    
#     fig.update_layout(
#         annotations=[
#             dict(
#                 text=f"{value}/{max_val}",
#                 x=0.5, y=0.5,
#                 font_size=24,
#                 showarrow=False
#             )
#         ],
#         showlegend=False,
#         title={
#             "text": title,
#             "y": 0.9,
#             "x": 0.5,
#             "xanchor": "center",
#             "yanchor": "top"
#         },
#         height=300
#     )
    
#     return fig

# def generate_improvement_report(analysis, resume_text):
#     """Generate a text report with improvement suggestions."""
#     report = "RESUME IMPROVEMENT REPORT\n"
#     report += "=========================\n\n"
    
#     # Add overview
#     report += "OVERVIEW:\n"
#     report += analysis.get("content_overview", "No overview available") + "\n\n"
    
#     # Add ATS score
#     ats_score = analysis.get("ats_compatibility_score", 0)
#     report += f"ATS COMPATIBILITY SCORE: {ats_score}/10\n"
    
#     if ats_score < 4:
#         report += "WARNING: Your resume may not pass through Applicant Tracking Systems effectively.\n"
#     elif ats_score < 7:
#         report += "NOTE: Your resume could be improved for better ATS compatibility.\n"
#     else:
#         report += "GOOD: Your resume is well-optimized for Applicant Tracking Systems.\n"
#     report += "\n"
    
#     # Add strengths
#     report += "STRENGTHS:\n"
#     strengths = analysis.get("strengths", [])
#     for strength in strengths:
#         report += f"✓ {strength}\n"
#     report += "\n"
    
#     # Add weaknesses
#     report += "AREAS FOR IMPROVEMENT:\n"
#     weaknesses = analysis.get("weaknesses", [])
#     for weakness in weaknesses:
#         report += f"! {weakness}\n"
#     report += "\n"
    
#     # Add skills analysis
#     report += "SKILLS ANALYSIS:\n"
#     report += "Skills Found in Your Resume:\n"
#     recognized_skills = analysis.get("skills_analysis", {}).get("present", [])
#     for skill in recognized_skills:
#         report += f"- {skill}\n"
    
#     report += "\nRecommended Skills to Add:\n"
#     missing_skills = analysis.get("skills_analysis", {}).get("missing", [])
#     for skill in missing_skills:
#         report += f"- {skill}\n"
#     report += "\n"
    
#     # Add improvement suggestions
#     report += "DETAILED IMPROVEMENT SUGGESTIONS:\n"
#     suggestions = analysis.get("improvement_suggestions", [])
#     for i, suggestion in enumerate(suggestions, 1):
#         report += f"{i}. {suggestion}\n"
    
#     return report

# if __name__ == "__main__":
#     app()


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import base64
import sys
from pathlib import Path
import nltk

# Initialize session state variables
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Initialize NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        # Handle SSL certificate issues
        import ssl
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        
        nltk.download('punkt')
        nltk.download('stopwords')
    except Exception as e:
        st.error(f"Failed to download NLTK data: {str(e)}")
        st.stop()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from utils.resume_parsar import extract_resume_text, extract_skills
    from utils.openai_utils import analyze_resume
    from utils.nlp_utils import extract_keywords, extract_action_verbs
except ImportError as e:
    st.error(f"Failed to import required modules: {str(e)}")
    st.stop()

def app():
    st.title("Resume Analyzer")
    
    # Resume upload section
    st.header("Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Choose a resume file (PDF, DOCX, or TXT)", 
        type=["pdf", "docx", "txt"]
    )
    
    if uploaded_file is not None:
        with st.spinner("Analyzing your resume..."):
            try:
                # Extract text from the uploaded resume
                resume_text = extract_resume_text(uploaded_file)
                
                if not resume_text:
                    st.error("Could not extract text from the uploaded file.")
                    return
                
                # Store in session state for other pages to use
                st.session_state.resume_text = resume_text
                
                # Display the extracted text with option to expand/collapse
                with st.expander("View Extracted Text"):
                    st.text_area("Resume Content", resume_text, height=300)
                
                # Analyze the resume using OpenAI
                analysis = analyze_resume(resume_text)
                
                if "error" in analysis:
                    st.error(analysis["error"])
                    return
                
                # Display analysis results
                display_analysis_results(analysis, resume_text)
                
            except Exception as e:
                st.error(f"Error analyzing resume: {str(e)}")
    else:
        if st.session_state.get("resume_text"):
            # If resume was previously uploaded
            st.info("Using previously uploaded resume.")
            resume_text = st.session_state.resume_text
            
            if st.button("Re-analyze Resume"):
                with st.spinner("Re-analyzing your resume..."):
                    try:
                        analysis = analyze_resume(resume_text)
                        display_analysis_results(analysis, resume_text)
                    except Exception as e:
                        st.error(f"Error re-analyzing resume: {str(e)}")
        else:
            st.info("Please upload your resume to get a detailed analysis.")

def display_analysis_results(analysis, resume_text):
    """Display the analysis results"""
    # Overview section
    st.header("Resume Analysis")
    st.subheader("Overview")
    st.write(analysis.get("content_overview", "No overview available"))
    
    # ATS Compatibility Score
    ats_score = analysis.get("ats_compatibility_score", 0)
    st.subheader("ATS Compatibility Score")
    
    # Create a gauge chart for the ATS score
    fig = create_gauge_chart(ats_score, "ATS Compatibility", 0, 10)
    st.plotly_chart(fig)
    
    # Add explanation for ATS score
    if ats_score < 4:
        st.error("Your resume may not pass through Applicant Tracking Systems effectively.")
    elif ats_score < 7:
        st.warning("Your resume could be improved for better ATS compatibility.")
    else:
        st.success("Your resume is well-optimized for Applicant Tracking Systems.")
    
    # Strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Strengths")
        strengths = analysis.get("strengths", [])
        for strength in strengths:
            st.markdown(f"✅ {strength}")
    
    with col2:
        st.subheader("Areas for Improvement")
        weaknesses = analysis.get("weaknesses", [])
        for weakness in weaknesses:
            st.markdown(f"⚠️ {weakness}")
    
    # Skills analysis
    st.subheader("Skills Analysis")
    
    # Extracted vs. recognized skills
    extracted_skills = extract_skills(resume_text)
    recognized_skills = analysis.get("skills_analysis", {}).get("present", [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Skills Found in Your Resume:**")
        if recognized_skills:
            for skill in recognized_skills:
                st.markdown(f"- {skill}")
        else:
            st.info("No specific skills were recognized.")
    
    with col2:
        st.markdown("**Recommended Skills to Add:**")
        missing_skills = analysis.get("skills_analysis", {}).get("missing", [])
        if missing_skills:
            for skill in missing_skills:
                st.markdown(f"- {skill}")
        else:
            st.success("Your skills section appears comprehensive!")
    
    # Word usage analysis
    st.subheader("Word Usage Analysis")
    
    try:
        # Extract action verbs and keywords
        action_verbs = extract_action_verbs(resume_text)
        keywords = extract_keywords(resume_text, 15)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top Keywords:**")
            if keywords:
                df = pd.DataFrame(keywords, columns=["Word", "Frequency"])
                fig = px.bar(df, x="Word", y="Frequency", title="Top Keywords in Your Resume")
                st.plotly_chart(fig)
            else:
                st.info("No significant keywords found.")
        
        with col2:
            st.markdown("**Action Verbs Used:**")
            if action_verbs:
                for verb in action_verbs:
                    st.markdown(f"- {verb}")
            else:
                st.warning("No common action verbs detected. Consider adding more achievement-oriented language.")
    except Exception as e:
        st.warning(f"Could not complete word analysis: {str(e)}")
    
    # Improvement suggestions
    st.subheader("Improvement Suggestions")
    suggestions = analysis.get("improvement_suggestions", [])
    for i, suggestion in enumerate(suggestions, 1):
        st.markdown(f"**{i}. {suggestion}**")
    
    # Download improved resume template
    st.subheader("Get Improvement Help")
    if st.button("Generate Improvement Report"):
        report = generate_improvement_report(analysis, resume_text)
        b64 = base64.b64encode(report.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="resume_improvement_report.txt">Download Improvement Report</a>'
        st.markdown(href, unsafe_allow_html=True)

# [Keep your existing create_gauge_chart and generate_improvement_report functions]

if __name__ == "__main__":
    app()