import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import string
import os

# Download required NLTK data if not already present
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

def extract_keywords(text, top_n=10):
    """
    Extract the most frequent keywords from text after removing stopwords.
    
    Args:
        text (str): The text to analyze
        top_n (int): Number of top keywords to return
    
    Returns:
        list: List of (keyword, frequency) tuples
    """
    if not text:
        return []
    
    # Tokenize text
    tokens = word_tokenize(text.lower())
    
    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words and token not in string.punctuation and len(token) > 2]
    
    # Count frequencies
    word_freq = Counter(tokens)
    
    # Return top N keywords
    return word_freq.most_common(top_n)

def analyze_text_sentiment(text):
    """
    Simple rule-based sentiment analysis for text.
    
    Args:
        text (str): Text to analyze
    
    Returns:
        dict: Sentiment analysis results
    """
    # This is a very simplistic approach - in a real app, we'd use NLTK's sentiment analyzers
    # or a pre-trained model, but this gives us a basic example
    
    positive_words = {
        'good', 'great', 'excellent', 'outstanding', 'exceptional', 'amazing', 'fantastic',
        'wonderful', 'positive', 'skilled', 'proficient', 'experienced', 'expert', 'accomplished',
        'successful', 'impressive', 'stellar', 'excellent', 'strong', 'innovative', 'creative',
        'talented', 'dedicated', 'committed', 'professional', 'enthusiastic', 'passionate',
        'achieve', 'achievement', 'success', 'improve', 'improvement', 'growth', 'develop'
    }
    
    negative_words = {
        'bad', 'poor', 'terrible', 'horrible', 'awful', 'inadequate', 'insufficient',
        'limited', 'weak', 'lacking', 'mediocre', 'subpar', 'unsuccessful', 'failure',
        'failed', 'struggle', 'struggled', 'problem', 'issue', 'concern', 'difficulty',
        'difficult', 'challenging', 'unfortunately', 'disappointment', 'disappointing'
    }
    
    # Tokenize and convert to lowercase
    tokens = word_tokenize(text.lower())
    
    # Count positive and negative words
    positive_count = sum(1 for token in tokens if token in positive_words)
    negative_count = sum(1 for token in tokens if token in negative_words)
    
    # Calculate sentiment score (-1 to 1)
    total = positive_count + negative_count
    sentiment_score = 0
    if total > 0:
        sentiment_score = (positive_count - negative_count) / total
    
    # Determine overall sentiment
    if sentiment_score > 0.1:
        sentiment = "positive"
    elif sentiment_score < -0.1:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "score": sentiment_score,
        "sentiment": sentiment,
        "positive_words": positive_count,
        "negative_words": negative_count
    }

def compare_job_descriptions(description1, description2):
    """
    Compare two job descriptions to find similarities and differences.
    
    Args:
        description1 (str): First job description
        description2 (str): Second job description
    
    Returns:
        dict: Comparison results
    """
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    
    tokens1 = word_tokenize(description1.lower())
    tokens1 = [token for token in tokens1 if token not in stop_words and token not in string.punctuation and len(token) > 2]
    
    tokens2 = word_tokenize(description2.lower())
    tokens2 = [token for token in tokens2 if token not in stop_words and token not in string.punctuation and len(token) > 2]
    
    # Find unique terms in each description
    set1 = set(tokens1)
    set2 = set(tokens2)
    
    common = set1.intersection(set2)
    unique1 = set1 - set2
    unique2 = set2 - set1
    
    # Calculate Jaccard similarity
    jaccard = len(common) / len(set1.union(set2)) if (set1 or set2) else 0
    
    return {
        "similarity_score": jaccard,
        "common_terms": list(common),
        "unique_to_first": list(unique1),
        "unique_to_second": list(unique2)
    }

def extract_action_verbs(text):
    """
    Extract action verbs from text, useful for resume analysis.
    
    Args:
        text (str): Text to analyze
    
    Returns:
        list: List of action verbs found
    """
    # Common action verbs used in resumes
    action_verbs = {
        'achieved', 'implemented', 'developed', 'managed', 'led', 'created', 'designed',
        'coordinated', 'organized', 'supervised', 'trained', 'researched', 'analyzed',
        'evaluated', 'improved', 'increased', 'decreased', 'reduced', 'negotiated',
        'established', 'launched', 'delivered', 'generated', 'produced', 'streamlined',
        'optimized', 'maintained', 'directed', 'oversaw', 'guided', 'facilitated',
        'prepared', 'presented', 'authored', 'initiated', 'pioneered', 'spearheaded'
    }
    
    # Tokenize and convert to lowercase
    tokens = word_tokenize(text.lower())
    
    # Find action verbs
    found_verbs = [token for token in tokens if token in action_verbs]
    
    # Return unique verbs
    return list(set(found_verbs))
