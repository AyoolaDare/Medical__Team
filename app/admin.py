from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Patient, Activity
from datetime import datetime, timedelta
from collections import defaultdict
import plotly.graph_objs as go
import plotly.utils as pu

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
def dashboard():
    if session.get('role') not in ['Admin', 'Doctor']:
        flash('Access denied. Admin or Doctor privileges required.', 'error')
        return redirect(url_for('auth.login'))

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
    
    # Prepare data for charts
    weight_data = [float(patient.get('weight', 0)) for patient in patients if patient.get('weight')]
    bp_values = [patient.get('blood_pressure', '').split('/') for patient in patients if patient.get('blood_pressure')]
    systolic_data = [int(bp[0]) for bp in bp_values if len(bp) == 2]
    diastolic_data = [int(bp[1]) for bp in bp_values if len(bp) == 2]
    age_data = [int(patient.get('age', 0)) for patient in patients if patient.get('age')]
    height_data = [float(patient.get('height', 0)) for patient in patients if patient.get('height')]
    
    return render_template('admin_dashboard.html', 
                           patients=patients, 
                           recent_activities=recent_activities,
                           patient_growth=patient_growth,
                           weight_data=weight_data,
                           systolic_data=systolic_data,
                           diastolic_data=diastolic_data,
                           age_data=age_data,
                           height_data=height_data)

# ... (rest of the admin.py file remains unchanged)

def calculate_patient_growth(start_date, end_date):
    patients = Patient.get_all()
    monthly_growth = defaultdict(int)
    
    for patient in patients:
        created_at = patient.get('created_at')
        if created_at:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if start_date <= created_at <= end_date:
                month_year = created_at.strftime('%Y-%m')
                monthly_growth[month_year] += 1
    
    sorted_growth = sorted(monthly_growth.items())
    labels = [datetime.strptime(date, '%Y-%m').strftime('%b %Y') for date, _ in sorted_growth]
    data = [count for _, count in sorted_growth]
    
    return {
        'labels': labels,
        'data': data
    }

def generate_weight_distribution_graph(patients):
    weights = [float(patient.get('weight', 0)) for patient in patients if patient.get('weight')]
    
    trace = go.Histogram(x=weights, nbinsx=20)
    layout = go.Layout(title='Weight Distribution', xaxis_title='Weight (kg)', yaxis_title='Count')
    fig = go.Figure(data=[trace], layout=layout)
    
    return pu.plot(fig, output_type='div')

def generate_bp_distribution_graph(patients):
    bp_values = [patient.get('blood_pressure', '').split('/') for patient in patients if patient.get('blood_pressure')]
    systolic = [int(bp[0]) for bp in bp_values if len(bp) == 2]
    diastolic = [int(bp[1]) for bp in bp_values if len(bp) == 2]
    
    trace_systolic = go.Box(y=systolic, name='Systolic')
    trace_diastolic = go.Box(y=diastolic, name='Diastolic')
    layout = go.Layout(title='Blood Pressure Distribution', yaxis_title='mmHg')
    fig = go.Figure(data=[trace_systolic, trace_diastolic], layout=layout)
    
    return pu.plot(fig, output_type='div')

def generate_combined_metrics_graph(patients):
    weights = [float(patient.get('weight', 0)) for patient in patients if patient.get('weight')]
    heights = [float(patient.get('height', 0)) for patient in patients if patient.get('height')]
    ages = [int(patient.get('age', 0)) for patient in patients if patient.get('age')]
    
    trace_weight = go.Scatter(x=ages, y=weights, mode='markers', name='Weight vs Age')
    trace_height = go.Scatter(x=ages, y=heights, mode='markers', name='Height vs Age')
    layout = go.Layout(title='Combined Metrics', xaxis_title='Age', yaxis_title='Value')
    fig = go.Figure(data=[trace_weight, trace_height], layout=layout)
    
    return pu.plot(fig, output_type='div')

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

