from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        if user and User.check_password(user, password):
            session['user_id'] = str(user['id'])  # Use 'id' instead of '_id'
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

