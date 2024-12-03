from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import Patient, Activity
from datetime import datetime

bp = Blueprint('patient', __name__)

@bp.route('/patient/<patient_id>')
def view(patient_id):
    patient = Patient.get_by_id(patient_id)
    if patient and 'medical_records' in patient:
        patient['medical_records'].sort(key=lambda x: x['timestamp'], reverse=True)
        patient['latest_records'] = patient['medical_records'][:5]
    return render_template('patient_dashboard.html', patient=patient)

@bp.route('/patient/<patient_id>/history')
def history(patient_id):
    patient = Patient.get_by_id(patient_id)
    if not patient:
        flash('Patient not found', 'error')
        return redirect(url_for('admin.dashboard'))
    if 'medical_records' in patient:
        patient['medical_records'].sort(key=lambda x: x['timestamp'], reverse=True)
    return render_template('patient_history.html', patient=patient)

@bp.route('/patient/<patient_id>/update', methods=['GET', 'POST'])
def update(patient_id):
    patient = Patient.get_by_id(patient_id)
    if not patient:
        flash('Patient not found', 'error')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'phone_number': request.form['phone_number'],
            'age': request.form.get('age')
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
        else:
            flash('Error updating patient information', 'error')
        return redirect(url_for('patient.view', patient_id=patient_id))
    return render_template('update_patient.html', patient=patient)

@bp.route('/patient/<patient_id>/add_medical_record', methods=['POST'])
def add_medical_record(patient_id):
    record = {
        'weight': request.form['weight'],
        'blood_pressure': request.form['blood_pressure'],
        'sugar_level': request.form['sugar_level'],
        'prescription': request.form['prescription'],
        'notes': request.form['notes'],
        'timestamp': datetime.utcnow().isoformat()
    }
    if Patient.add_medical_record(patient_id, record):
        patient = Patient.get_by_id(patient_id)
        Activity.create(
            patient_id=patient_id,
            patient_name=f"{patient['first_name']} {patient['last_name']}",
            action="Added medical record",
            admin_name=session.get('username'),
            admin_role=session.get('role')
        )
        flash('Medical record added successfully', 'success')
    else:
        flash('Error adding medical record', 'error')
    return redirect(url_for('patient.view', patient_id=patient_id))

