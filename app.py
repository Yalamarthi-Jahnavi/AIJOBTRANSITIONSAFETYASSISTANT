import os
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, save_assessment, get_assessments, save_document_analysis, get_documents, create_user, get_user_by_username
from utils import calculate_notice_dates, calculate_employment_gap
from risk_engine import calculate_score, get_risk_level, generate_safety_checklist
from ai_service import analyze_transition_risk, analyze_offer_letter
from document_analyzer import extract_text

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_dev_key')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        
        if create_user(username, hashed_password):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose a different one.', 'error')
            
    return render_template('register.html', active_page='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('login.html', active_page='login')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('last_assessment', None) # Clear dashboard data
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    # Show the last assessment if it exists in session
    assessment_data = session.get('last_assessment')
    if assessment_data:
        score = assessment_data.get('score', 0)
        risk_level = assessment_data.get('risk_level', 'UNKNOWN')
        checklist = assessment_data.get('checklist', {'items': []})
        ai_analysis = assessment_data.get('ai_analysis')
        return render_template('dashboard.html', active_page='dashboard', 
                               assessment_data=True, score=score, 
                               risk_level=risk_level, checklist=checklist, 
                               ai_analysis=ai_analysis)
    
    return render_template('dashboard.html', active_page='dashboard', assessment_data=False)

@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        # Calculate risk and checklist
        score = calculate_score(form_data)
        risk_level = get_risk_level(score)
        checklist = generate_safety_checklist(form_data)
        
        # Save to DB
        form_data['safety_score'] = score
        form_data['risk_level'] = risk_level
        
        # Call AI for analysis
        ai_analysis = analyze_transition_risk(form_data)
        if not ai_analysis.get('error'):
            form_data['recommendation'] = ai_analysis.get('risk_summary', '')
            
        save_assessment(form_data)
        
        # Store in session for dashboard
        session['last_assessment'] = {
            'score': score,
            'risk_level': risk_level,
            'checklist': checklist,
            'ai_analysis': ai_analysis,
            'form_data': form_data
        }
        
        # Clear demo data
        if 'demo_data' in session:
            session.pop('demo_data')
            
        flash('Assessment completed successfully.', 'success')
        return redirect(url_for('index'))
        
    # GET request
    demo_data = session.get('demo_data')
    return render_template('assessment.html', active_page='assessment', demo_data=demo_data)

@app.route('/analyzer', methods=['GET', 'POST'])
@login_required
def analyzer():
    if request.method == 'POST':
        if 'offer_letter' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
            
        file = request.files['offer_letter']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text
            text, error = extract_text(filepath)
            
            # Delete file after extraction to protect privacy
            try:
                os.remove(filepath)
            except:
                pass
                
            if error:
                flash(error, 'error')
                return redirect(request.url)
                
            # Analyze text
            analysis = analyze_offer_letter(text)
            
            if not analysis.get('error'):
                # Save to history
                save_document_analysis(
                    filename=filename,
                    company=analysis.get('company_name', 'Unknown'),
                    analysis=json.dumps(analysis),
                    risk_level=analysis.get('overall_document_risk', 'UNKNOWN')
                )
                flash('Document analyzed successfully.', 'success')
            else:
                flash(analysis.get('error'), 'error')
                
            return render_template('analyzer.html', active_page='analyzer', analysis=analysis)

    return render_template('analyzer.html', active_page='analyzer')

@app.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculator():
    if request.method == 'POST':
        resignation_date = request.form.get('resignation_date')
        notice_period = request.form.get('notice_period')
        joining_date = request.form.get('joining_date')
        
        result = calculate_notice_dates(resignation_date, notice_period)
        gap_result = None
        
        if result and joining_date:
            gap_result = calculate_employment_gap(result['last_working_day_date'], joining_date)
            
        if not result:
            flash("Error calculating dates. Please check your inputs.", 'error')
            
        return render_template('calculator.html', active_page='calculator', 
                               result=result, gap_result=gap_result)
                               
    return render_template('calculator.html', active_page='calculator')

@app.route('/resignation_checker', methods=['GET', 'POST'])
@login_required
def resignation_checker():
    result = None
    if request.method == 'POST':
        written_offer = request.form.get('written_offer')
        bg_complete = request.form.get('bg_complete')
        date_confirmed = request.form.get('date_confirmed')
        contract_signed = request.form.get('contract_signed')
        
        safe_count = 0
        risks = []
        
        if written_offer == 'yes':
            safe_count += 1
        else:
            risks.append("You do not have a written offer. Verbal offers can be withdrawn easily.")
            
        if bg_complete == 'yes' or bg_complete == 'not_applicable':
            safe_count += 1
        else:
            risks.append("Background verification is not complete. Your offer could be revoked if it fails.")
            
        if date_confirmed == 'yes':
            safe_count += 1
        else:
            risks.append("Your joining date is not confirmed in writing.")
            
        if contract_signed == 'yes':
            safe_count += 1
        else:
            risks.append("You have not signed the final employment contract.")
            
        if safe_count == 4:
            recommendation = "SAFE TO RESIGN"
            color = "success"
            icon = "check-circle"
            explanation = "You have all the necessary written confirmations. It is generally safe to submit your resignation."
        elif safe_count >= 2:
            recommendation = "RESIGN WITH CAUTION"
            color = "warning"
            icon = "exclamation-triangle"
            explanation = "You have some confirmations, but there are still significant risks. Consider waiting until all conditions are met."
        else:
            recommendation = "DO NOT RESIGN YET"
            color = "danger"
            icon = "times-circle"
            explanation = "It is highly risky to resign right now. Wait for written confirmation and cleared verifications."
            
        result = {
            'recommendation': recommendation,
            'color': color,
            'icon': icon,
            'explanation': explanation,
            'risks': risks
        }
        
    return render_template('resignation_checker.html', active_page='resignation_checker', result=result)

@app.route('/history')
@login_required
def history():
    assessments = get_assessments()
    documents = get_documents()
    return render_template('history.html', active_page='history', 
                           assessments=assessments, documents=documents)

@app.route('/demo', methods=['POST'])
@login_required
def demo():
    session['demo_data'] = {
        'current_job_title': 'Software Developer',
        'current_company': 'ABC Technologies',
        'new_company': 'XYZ Solutions',
        'new_job_title': 'AI Engineer',
        'offer_received': 'yes',
        'offer_type': 'Verbal Offer',
        'joining_date_confirmed': 'no',
        'background_verification': 'in_progress',
        'resignation_submitted': 'yes',
        'notice_period': '60',
        'is_conditional': 'yes',
        'subject_to_bg': 'yes'
    }
    flash('Demo data loaded! Review the form and click Analyze.', 'info')
    return redirect(url_for('assessment'))

if __name__ == '__main__':
    app.run(debug=True)
