from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Patient, Activity
from datetime import datetime, timedelta
from collections import defaultdict

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
def dashboard():
    patients = Patient.get_all()
    recent_activities = Activity.get_recent(limit=10)
    
    # Convert timestamp strings to datetime objects
    for activity in recent_activities:
        if isinstance(activity['timestamp'], str):
            activity['timestamp'] = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
    
    # Calculate patient growth for the last 6 months
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=180)
    patient_growth = calculate_patient_growth(start_date, end_date)
    
    return render_template('admin_dashboard.html', 
                           patients=patients, 
                           recent_activities=recent_activities,
                           patient_growth=patient_growth)

def calculate_patient_growth(start_date, end_date):
    patients = Patient.get_all()
    monthly_growth = defaultdict(int)
    
    for patient in patients:
        created_at = patient.get('created_at')
        if created_at:
            # Convert the string to a datetime object
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if start_date <= created_at <= end_date:
                month_year = created_at.strftime('%Y-%m')
                monthly_growth[month_year] += 1
    
    # Sort the data by date
    sorted_growth = sorted(monthly_growth.items())
    
    # Prepare data for Chart.js
    labels = [datetime.strptime(date, '%Y-%m').strftime('%b') for date, _ in sorted_growth]
    data = [count for _, count in sorted_growth]
    
    return {
        'labels': labels,
        'data': data
    }

@bp.route('/create_patient', methods=['GET', 'POST'])
def create_patient():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            phone_number = request.form['phone_number']
            age = request.form['age']
            
            new_patient_id = Patient.create(first_name, last_name, phone_number, age)
            if new_patient_id:
                Activity.create(
                    patient_id=new_patient_id,
                    patient_name=f"{first_name} {last_name}",
                    action="Created new patient",
                    admin_name=session.get('username'),
                    admin_role=session.get('role')
                )
                flash('Patient created successfully', 'success')
                return redirect(url_for('patient.view', patient_id=new_patient_id))
            else:
                flash('Error creating patient', 'error')
        except Exception as e:
            print(f"Error in create_patient route: {e}")
            flash('Error creating patient', 'error')
    
    return render_template('create_patient.html')

@bp.route('/patient_list')
def patient_list():
    patients = Patient.get_all()
    return render_template('patient_list.html', patients=patients)

@bp.route('/search')
def search():
    query = request.args.get('query', '')
    patients = Patient.search(query)
    return render_template('search_results.html', patients=patients, query=query)

@bp.route('/recent_activities')
def recent_activities():
    activities = Activity.get_all()
    # Convert timestamp strings to datetime objects
    for activity in activities:
        if isinstance(activity['timestamp'], str):
            activity['timestamp'] = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
    return render_template('recent_activities.html', activities=activities)

