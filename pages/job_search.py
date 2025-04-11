import streamlit as st
import pandas as pd
import plotly.express as px
from utils.openai_utils import get_openai_client
import json
from datetime import datetime
import random

def app():
    st.title("Job Search Assistant")
    
    # Initialize session state for saved jobs
    if "saved_jobs" not in st.session_state:
        st.session_state.saved_jobs = []
    
    # Initialize session state for job search history
    if "search_history" not in st.session_state:
        st.session_state.search_history = []
    
    # Tabs for different job search functions
    tabs = st.tabs(["Search Jobs", "Saved Jobs", "Job Application Tracker"])
    
    with tabs[0]:
        display_job_search()
    
    with tabs[1]:
        display_saved_jobs()
    
    with tabs[2]:
        display_job_tracker()

def display_job_search():
    """Display the job search interface."""
    st.header("Search for Jobs")
    
    # Search form
    with st.form("job_search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Default to user's current role if available
            default_role = st.session_state.user_profile.get("current_role", "")
            job_title = st.text_input("Job Title", value=default_role)
        
        with col2:
            # Default to user's industry if available
            default_industry = st.session_state.user_profile.get("industry", "")
            industry = st.text_input("Industry", value=default_industry)
        
        col1, col2 = st.columns(2)
        
        with col1:
            location = st.text_input("Location", placeholder="e.g., Remote, New York, London")
        
        with col2:
            experience_level = st.selectbox(
                "Experience Level",
                ["Entry Level", "Mid Level", "Senior", "Executive", "Any"]
            )
        
        search_button = st.form_submit_button("Search Jobs")
        
        if search_button and job_title:
            # Add search to history
            st.session_state.search_history.append({
                "job_title": job_title,
                "industry": industry,
                "location": location,
                "experience_level": experience_level,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Perform job search
            with st.spinner("Searching for jobs..."):
                jobs = search_jobs(job_title, industry, location, experience_level)
                
                if "error" in jobs:
                    st.error(jobs["error"])
                else:
                    display_job_results(jobs)
    
    # Recent searches
    if st.session_state.search_history:
        with st.expander("Recent Searches"):
            # Display recent searches in a dataframe
            searches_df = pd.DataFrame(st.session_state.search_history)
            st.dataframe(searches_df[["job_title", "industry", "location", "timestamp"]])
            
            # Option to clear search history
            if st.button("Clear Search History"):
                st.session_state.search_history = []
                st.rerun()
    
    # Job search tips
    with st.expander("Job Search Tips"):
        st.markdown("""
        ### Effective Job Search Strategies
        
        1. **Tailor your resume for each application**
           - Highlight relevant skills and experience for the specific role
           - Use keywords from the job description
        
        2. **Leverage your network**
           - Reach out to contacts in target companies
           - Attend industry events and join professional groups
        
        3. **Use multiple job platforms**
           - Industry-specific job boards
           - Company career pages
           - LinkedIn, Indeed, Glassdoor, etc.
        
        4. **Research companies before applying**
           - Understand the company culture and values
           - Prepare targeted cover letters addressing company needs
        
        5. **Track your applications**
           - Keep a spreadsheet of all applications, responses, and follow-ups
           - Follow up if you don't hear back within 1-2 weeks
        
        6. **Prepare for interviews thoroughly**
           - Research common interview questions
           - Practice with the Interview Preparation tool in this app
        """)

def display_job_results(jobs_data):
    """
    Display job search results.
    
    Args:
        jobs_data (dict): Job search results data
    """
    jobs = jobs_data.get("jobs", [])
    
    if not jobs:
        st.info("No jobs found matching your criteria. Try broadening your search.")
        return
    
    # Display jobs
    st.subheader(f"Found {len(jobs)} matching jobs")
    
    for i, job in enumerate(jobs):
        with st.expander(f"{job.get('title')} - {job.get('company')}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Location:** {job.get('location', 'Not specified')}")
                st.markdown(f"**Type:** {job.get('job_type', 'Not specified')}")
                
                if job.get('salary_range'):
                    st.markdown(f"**Salary Range:** {job.get('salary_range')}")
                
                st.markdown(f"**Posted:** {job.get('posted_date', 'Not specified')}")
                st.markdown("---")
                st.markdown("**Job Description:**")
                st.write(job.get('description', 'No description available.'))
                
                # Skills match
                if "skills_match" in job:
                    st.markdown("**Skills Match:**")
                    user_skills = st.session_state.user_profile.get("skills", [])
                    matching_skills = set(job["skills_match"]).intersection(set(user_skills))
                    
                    if matching_skills:
                        st.markdown("Your matching skills:")
                        for skill in matching_skills:
                            st.markdown(f"- {skill}")
                    else:
                        st.info("No direct skill matches found.")
            
            with col2:
                # Add to saved jobs button
                if st.button("Save Job", key=f"save_{i}"):
                    save_job(job)
                    st.success("Job saved!")
                
                # Apply button
                st.markdown(f"[Apply Now](https://example.com/jobs/{i}) 🔗")
                
                # Company info
                st.markdown("**About the Company:**")
                st.write(job.get('company_description', 'No company information available.'))

def display_saved_jobs():
    """Display the user's saved jobs."""
    st.header("Saved Jobs")
    
    saved_jobs = st.session_state.saved_jobs
    
    if not saved_jobs:
        st.info("You haven't saved any jobs yet. Use the Search tab to find and save jobs.")
        return
    
    # Display saved jobs
    for i, job in enumerate(saved_jobs):
        with st.expander(f"{job.get('title')} - {job.get('company')}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Location:** {job.get('location', 'Not specified')}")
                st.markdown(f"**Type:** {job.get('job_type', 'Not specified')}")
                
                if job.get('salary_range'):
                    st.markdown(f"**Salary Range:** {job.get('salary_range')}")
                
                st.markdown(f"**Posted:** {job.get('posted_date', 'Not specified')}")
                st.markdown(f"**Saved on:** {job.get('saved_date', 'Unknown')}")
                st.markdown("---")
                st.markdown("**Job Description:**")
                st.write(job.get('description', 'No description available.'))
            
            with col2:
                # Remove from saved jobs button
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.saved_jobs.pop(i)
                    st.rerun()
                
                # Apply button
                st.markdown(f"[Apply Now](https://example.com/jobs/{i}) 🔗")
                
                # Show status if tracked
                for application in st.session_state.get("job_applications", []):
                    if are_jobs_same(job, application):
                        st.success(f"Status: {application.get('status', 'Applied')}")
                        break
                else:
                    # Add to job tracker button
                    if st.button("Track Application", key=f"track_{i}"):
                        add_to_job_tracker(job)
                        st.success("Added to job tracker!")
                        st.rerun()

def display_job_tracker():
    """Display the job application tracker."""
    st.header("Job Application Tracker")
    
    # Initialize job applications in session state if needed
    if "job_applications" not in st.session_state:
        st.session_state.job_applications = []
    
    # Add new application form
    with st.expander("Add New Application"):
        with st.form("new_application_form"):
            company = st.text_input("Company Name")
            job_title = st.text_input("Job Title")
            application_date = st.date_input("Application Date")
            status = st.selectbox(
                "Status",
                ["Applied", "Screening", "Interview", "Technical Test", "Offer", "Rejected", "Accepted"]
            )
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Add Application"):
                if company and job_title:
                    new_application = {
                        "company": company,
                        "title": job_title,
                        "application_date": application_date.strftime("%Y-%m-%d"),
                        "status": status,
                        "notes": notes,
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.job_applications.append(new_application)
                    st.success("Application added!")
                    st.rerun()
                else:
                    st.error("Company name and job title are required!")
    
    # Display application statistics
    applications = st.session_state.job_applications
    
    if applications:
        col1, col2 = st.columns(2)
        
        with col1:
            # Count applications by status
            status_counts = {}
            for app in applications:
                status = app.get("status", "Applied")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Create a DataFrame for the status counts
            status_df = pd.DataFrame({
                "Status": list(status_counts.keys()),
                "Count": list(status_counts.values())
            })
            
            # Create a bar chart
            fig = px.bar(
                status_df,
                x="Status",
                y="Count",
                color="Status",
                title="Application Status Overview"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Calculate metrics
            total_applications = len(applications)
            active_applications = sum(1 for app in applications if app.get("status") not in ["Rejected", "Accepted"])
            response_rate = sum(1 for app in applications if app.get("status") != "Applied") / total_applications if total_applications > 0 else 0
            
            # Display metrics
            st.metric("Total Applications", total_applications)
            st.metric("Active Applications", active_applications)
            st.metric("Response Rate", f"{response_rate:.0%}")
        
        # Display applications table
        st.subheader("Your Applications")
        
        # Create an applications table
        apps_df = pd.DataFrame(applications)
        
        # Sort by application date (most recent first)
        if not apps_df.empty and "application_date" in apps_df.columns:
            apps_df["application_date"] = pd.to_datetime(apps_df["application_date"])
            apps_df = apps_df.sort_values(by="application_date", ascending=False)
        
        # Display applications as an interactive table
        if not apps_df.empty:
            # Show only certain columns in the table
            display_columns = ["company", "title", "application_date", "status", "last_updated"]
            available_columns = [col for col in display_columns if col in apps_df.columns]
            
            # Rename columns for better display
            column_map = {
                "company": "Company",
                "title": "Job Title",
                "application_date": "Applied On",
                "status": "Status",
                "last_updated": "Last Updated"
            }
            
            # Create the display dataframe
            display_df = apps_df[available_columns].rename(columns=column_map)
            st.dataframe(display_df, use_container_width=True)
            
            # Application details
            selected_index = st.selectbox(
                "Select application to view/edit details:", 
                range(len(applications)),
                format_func=lambda i: f"{applications[i].get('company')} - {applications[i].get('title')}"
            )
            
            display_application_details(selected_index)
        else:
            st.info("No applications to display.")
    else:
        st.info("No job applications tracked yet. Add an application or track from your saved jobs.")
        
        # Sample data option
        if st.button("Add Sample Data for Demo"):
            add_sample_applications()
            st.rerun()

def display_application_details(index):
    """
    Display details for a single job application with ability to edit.
    
    Args:
        index (int): Index of the application in the session state list
    """
    applications = st.session_state.job_applications
    
    if 0 <= index < len(applications):
        application = applications[index]
        
        with st.expander("Application Details", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Company:** {application.get('company')}")
                st.markdown(f"**Job Title:** {application.get('title')}")
                st.markdown(f"**Applied On:** {application.get('application_date')}")
                st.markdown(f"**Current Status:** {application.get('status')}")
            
            with col2:
                # Update status
                new_status = st.selectbox(
                    "Update Status:",
                    ["Applied", "Screening", "Interview", "Technical Test", "Offer", "Rejected", "Accepted"],
                    index=["Applied", "Screening", "Interview", "Technical Test", "Offer", "Rejected", "Accepted"].index(application.get("status", "Applied"))
                )
                
                if new_status != application.get("status") and st.button("Update Status"):
                    applications[index]["status"] = new_status
                    applications[index]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success("Status updated!")
                    st.rerun()
            
            # Notes section
            st.subheader("Notes")
            new_notes = st.text_area("Application Notes", value=application.get("notes", ""))
            
            if new_notes != application.get("notes", "") and st.button("Update Notes"):
                applications[index]["notes"] = new_notes
                applications[index]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success("Notes updated!")
                st.rerun()
            
            # Interview preparation
            if application.get("status") in ["Screening", "Interview", "Technical Test"]:
                st.markdown("### Prepare for Your Interview")
                st.markdown("""
                It looks like you're in the interview process! Would you like to prepare for your interview?
                """)
                
                if st.button("Prepare for Interview"):
                    st.switch_page("pages/interview_prep.py")
            
            # Delete application
            if st.button("Delete This Application", key=f"delete_{index}"):
                if st.checkbox("Confirm deletion?", key=f"confirm_{index}"):
                    applications.pop(index)
                    st.success("Application deleted!")
                    st.rerun()

# Utility functions

def search_jobs(job_title, industry=None, location=None, experience_level=None):
    """
    Search for jobs based on criteria using OpenAI to generate mock results.
    
    Args:
        job_title (str): The job title to search for
        industry (str): Optional industry filter
        location (str): Optional location filter
        experience_level (str): Optional experience level filter
    
    Returns:
        dict: Job search results
    """
    try:
        client = get_openai_client()
        # ... existing code ...
    except Exception as e:
        if "insufficient_quota" in str(e):
            return {
                "error": "API quota exceeded. Please check your OpenAI billing.",
                "jobs": [{
                    "title": "Sample Job - API Quota Exceeded",
                    "company": "Your OpenAI Account",
                    "location": "platform.openai.com/account",
                    "description": "Please check your OpenAI billing and quota",
                    "salary_range": "N/A"
                }]
            }
    
    # Get user skills for matching
    user_skills = st.session_state.user_profile.get("skills", [])
    skills_str = ", ".join(user_skills) if user_skills else "None provided"
    
    prompt = f"""
    Generate realistic job listings for "{job_title}" jobs
    {f'in the {industry} industry' if industry else ''}
    {f'in {location}' if location else ''}
    {f'at {experience_level} experience level' if experience_level and experience_level != 'Any' else ''}.
    
    The user has the following skills: {skills_str}
    
    Please provide a JSON response with the following structure:
    {{
        "jobs": [
            {{
                "title": "Job Title",
                "company": "Company Name",
                "location": "Job Location",
                "job_type": "Full-time/Part-time/Contract",
                "salary_range": "Salary range if available",
                "description": "Job description",
                "company_description": "Brief company info",
                "required_skills": ["Skill 1", "Skill 2", ...],
                "skills_match": ["User skill that matches", ...],
                "posted_date": "Posted date (recent)"
            }},
            ...
        ]
    }}
    
    Provide 5-8 realistic job listings. For the skills_match field, include any of the user's skills that match the job requirements.
    All job listings should be different positions at different companies. Make the job descriptions realistic and detailed.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a job search engine that provides realistic job listings based on search criteria."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {
            "error": f"Failed to search for jobs: {str(e)}",
            "jobs": []
        }

def save_job(job):
    """
    Save a job to the user's saved jobs list.
    
    Args:
        job (dict): The job to save
    """
    # Add saved date
    job["saved_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if already saved
    for saved_job in st.session_state.saved_jobs:
        if are_jobs_same(job, saved_job):
            return
    
    # Add to saved jobs
    st.session_state.saved_jobs.append(job)

def add_to_job_tracker(job):
    """
    Add a job to the job application tracker.
    
    Args:
        job (dict): The job to add to the tracker
    """
    # Initialize job applications if needed
    if "job_applications" not in st.session_state:
        st.session_state.job_applications = []
    
    # Create a new application entry
    new_application = {
        "company": job.get("company", "Unknown Company"),
        "title": job.get("title", "Unknown Position"),
        "application_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "Applied",
        "notes": f"Applied via AI Career Advisor\n\nJob Description:\n{job.get('description', 'No description')}",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Check if already tracked
    for app in st.session_state.job_applications:
        if are_jobs_same(job, app):
            return
    
    # Add to applications
    st.session_state.job_applications.append(new_application)

def are_jobs_same(job1, job2):
    """
    Check if two job entries refer to the same job.
    
    Args:
        job1 (dict): First job entry
        job2 (dict): Second job entry
    
    Returns:
        bool: True if they appear to be the same job
    """
    # Check company and title
    same_company = job1.get("company", "").lower() == job2.get("company", "").lower()
    same_title = job1.get("title", "").lower() == job2.get("title", "").lower()
    
    return same_company and same_title

def add_sample_applications():
    """Add sample job applications for demonstration purposes."""
    sample_applications = [
        {
            "company": "TechCorp Inc.",
            "title": "Senior Software Developer",
            "application_date": (datetime.now().date()).strftime("%Y-%m-%d"),
            "status": "Interview",
            "notes": "Had initial phone screening. Technical interview scheduled for next week.",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "company": "Data Analytics Partners",
            "title": "Data Scientist",
            "application_date": (datetime.now().date()).strftime("%Y-%m-%d"),
            "status": "Applied",
            "notes": "Applied through company website. Used referral from John Smith.",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "company": "Global Finance Solutions",
            "title": "Project Manager",
            "application_date": (datetime.now().date()).strftime("%Y-%m-%d"),
            "status": "Screening",
            "notes": "Received email to schedule initial phone screening.",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "company": "Innovative Healthcare",
            "title": "UX Designer",
            "application_date": (datetime.now().date()).strftime("%Y-%m-%d"),
            "status": "Rejected",
            "notes": "Received rejection email. Position filled internally.",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "company": "Enterprise Solutions Ltd.",
            "title": "Product Marketing Manager",
            "application_date": (datetime.now().date()).strftime("%Y-%m-%d"),
            "status": "Technical Test",
            "notes": "Completed first interview. Received marketing case study to complete within 5 days.",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    if "job_applications" not in st.session_state:
        st.session_state.job_applications = []
    
    st.session_state.job_applications.extend(sample_applications)

if __name__ == "__main__":
    app()
