from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import execute_query
import functools

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "danger")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            if session.get('role') not in roles:
                flash("Access Denied: You do not have permissions to view this resource.", "danger")
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        phone = request.form.get('phone').strip()
        college = request.form.get('college').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Simple Validation
        if not username or not email or not college or not password:
            flash("Please fill in all required fields.", "warning")
            return render_template('register.html')
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')
            
        try:
            # Check if user already exists
            existing_user = execute_query(
                "SELECT UserID FROM Users WHERE Username = ? OR Email = ?",
                (username, email)
            )
            if existing_user:
                flash("Username or Email already registered.", "warning")
                return render_template('register.html')
                
            # Insert User (role is hardcoded as 'Student' for public registrations)
            hashed_pw = generate_password_hash(password)
            execute_query(
                "INSERT INTO Users (Username, Email, PasswordHash, Phone, CollegeName, Role) VALUES (?, ?, ?, ?, ?, 'Student')",
                (username, email, hashed_pw, phone, college),
                fetch=False,
                commit=True
            )
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f"Registration failed: {e}", "danger")
            
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        role = request.form.get('role')
        
        if not username or not password or not role:
            flash("Please fill in all login fields.", "warning")
            return render_template('login.html')
            
        try:
            user_list = execute_query(
                "SELECT * FROM Users WHERE Username = ? OR Email = ?",
                (username, username)
            )
            if not user_list:
                flash("Invalid credentials.", "danger")
                return render_template('login.html')
                
            user = user_list[0]
            
            # Check Role Match
            if user['Role'] != role:
                flash(f"Access Denied: Account role mismatch. You cannot log in as '{role}'.", "danger")
                return render_template('login.html')
                
            # Check Status
            if user['UserStatus'] == 'Suspended':
                flash("Your account has been suspended. Please contact customer support.", "danger")
                return render_template('login.html')
                
            # Check Password
            if check_password_hash(user['PasswordHash'], password):
                session.clear()
                session['user_id'] = user['UserID']
                session['username'] = user['Username']
                session['role'] = user['Role']
                session['college'] = user['CollegeName']
                session.permanent = True
                
                flash(f"Welcome back, {user['Username']}!", "success")
                return redirect(url_for('dashboard.index'))
            else:
                flash("Invalid credentials.", "danger")
        except Exception as e:
            flash(f"Login failed: {e}", "danger")
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    
    if request.method == 'POST':
        email = request.form.get('email').strip()
        phone = request.form.get('phone').strip()
        college = request.form.get('college').strip()
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        try:
            user_data = execute_query("SELECT * FROM Users WHERE UserID = ?", (user_id,))[0]
            
            # Simple profile update without password change
            if not new_password:
                execute_query(
                    "UPDATE Users SET Email = ?, Phone = ?, CollegeName = ? WHERE UserID = ?",
                    (email, phone, college, user_id),
                    fetch=False,
                    commit=True
                )
                session['college'] = college # Update active session
                flash("Profile details updated successfully.", "success")
                return redirect(url_for('auth.profile'))
                
            # Update password flow
            if not current_password or not check_password_hash(user_data['PasswordHash'], current_password):
                flash("Incorrect current password. Password was not changed.", "danger")
                return redirect(url_for('auth.profile'))
                
            hashed_pw = generate_password_hash(new_password)
            execute_query(
                "UPDATE Users SET Email = ?, Phone = ?, CollegeName = ?, PasswordHash = ? WHERE UserID = ?",
                (email, phone, college, hashed_pw, user_id),
                fetch=False,
                commit=True
            )
            session['college'] = college
            flash("Profile and password updated successfully.", "success")
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            flash(f"Profile update failed: {e}", "danger")
            
    # Fetch fresh user data
    user_data = execute_query("SELECT * FROM Users WHERE UserID = ?", (user_id,))[0]
    return render_template('profile.html', user=user_data)
