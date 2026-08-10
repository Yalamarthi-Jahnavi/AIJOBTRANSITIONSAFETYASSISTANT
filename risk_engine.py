def calculate_score(form_data):
    """
    Calculate a rule-based risk score from 0-100 based on the job transition form data.
    """
    score = 50 # Base score
    
    # 1. Offer Status Rules
    offer_type = form_data.get('offer_type', '')
    if offer_type == 'Offer Letter':
        score += 15
    elif offer_type == 'Appointment Letter':
        score += 10
    elif offer_type == 'Email Confirmation':
        score += 5
    elif offer_type == 'Verbal Offer':
        score -= 25
        
    # 2. Joining Date Rules
    joining_confirmed = form_data.get('joining_date_confirmed')
    if joining_confirmed == 'yes':
        score += 15
    elif joining_confirmed == 'no':
        score -= 20
        
    # 3. Background Verification Rules
    bg_status = form_data.get('background_verification', '')
    if bg_status == 'completed':
        score += 20
    elif bg_status == 'in_progress':
        score += 5
    elif bg_status == 'not_started' or bg_status == 'pending':
        score -= 10
    elif bg_status == 'failed':
        score -= 50
        
    # 4. Medical Verification Rules
    med_status = form_data.get('medical_verification', '')
    if med_status == 'completed':
        score += 5
    elif med_status == 'failed':
        score -= 20
        
    # 5. Additional Conditions
    if form_data.get('is_conditional') == 'yes':
        score -= 15
    if form_data.get('subject_to_bg') == 'yes' and bg_status != 'completed':
        score -= 10
        
    # 6. Resignation Timing
    if form_data.get('resignation_submitted') == 'yes':
        if bg_status != 'completed' or offer_type == 'Verbal Offer' or joining_confirmed == 'no':
            score -= 20
        else:
            score -= 5 # Resigned but everything is somewhat fine, still a slight risk until joined
    
    # Normalize score between 0 and 100
    score = max(0, min(100, score))
    
    return score

def get_risk_level(score):
    """
    Map score to risk level strings.
    """
    if score >= 80:
        return 'SAFE'
    elif score >= 60:
        return 'MODERATE RISK'
    elif score >= 40:
        return 'HIGH RISK'
    else:
        return 'VERY HIGH RISK'

def generate_safety_checklist(form_data):
    """
    Generate a checklist status based on form inputs.
    """
    checklist = [
        {"item": "Written offer received", "completed": form_data.get('offer_type') in ['Offer Letter', 'Appointment Letter']},
        {"item": "Joining date confirmed", "completed": form_data.get('joining_date_confirmed') == 'yes'},
        {"item": "Background verification completed", "completed": form_data.get('background_verification') == 'completed'},
        {"item": "Medical verification completed", "completed": form_data.get('medical_verification') in ['completed', 'not_applicable']},
        {"item": "Employment conditions understood", "completed": form_data.get('is_conditional') == 'no'},
        {"item": "Resignation timing checked", "completed": form_data.get('resignation_submitted') == 'no' or form_data.get('background_verification') == 'completed'}
    ]
    
    completed_count = sum(1 for c in checklist if c['completed'])
    total_count = len(checklist)
    percentage = int((completed_count / total_count) * 100) if total_count > 0 else 0
    
    return {
        "items": checklist,
        "completed": completed_count,
        "total": total_count,
        "percentage": percentage
    }
