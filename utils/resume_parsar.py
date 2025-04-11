import os
import re
import shutil
import PyPDF2
import io
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from typing import Optional, Dict, List
from docx import Document

# ======================
# NLTK INITIALIZATION
# ======================
def initialize_nltk():
    """Initialize NLTK with proper data download and path configuration"""
    # Create a custom directory for NLTK data in user's home folder
    nltk_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
    
    # Create directory if it doesn't exist
    os.makedirs(nltk_dir, exist_ok=True)
    
    # Set the NLTK data path to our custom directory
    nltk.data.path = [nltk_dir]
    
    # List of required NLTK packages
    required_packages = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
    
    for package in required_packages:
        try:
            # Check if the package is already downloaded
            nltk.data.find(f'tokenizers/{package}' if package == 'punkt' else 
                          f'taggers/{package}' if package == 'averaged_perceptron_tagger' else 
                          f'corpora/{package}')
        except LookupError:
            try:
                # Download the package to our custom directory
                nltk.download(package, download_dir=nltk_dir)
            except Exception as e:
                print(f"Error downloading {package}: {str(e)}")
                # Try one more time with fresh download
                try:
                    nltk.download(package, download_dir=nltk_dir, force=True)
                except Exception as e:
                    print(f"Failed to download {package} after retry: {str(e)}")
                    continue

# Initialize NLTK when module loads
initialize_nltk()

# ======================
# TEXT EXTRACTION
# ======================
def extract_resume_text(uploaded_file) -> Optional[str]:
    """
    Extract text content from a resume file with robust error handling.
    
    Args:
        uploaded_file: File-like object containing the resume
        
    Returns:
        str: Extracted text or None if error occurs
    """
    if uploaded_file is None:
        return None
    
    try:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_ext == '.pdf':
            return extract_from_pdf(uploaded_file)
        elif file_ext == '.docx':
            return extract_from_docx(uploaded_file)
        elif file_ext == '.txt':
            return uploaded_file.getvalue().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    except Exception as e:
        raise RuntimeError(f"Error processing resume: {str(e)}")

def extract_from_pdf(pdf_file) -> str:
    """
    Extract text from PDF with improved error handling.
    
    Args:
        pdf_file: File-like object containing PDF data
        
    Returns:
        str: Extracted and cleaned text
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.getvalue()))
        text = ""
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:  # Only add if text was extracted
                text += page_text + "\n"
        
        if not text.strip():
            raise ValueError("PDF appears to be image-based or contains no extractable text")
            
        return clean_text(text)
    except PyPDF2.PdfReadError:
        raise ValueError("Invalid or corrupted PDF file")
    except Exception as e:
        raise RuntimeError(f"PDF processing failed: {str(e)}")

def extract_from_docx(docx_file) -> str:
    """
    Extract text from DOCX files using python-docx.
    
    Args:
        docx_file: File-like object containing DOCX data
        
    Returns:
        str: Extracted and cleaned text
    """
    try:
        doc = Document(io.BytesIO(docx_file.getvalue()))
        full_text = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        
        return clean_text("\n".join(full_text))
    except Exception as e:
        raise RuntimeError(f"DOCX processing failed: {str(e)}")

# ======================
# TEXT PROCESSING
# ======================
def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text with enhanced processing.
    
    Args:
        text: Raw extracted text
        
    Returns:
        str: Cleaned and normalized text
    """
    if not text:
        return ""
    
    # Normalize line endings and remove excessive whitespace
    text = re.sub(r'\r\n', '\n', text)  # Standardize line endings
    text = re.sub(r'[ \t]+', ' ', text)  # Collapse multiple spaces/tabs
    text = re.sub(r'\n{3,}', '\n\n', text)  # Limit consecutive newlines
    
    # Remove special characters but preserve meaningful punctuation
    text = re.sub(r'[^\w\s.,;:()\-\'"/]', '', text)
    
    # Remove common resume artifacts
    text = re.sub(r'\b(?:page|phone|email|http[s]?://\S+)\b', '', text, flags=re.IGNORECASE)
    
    return text.strip()

