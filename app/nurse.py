from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Patient, Activity

bp = Blueprint('nurse', __name__, url_prefix='/nurse')

@bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'Nurse':
        flash('Access denied. Nurse privileges required.', 'error')
        return redirect(url_for('auth.dashboard'))

    patients = Patient.get_all()
    recent_activities = Activity.get_recent(limit=10)
    
    return render_template('nurse_dashboard.html', patients=patients, recent_activities=recent_activities)

@bp.route('/search')
def search():
    if session.get('role') != 'Nurse':
        flash('Access denied. Nurse privileges required.', 'error')
        return redirect(url_for('auth.dashboard'))

    query = request.args.get('query', '')
    patients = Patient.search(query)
    return render_template('search_results.html', patients=patients, query=query)

@bp.route('/patient/<string:patient_id>')
def view_patient(patient_id):
    if session.get('role') != 'Nurse':
        flash('Access denied. Nurse privileges required.', 'error')
        return redirect(url_for('auth.dashboard'))

    patient = Patient.get_by_id(patient_id)
    if patient:
        return render_template('patient_view.html', patient=patient)
    else:
        flash('Patient not found', 'error')
        return redirect(url_for('nurse.dashboard'))

@bp.route('/patient/<string:patient_id>/update', methods=['GET', 'POST'])
def update_patient(patient_id):
    if session.get('role') != 'Nurse':
        flash('Access denied. Nurse privileges required.', 'error')
        return redirect(url_for('auth.dashboard'))

    patient = Patient.get_by_id(patient_id)
    if not patient:
        flash('Patient not found', 'error')
        return redirect(url_for('nurse.dashboard'))

    if request.method == 'POST':
        # Update patient information
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'phone_number': request.form['phone_number'],
            'age': request.form['age'],
            'weight': request.form['weight'],
            'height': request.form['height'],
            'blood_pressure': request.form['blood_pressure']
        }
        if Patient.update(patient_id, data):
            Activity.create(
                patient_id=patient_id,
                patient_name=f"{data['first_name']} {data['last_name']}",
                action="Updated patient information",
                admin_name=session.get('username'),
                admin_role=session.get('role')
            )
            flash('Patient information updated successfully', 'success')
            return redirect(url_for('nurse.view_patient', patient_id=patient_id))
        else:
            flash('Error updating patient information', 'error')

    return render_template('patient_update.html', patient=patient)

