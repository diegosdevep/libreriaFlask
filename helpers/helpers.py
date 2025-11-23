from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder', 'warning')
            return redirect(url_for('auth.login'))  
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder', 'warning')
                return redirect(url_for('auth.login')) 
            
            if session.get('role') != role:
                flash('No tienes permisos para acceder a esta página', 'error')
                return redirect(url_for('auth.login')) 
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator