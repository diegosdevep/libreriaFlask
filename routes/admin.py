from flask import render_template, redirect, session, flash, request
from datetime import datetime
from models import db, User, Propuesta, Libro
from routes import admin_bp
from helpers.helpers import role_required

@admin_bp.route('/dashboard/admin')
@role_required('admin')
def dashboard_admin():
    admin = User.query.get(session['user_id'])
    
    if not admin:
        session.clear()
        flash('Tu sesion ha expirado', 'warning')
        return redirect('/login')
    
    filtro = request.args.get('filtro', 'all')
    query = Propuesta.query
    
    filtros_estado = {
        'pendiente': 'pendiente',
        'aceptada': 'aceptada',
        'rechazada': 'rechazada',
        'en_revision': 'en_revision'
    }
    
    if filtro in filtros_estado:
        propuestas = query.filter_by(estado=filtros_estado[filtro]).order_by(Propuesta.fecha_envio.desc()).all()
    else:
        propuestas = query.order_by(Propuesta.fecha_envio.desc()).all()
        filtro = 'all'
    
    todas = Propuesta.query.all()
    
    total_autores = User.query.filter_by(rol='autor').count()
    total_editores = User.query.filter_by(rol='editor').count()
    libros_publicados = Libro.query.filter_by(estado='publicado').count()
    
    return render_template(
        'dashboard_admin.html',
        admin=admin,
        propuestas=propuestas,
        filtro_actual=filtro,
        stats={
            'total_propuestas': len(todas),
            'aceptadas': sum(1 for p in todas if p.estado == 'aceptada'),
            'en_revision': sum(1 for p in todas if p.estado == 'en_revision'),
            'pendientes': sum(1 for p in todas if p.estado == 'pendiente'),
            'rechazadas': sum(1 for p in todas if p.estado == 'rechazada'),
            'total_autores': total_autores,
            'total_editores': total_editores,
            'libros_publicados': libros_publicados
        }
    )

@admin_bp.route('/admin/propuesta/<int:id>')
@role_required('admin')
def ver_propuesta_admin(id):
    propuesta = Propuesta.query.get_or_404(id)
    return render_template('admin_ver_propuesta.html', propuesta=propuesta)

@admin_bp.route('/admin/propuesta/<int:id>/cambiar-estado', methods=['POST'])
@role_required('admin')
def cambiar_estado(id):
    propuesta = Propuesta.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    
    if nuevo_estado not in ['pendiente', 'en_revision', 'aceptada', 'rechazada']:
        flash('Estado no valido', 'error')
        return redirect(f'/admin/propuesta/{id}')
    
    try:
        propuesta.estado = nuevo_estado
        propuesta.editor_id = session['user_id']
        propuesta.fecha_revision = datetime.utcnow()
        db.session.commit()
        flash(f'Estado cambiado a {nuevo_estado}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al cambiar el estado', 'error')
    
    return redirect(f'/admin/propuesta/{id}')

@admin_bp.route('/admin/propuesta/<int:id>/publicar', methods=['POST'])
@role_required('admin')
def publicar_libro(id):
    propuesta = Propuesta.query.get_or_404(id)
    
    if propuesta.estado != 'aceptada':
        flash('Solo se pueden publicar propuestas aceptadas', 'warning')
        return redirect(f'/admin/propuesta/{id}')
    
    if Libro.query.filter_by(propuesta_id=propuesta.id).first():
        flash('Esta propuesta ya esta publicada', 'warning')
        return redirect(f'/admin/propuesta/{id}')
    
    precio = request.form.get('precio')
    if not precio:
        flash('Debes especificar un precio', 'error')
        return redirect(f'/admin/propuesta/{id}')
    
    try:
        libro = Libro(
            titulo=propuesta.titulo,
            autor_nombre=propuesta.autor.nombre,
            descripcion=propuesta.descripcion,
            genero=propuesta.genero,
            precio=float(precio),
            estado='publicado',
            propuesta_id=propuesta.id
        )
        
        db.session.add(libro)
        db.session.commit()
        flash('Libro publicado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al publicar el libro', 'error')
    
    return redirect('/dashboard/admin')

@admin_bp.route('/admin/usuarios')
@role_required('admin')
def gestionar_usuarios():
    autores = User.query.filter_by(rol='autor').all()
    editores = User.query.filter_by(rol='editor').all()
    admins = User.query.filter_by(rol='admin').all()
    
    return render_template(
        'admin_usuarios.html',
        autores=autores,
        editores=editores,
        admins=admins
    )

@admin_bp.route('/admin/libros')
@role_required('admin')
def gestionar_libros():
    libros = Libro.query.order_by(Libro.fecha_publicacion.desc()).all()
    
    return render_template('admin_libros.html', libros=libros)

@admin_bp.route('/admin/libro/<int:id>/eliminar', methods=['POST'])
@role_required('admin')
def eliminar_libro(id):
    libro = Libro.query.get_or_404(id)
    
    try:
        db.session.delete(libro)
        db.session.commit()
        flash('Libro eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el libro', 'error')
    
    return redirect('/admin/libros')