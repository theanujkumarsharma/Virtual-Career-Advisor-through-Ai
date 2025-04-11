import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.openai_utils import get_openai_client
import json

# Sample job market data - In a real application, this would come from an API or database
SAMPLE_JOB_TRENDS = {
    "Technology": {
        "growing_roles": ["Data Scientist", "AI Engineer", "Cloud Architect", "DevOps Engineer", "Cybersecurity Specialist"],
        "declining_roles": ["Basic Web Developer", "System Administrator", "Desktop Support"],
        "top_skills": ["Python", "AWS", "Machine Learning", "Kubernetes", "React", "JavaScript", "Azure", "Data Analysis"]
    },
    "Healthcare": {
        "growing_roles": ["Telemedicine Physician", "Health Informatics Specialist", "Nurse Practitioner", "Mental Health Counselor"],
        "declining_roles": ["Medical Transcriptionist", "Medical Records Clerk"],
        "top_skills": ["Telehealth", "Electronic Health Records", "Patient Care", "Healthcare Management", "Medical Coding"]
    },
    "Finance": {
        "growing_roles": ["Financial Analyst", "Risk Manager", "FinTech Developer", "ESG Specialist", "Financial Planner"],
        "declining_roles": ["Bank Teller", "Data Entry Clerk", "Loan Processor"],
        "top_skills": ["Financial Analysis", "Python", "SQL", "Risk Assessment", "Blockchain", "Regulatory Compliance"]
    },
    "Education": {
        "growing_roles": ["Instructional Designer", "EdTech Specialist", "Virtual Tutor", "Learning Experience Designer"],
        "declining_roles": ["Traditional Textbook Publisher", "Library Assistant"],
        "top_skills": ["Online Learning Platforms", "Digital Curriculum Development", "Educational Technology", "Student Engagement"]
    },
    "Manufacturing": {
        "growing_roles": ["Automation Engineer", "Supply Chain Analyst", "IoT Specialist", "Robotics Technician"],
        "declining_roles": ["Assembly Line Worker", "Quality Control Inspector"],
        "top_skills": ["Lean Manufacturing", "Automation", "Six Sigma", "IoT", "Supply Chain Management", "CAD"]
    },
    "Retail": {
        "growing_roles": ["E-commerce Manager", "Digital Marketing Specialist", "Supply Chain Coordinator", "Customer Experience Manager"],
        "declining_roles": ["Cashier", "In-store Sales Associate", "Inventory Clerk"],
        "top_skills": ["E-commerce Platforms", "Digital Marketing", "Inventory Management", "Customer Experience", "Omnichannel Strategy"]
    }
}

def get_job_market_insights(industry):
    """
    Get job market insights for a specific industry.
    
    Args:
        industry (str): The industry to get insights for
    
    Returns:
        dict: Job market insights data
    """
    if industry in SAMPLE_JOB_TRENDS:
        return SAMPLE_JOB_TRENDS[industry]
    else:
        # Default to Technology if industry not found
        return SAMPLE_JOB_TRENDS["Technology"]

def get_skill_gap_analysis(user_skills, target_role, industry="Technology"):
    """
    Analyze the gap between user's skills and those required for a target role.
    
    Args:
        user_skills (list): List of user's current skills
        target_role (str): The role the user is targeting
        industry (str): The industry of interest
    
    Returns:
        dict: Skill gap analysis results
    """
    client = get_openai_client()
    
    # Convert skills list to comma-separated string
    skills_str = ", ".join(user_skills) if user_skills else "None provided"
    
    prompt = f"""
    Perform a skill gap analysis for someone with the following skills looking to become a {target_role} in the {industry} industry.
    
    Current skills: {skills_str}
    
    Please provide a JSON response with the following structure:
    {{
        "required_skills": ["Skill 1", "Skill 2", ...],
        "matching_skills": ["Skill 1", "Skill 2", ...],
        "missing_skills": ["Skill 1", "Skill 2", ...],
        "skill_acquisition_tips": [
            {{
                "skill": "Skill name",
                "learning_resources": ["Resource 1", "Resource 2", ...],
                "estimated_time": "Estimated time to learn"
            }},
            ...
        ],
        "match_percentage": 0-100
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in career development and skills analysis."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {
            "error": f"Failed to perform skill gap analysis: {str(e)}",
            "required_skills": [],
            "matching_skills": [],
            "missing_skills": ["Unable to analyze skills"],
            "skill_acquisition_tips": [],
            "match_percentage": 0
        }

def generate_skills_radar_chart(user_skills, required_skills):
    """
    Generate a radar chart comparing user skills to required skills.
    
    Args:
        user_skills (list): List of user's current skills
        required_skills (list): List of required skills for target role
    
    Returns:
        plotly.graph_objects.Figure: Radar chart figure
    """
    # Create a set of all skills
    all_skills = list(set(user_skills + required_skills))
    
    # Create values for radar chart (1 if skill present, 0 if not)
    user_values = [1 if skill in user_skills else 0 for skill in all_skills]
    required_values = [1 if skill in required_skills else 0 for skill in all_skills]
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=user_values,
        theta=all_skills,
        fill='toself',
        name='Your Skills'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=required_values,
        theta=all_skills,
        fill='toself',
        name='Required Skills'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="Skills Comparison"
    )
    
    return fig

def generate_job_growth_chart(industry_data):
    """
    Generate a bar chart showing job growth trends.
    
    Args:
        industry_data (dict): Industry job trend data
    
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    growing_roles = industry_data.get("growing_roles", [])
    declining_roles = industry_data.get("declining_roles", [])
    
    # Create sample growth rates (would come from real data in production)
    growing_rates = np.linspace(5, 25, len(growing_roles))
    declining_rates = np.linspace(-15, -5, len(declining_roles))
    
    # Combine data
    roles = growing_roles + declining_roles
    rates = list(growing_rates) + list(declining_rates)
    colors = ['green'] * len(growing_roles) + ['red'] * len(declining_roles)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Role': roles,
        'Growth Rate (%)': rates,
        'Trend': ['Growing'] * len(growing_roles) + ['Declining'] * len(declining_roles)
    })
    
    # Create bar chart
    fig = px.bar(
        df, 
        x='Role', 
        y='Growth Rate (%)', 
        color='Trend',
        color_discrete_map={'Growing': 'green', 'Declining': 'red'},
        title="Job Growth Trends"
    )
    
    fig.update_layout(xaxis_tickangle=-45)
    
    return fig

def generate_salary_range_chart(job_titles):
    """
    Generate a box plot showing salary ranges for different job titles.
    
    Args:
        job_titles (list): List of job titles to compare
    
    Returns:
        plotly.graph_objects.Figure: Box plot figure
    """
    # Sample data - in a production app, this would come from a salary API or database
    np.random.seed(42)  # For reproducible results
    
    # Generate random salary data for each job title
    data = []
    for job in job_titles:
        # Base salary varies by job
        if "Senior" in job or "Architect" in job:
            base = 120000
            spread = 40000
        elif "Engineer" in job or "Developer" in job:
            base = 90000
            spread = 30000
        else:
            base = 70000
            spread = 25000
        
        # Generate sample data points
        salaries = np.random.normal(base, spread/3, 50)
        for salary in salaries:
            data.append({
                'Job Title': job,
                'Salary': max(30000, int(salary))  # Ensure no negative salaries
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create box plot
    fig = px.box(
        df, 
        x='Job Title', 
        y='Salary',
        title="Salary Ranges by Job Title",
        points="all"
    )
    
    fig.update_layout(xaxis_tickangle=-45)
    
    return fig
