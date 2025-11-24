from flask import render_template, request, redirect, session, flash,  jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from routes import auth_bp
from helpers.helpers import login_required
from firebase_admin import auth as admin_auth
import os


def get_dashboard_url(role):
    return f'/dashboard/{role}'


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(get_dashboard_url(session['role']))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        generos = request.form.getlist('generos')
        
        if not all([nombre, apellido, email, password, confirm_password]):
            flash('Todos los campos son obligatorios', 'error')
            return render_template('register.html')
        
        if not generos:
            flash('Debes seleccionar al menos un género de interés', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Este correo ya está registrado', 'error')
            return render_template('register.html')
        
        import uuid
        user_id = str(uuid.uuid4())
        
        new_user = User(
            id=user_id,  
            nombre=f"{nombre} {apellido}",
            email=email,
            password=generate_password_hash(password),
            rol='autor',
            generos_interes=','.join(generos)
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            session['nombre'] = new_user.nombre
            session['role'] = new_user.rol
            
            flash('¡Cuenta creada exitosamente!', 'success')
            return redirect('/dashboard/autor')
        except Exception:
            db.session.rollback()
            flash('Error al crear la cuenta. Intenta nuevamente', 'error')
    
    return render_template('register.html')

@auth_bp.route('/google-login')
def google_login():
    firebase_config = {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID')
    }
    return render_template('google_auth.html', firebase_config=firebase_config)


@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    try:
        id_token = request.json.get('idToken')
        
        decoded_token = admin_auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email')
        name = decoded_token.get('name', email.split('@')[0])
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User(
                id=uid,
                nombre=name,
                email=email,
                password=generate_password_hash('google_auth_' + uid),
                rol='autor',
                generos_interes=''
            )
            db.session.add(user)
            db.session.commit()
        
        session['user_id'] = user.id
        session['nombre'] = user.nombre
        session['role'] = user.rol
        
        return jsonify({
            'success': True, 
            'redirect': get_dashboard_url(user.rol)
        })
        
    except Exception as e:
        print(f"Error en verify_token: {e}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 401

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(get_dashboard_url(session['role']))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['nombre'] = user.nombre
            session['role'] = user.rol
            
            return redirect(get_dashboard_url(user.rol))
        
        flash('Correo o contraseña incorrectos', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'success')
    return redirect('/')


@auth_bp.route('/perfil')
@login_required
def perfil():
    user = User.query.get(session['user_id'])
    
    if not user:
        session.clear()
        flash('Sesión expirada', 'warning')
        return redirect('/login')
    
    return redirect(get_dashboard_url(user.rol))

@auth_bp.route('/setup-usuarios-xyz')
def setup_usuarios():
    from models import db, User
    from werkzeug.security import generate_password_hash
    import uuid
    
    admin = User.query.filter_by(email='admin@gmail.com').first()
    if not admin:
        admin = User(
            id=str(uuid.uuid4()),
            nombre='Administrador',
            email='admin@gmail.com',
            password=generate_password_hash('123123'),
            rol='admin',
            generos_interes=''
        )
        db.session.add(admin)
    
    editor1 = User.query.filter_by(email='editor1@gmail.com').first()
    if not editor1:
        editor1 = User(
            id=str(uuid.uuid4()),
            nombre='Maria Garcia',
            email='editor1@gmail.com',
            password=generate_password_hash('123123'),
            rol='editor',
            generos_interes='Ficcion, Misterio'
        )
        db.session.add(editor1)
    
    editor2 = User.query.filter_by(email='editor2@gmail.com').first()
    if not editor2:
        editor2 = User(
            id=str(uuid.uuid4()),
            nombre='Carlos Martinez',
            email='editor2@gmail.com',
            password=generate_password_hash('123123'),
            rol='editor',
            generos_interes='No Ficcion, Ciencia'
        )
        db.session.add(editor2)
    
    db.session.commit()
    return "Usuarios creados"