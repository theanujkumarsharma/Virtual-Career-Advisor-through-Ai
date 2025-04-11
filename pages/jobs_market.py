import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.data_analysis import get_job_market_insights, generate_job_growth_chart, generate_salary_range_chart
from utils.openai_utils import get_openai_client
import json

def app():
    st.title("Job Market Insights")
    
    # Industry selection
    industries = [
        "Technology", "Healthcare", "Finance", "Education", 
        "Manufacturing", "Retail", "Other"
    ]
    
    default_index = 0
    if st.session_state.user_profile.get("industry"):
        # Set default based on user profile if available
        user_industry = st.session_state.user_profile["industry"]
        if user_industry in industries:
            default_index = industries.index(user_industry)
    
    selected_industry = st.selectbox(
        "Select an industry to explore", 
        industries,
        index=default_index
    )
    
    # Get job market insights for the selected industry
    industry_data = get_job_market_insights(selected_industry)
    
    # Display industry insights
    st.header(f"{selected_industry} Industry Insights")
    
    # Job growth trends chart
    st.subheader("Job Growth Trends")
    job_growth_fig = generate_job_growth_chart(industry_data)
    st.plotly_chart(job_growth_fig, use_container_width=True)
    
    # Top skills in demand
    st.subheader("Top Skills in Demand")
    top_skills = industry_data.get("top_skills", [])
    
    # Create skill demand chart
    skill_values = np.linspace(70, 100, len(top_skills))  # Sample demand percentages
    skill_df = pd.DataFrame({
        "Skill": top_skills,
        "Demand (%)": skill_values
    })
    
    skill_fig = px.bar(
        skill_df,
        x="Skill",
        y="Demand (%)",
        color="Demand (%)",
        color_continuous_scale="Blues",
        title="Skills in Highest Demand"
    )
    
    st.plotly_chart(skill_fig, use_container_width=True)
    
    # Salary trends
    st.subheader("Salary Trends")
    
    # Get roles to compare
    growing_roles = industry_data.get("growing_roles", [])
    if growing_roles:
        # Limit to top 5 roles to avoid overcrowding
        roles_to_compare = growing_roles[:5]
        salary_fig = generate_salary_range_chart(roles_to_compare)
        st.plotly_chart(salary_fig, use_container_width=True)
        st.caption("Note: Salary data is approximate and may vary by location and individual experience.")
    else:
        st.info("No salary data available for this industry.")
    
    # Specific role analysis
    st.header("Specific Role Analysis")
    
    # Let user select or input a specific role
    role_options = growing_roles + industry_data.get("declining_roles", [])
    
    if role_options:
        selected_role = st.selectbox("Select a role to analyze", role_options)
    else:
        selected_role = st.text_input("Enter a role to analyze")
    
    if selected_role and st.button("Analyze Role"):
        with st.spinner(f"Analyzing the {selected_role} role..."):
            role_analysis = get_role_analysis(selected_role, selected_industry)
            
            if "error" in role_analysis:
                st.error(role_analysis["error"])
            else:
                # Display role analysis
                st.subheader(f"{selected_role} Role Analysis")
                
                # Role description
                st.markdown("**Role Description:**")
                st.write(role_analysis.get("description", "No description available."))
                
                # Required skills
                st.markdown("**Key Skills Required:**")
                for skill in role_analysis.get("required_skills", []):
                    st.markdown(f"- {skill}")
                
                # Education and qualifications
                st.markdown("**Typical Education/Qualifications:**")
                for qual in role_analysis.get("qualifications", []):
                    st.markdown(f"- {qual}")
                
                # Future outlook
                st.markdown("**Future Outlook:**")
                st.write(role_analysis.get("future_outlook", "No outlook data available."))
                
                # Career progression
                st.markdown("**Typical Career Progression:**")
                for step in role_analysis.get("career_progression", []):
                    st.markdown(f"- {step}")
    
    # Industry trends and news
    st.header("Industry Trends and News")
    with st.spinner("Loading industry trends..."):
        trends = get_industry_trends(selected_industry)
        
        # Display trends
        for trend in trends.get("trends", []):
            st.subheader(trend.get("title", ""))
            st.write(trend.get("description", ""))
            
        # Display related articles/resources
        st.subheader("Related Resources")
        for resource in trends.get("resources", []):
            st.markdown(f"- **{resource.get('title', '')}**: {resource.get('description', '')}")

def get_role_analysis(role, industry):
    """
    Get detailed analysis for a specific role using OpenAI.
    
    Args:
        role (str): The role to analyze
        industry (str): The industry context
    
    Returns:
        dict: Role analysis data
    """
    client = get_openai_client()
    
    prompt = f"""
    Provide a detailed analysis of the {role} role in the {industry} industry.
    
    Please provide a JSON response with the following structure:
    {{
        "description": "Brief description of the role",
        "required_skills": ["Skill 1", "Skill 2", ...],
        "qualifications": ["Qualification 1", "Qualification 2", ...],
        "future_outlook": "Analysis of future prospects for this role",
        "career_progression": ["Next step 1", "Next step 2", ...]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert career and job market analyst."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {
            "error": f"Failed to analyze role: {str(e)}",
            "description": f"Analysis for {role} is currently unavailable."
        }

def get_industry_trends(industry):
    """
    Get current trends and news for a specific industry using OpenAI.
    
    Args:
        industry (str): The industry to get trends for
    
    Returns:
        dict: Industry trends and news
    """
    client = get_openai_client()
    
    prompt = f"""
    Provide an overview of current trends and developments in the {industry} industry.
    
    Please provide a JSON response with the following structure:
    {{
        "trends": [
            {{
                "title": "Trend title",
                "description": "Description of the trend"
            }},
            ...
        ],
        "resources": [
            {{
                "title": "Resource title",
                "description": "Description of the resource"
            }},
            ...
        ]
    }}
    
    Limit to 3-5 major trends and 3-5 resources.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an industry analyst with knowledge of current market trends."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {
            "error": f"Failed to retrieve industry trends: {str(e)}",
            "trends": [{"title": "Trend data unavailable", "description": "Please try again later."}],
            "resources": []
        }

if __name__ == "__main__":
    app()
