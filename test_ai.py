import sys
import os
sys.path.append(os.path.dirname(__file__))

from ai_service import analyze_transition_risk

form_data = {
    'current_job_title': 'Software Developer',
    'current_company': 'ABC',
    'notice_period': '60',
    'resignation_submitted': 'yes',
    'new_company': 'XYZ',
    'new_job_title': 'AI Engineer',
    'offer_received': 'yes',
    'offer_type': 'Verbal Offer',
    'joining_date_confirmed': 'no',
    'background_verification': 'in_progress',
    'medical_verification': 'not_applicable',
    'is_conditional': 'yes',
    'subject_to_bg': 'yes'
}

print("Testing AI Service...")
result = analyze_transition_risk(form_data)
print(result)