# ======================
# SECTION EXTRACTION
# ======================
def extract_sections(resume_text: str) -> Dict[str, str]:
    """
    Extract common resume sections with improved pattern matching.
    
    Args:
        resume_text: Cleaned resume text
        
    Returns:
        dict: Dictionary with section names as keys and content as values
    """
    section_patterns = {
        'contact': r'(?i)(contact\s*information|personal\s*details)(.*?)(?=\n\s*\n|$)',
        'summary': r'(?i)(summary|profile|objective)(.*?)(?=\n\s*\n|$)',
        'education': r'(?i)(education|academic\s*background|qualifications)(.*?)(?=\n\s*\n|$)',
        'experience': r'(?i)(experience|work\s*history|employment)(.*?)(?=\n\s*\n|$)',
        'skills': r'(?i)(skills|technical\s*skills|competencies)(.*?)(?=\n\s*\n|$)',
        'projects': r'(?i)(projects|key\s*projects)(.*?)(?=\n\s*\n|$)',
        'certifications': r'(?i)(certifications|licenses)(.*?)(?=\n\s*\n|$)'
    }
    
    sections = {section: '' for section in section_patterns}
    sections['other'] = resume_text  # Default content
    
    for section, pattern in section_patterns.items():
        match = re.search(pattern, resume_text, re.DOTALL)
        if match:
            sections[section] = clean_section_content(match.group(2).strip())
            # Remove extracted section from 'other' content
            sections['other'] = sections['other'].replace(match.group(0), '')
    
    return sections

def clean_section_content(text: str) -> str:
    """Clean and normalize section content."""
    text = re.sub(r'^[\s•\-*\d.]+\s*', '', text, flags=re.MULTILINE)
    return text.strip()

# ======================
# SKILL EXTRACTION
# ======================
def extract_skills(resume_text: str) -> List[str]:
    """
    Extract skills from resume text with comprehensive matching.
    
    Args:
        resume_text: Text content of the resume
        
    Returns:
        list: Sorted list of unique skills found
    """
    # Enhanced skill database
    skill_db = {
        'Programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'swift', 'kotlin'],
        'Web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'express', 'spring'],
        'Data': ['sql', 'mysql', 'postgresql', 'mongodb', 'hadoop', 'spark', 'pandas', 'numpy', 'pytorch', 'tensorflow'],
        'Cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'ci/cd'],
        'Tools': ['git', 'linux', 'bash', 'jira', 'tableau', 'power bi', 'excel', 'selenium'],
        'Methodologies': ['agile', 'scrum', 'kanban', 'devops', 'tdd', 'oop', 'microservices'],
        'Soft Skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking']
    }
    
    # Get skills from dedicated section first
    sections = extract_sections(resume_text)
    skill_text = sections['skills'].lower() if sections['skills'] else resume_text.lower()
    
    found_skills = set()
    
    # Match against skill database
    for category, skills in skill_db.items():
        for skill in skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', skill_text):
                found_skills.add(skill.title())
    
    # Additional pattern matching for skills not in database
    skill_patterns = [
        r'\b([A-Z][a-z]*[ /-]+[A-Z][a-z]*)\b',  # Matches "Machine Learning" style terms
        r'\b[A-Z]{2,}\b',  # Matches acronyms like "AWS", "SQL"
    ]
    
    for pattern in skill_patterns:
        for match in re.finditer(pattern, resume_text):
            potential_skill = match.group(1) if match.groups() else match.group(0)
            if len(potential_skill) > 2:  # Filter out very short matches
                found_skills.add(potential_skill.lower())
    
    return sorted(found_skills, key=lambda x: (x not in skill_text, x))  # Sort by relevance

def extract_experience_duration(resume_text: str) -> Optional[int]:
    """
    Estimate total years of experience from resume text.
    
    Args:
        resume_text: Text content of the resume
        
    Returns:
        int: Estimated total years of experience or None if not found
    """
    # Look for duration patterns in experience section
    sections = extract_sections(resume_text)
    exp_text = sections['experience']
    
    # Pattern for "Jan 2020 - Present (3 years 5 months)" style
    duration_pattern = r'(\d+)\s*years?'
    matches = re.findall(duration_pattern, exp_text, re.IGNORECASE)
    
    if matches:
        return max(map(int, matches))  # Return the longest duration found
    
    return None