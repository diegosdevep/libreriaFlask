from flask import render_template, redirect, session, flash
from routes import admin_bp

@admin_bp.route('/dashboard/admin')
def dashboard_admin():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'warning')
        return redirect('/login')
    
    if session.get('role') != 'admin':
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect('/')
    
    return render_template('dashboard_admin.html')