import os
from mistralai.client import Mistral
import json
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure API
API_KEY = os.getenv("MISTRAL_API_KEY")

def clean_transition_risk_analysis(data):
    if not isinstance(data, dict):
        return data
        
    def to_string(val):
        if isinstance(val, dict):
            for k in ['risk', 'factor', 'action', 'summary', 'text', 'description']:
                if k in val and isinstance(val[k], str):
                    extra = []
                    for other_k, other_v in val.items():
                        if other_k != k and isinstance(other_v, (str, int)):
                            extra.append(f"{other_k}: {other_v}")
                    if extra:
                        return f"{val[k]} ({', '.join(extra)})"
                    return val[k]
            return ", ".join(f"{k}: {v}" for k, v in val.items() if isinstance(v, (str, int)))
        return str(val)

    for list_key in ['positive_factors', 'risk_factors', 'recommended_action', 'hr_questions']:
        if list_key in data:
            if isinstance(data[list_key], list):
                data[list_key] = [to_string(x) for x in data[list_key]]
            elif isinstance(data[list_key], dict):
                data[list_key] = [to_string(data[list_key])]
            else:
                # Handle single string
                data[list_key] = [str(data[list_key])]
                
    if 'risk_summary' in data:
        if isinstance(data['risk_summary'], list):
            data['risk_summary'] = " ".join(str(x) for x in data['risk_summary'])
        elif isinstance(data['risk_summary'], dict):
            data['risk_summary'] = to_string(data['risk_summary'])
            
    return data

def clean_offer_letter_analysis(data):
    if not isinstance(data, dict):
        return data
        
    def to_string(val):
        if isinstance(val, dict):
            for k in ['amount', 'base', 'summary', 'duration', 'text', 'value', 'description']:
                if k in val and isinstance(val[k], str):
                    extra = []
                    for other_k, other_v in val.items():
                        if other_k != k and isinstance(other_v, (str, int)):
                            extra.append(f"{other_k}: {other_v}")
                    if extra:
                        return f"{val[k]} ({', '.join(extra)})"
                    return val[k]
            return ", ".join(f"{k}: {v}" for k, v in val.items() if isinstance(v, (str, int)))
        elif isinstance(val, list):
            return ", ".join(to_string(x) for x in val)
        return str(val)

    for key in ['salary', 'notice_period', 'probation', 'background_verification_clause', 'location', 'joining_date']:
        if key in data:
            data[key] = to_string(data[key])
            
    for list_key in ['important_clauses', 'warning_clauses', 'missing_information', 'hr_questions']:
        if list_key in data and isinstance(data[list_key], list):
            cleaned_list = []
            for item in data[list_key]:
                if isinstance(item, dict):
                    summary = item.get('summary', item.get('action', ''))
                    risk = item.get('risk', item.get('purpose', item.get('impact', '')))
                    if summary and risk:
                        cleaned_list.append(f"{summary} (Note: {risk})")
                    elif summary:
                        cleaned_list.append(summary)
                    else:
                        cleaned_list.append(to_string(item))
                else:
                    cleaned_list.append(str(item))
            data[list_key] = cleaned_list
            
    return data

def is_api_configured():
    return bool(API_KEY and API_KEY != "your_mistral_api_key_here")

def get_client():
    if not is_api_configured():
        return None
    return Mistral(api_key=API_KEY)

def extract_json_from_text(text):
    text = text.strip()
    # Safer JSON extraction
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
    return json.loads(text)

def analyze_transition_risk(form_data):
    """
    Analyzes the job transition form data using Mistral API and returns a JSON structure.
    """
    client = get_client()
    if not client:
        return {
            "error": "AI API is not configured. Please add your MISTRAL_API_KEY to the .env file."
        }
        
    prompt = f"""
    Analyze the following job transition scenario for a professional moving from their current job to a new job.
    Identify the positive factors, risk factors, provide a short risk summary, and a recommended action.
    
    Current Job Title: {form_data.get('current_job_title')}
    Current Company: {form_data.get('current_company')}
    Notice Period: {form_data.get('notice_period')}
    Resignation Submitted: {form_data.get('resignation_submitted')}
    
    New Company: {form_data.get('new_company')}
    New Job Title: {form_data.get('new_job_title')}
    Offer Received: {form_data.get('offer_received')}
    Offer Type: {form_data.get('offer_type')}
    Joining Date Confirmed: {form_data.get('joining_date_confirmed')}
    Background Verification Status: {form_data.get('background_verification')}
    Medical Verification Status: {form_data.get('medical_verification')}
    Is Offer Conditional: {form_data.get('is_conditional')}
    Subject to Background Verification: {form_data.get('subject_to_bg')}
    
    Return the response ONLY as a valid JSON object with the following structure:
    {{
        "positive_factors": ["factor 1", "factor 2"],
        "risk_factors": ["risk 1", "risk 2"],
        "risk_summary": "A short 2-3 sentence summary of the situation.",
        "recommended_action": "Practical next steps.",
        "hr_questions": ["Specific question to ask the new company HR about the offer letter, joining date, or salary", "Specific question about post-resignation benefits", "Clarification on any identified risks"]
    }}
    Ensure the output is strictly valid JSON without markdown wrapping.
    """
    
    try:
        response = client.chat.complete(
            model="open-mistral-nemo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        text = response.choices[0].message.content
        return clean_transition_risk_analysis(extract_json_from_text(text))
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {
            "error": f"Failed to generate analysis: {str(e)}"
        }

def analyze_offer_letter(text):
    """
    Analyzes the extracted text from an offer letter using Mistral API.
    """
    client = get_client()
    if not client:
        return {
            "error": "AI API is not configured. Please add your MISTRAL_API_KEY to the .env file."
        }
        
    # Trim text to prevent token limit issues, roughly taking first 15000 chars
    truncated_text = text[:15000]
        
    prompt = f"""
    Analyze the following text extracted from an offer letter or employment contract.
    Extract key information and identify potential risks.
    
    Offer Letter Text:
    ---
    {truncated_text}
    ---
    
    Return the response ONLY as a valid JSON object with the following structure:
    {{
        "company_name": "Extracted name or Unknown",
        "job_title": "Extracted title or Unknown",
        "salary": "Extracted salary info or Not Mentioned",
        "joining_date": "Extracted date or Not Mentioned",
        "location": "Extracted location or Not Mentioned",
        "notice_period": "Extracted notice period or Not Mentioned",
        "probation": "Extracted probation info or Not Mentioned",
        "background_verification_clause": "Summary of BV clause if present, or Not Mentioned",
        "overall_document_risk": "LOW, MEDIUM, or HIGH",
        "important_clauses": ["Clause 1 summary", "Clause 2 summary"],
        "warning_clauses": ["Warning 1 summary", "Warning 2 summary"],
        "missing_information": ["Missing item 1", "Missing item 2"],
        "hr_questions": ["Question to ask HR 1", "Question to ask HR 2", "Question 3"]
    }}
    Ensure the output is strictly valid JSON without markdown wrapping.
    """
    
    try:
        response = client.chat.complete(
            model="open-mistral-nemo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content
        return clean_offer_letter_analysis(extract_json_from_text(response_text))
    except Exception as e:
        print(f"Offer Letter AI Analysis Error: {e}")
        return {
            "error": f"Failed to analyze document: {str(e)}"
        }
