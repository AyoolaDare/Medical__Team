from flask import Blueprint, redirect, url_for, session, flash

bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'Doctor':
        flash('Access denied. Doctor privileges required.', 'error')
        return redirect(url_for('auth.dashboard'))
    
    # Redirect to admin dashboard
    return redirect(url_for('admin.dashboard'))

