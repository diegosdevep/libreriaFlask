from flask import render_template, redirect, session, flash, request
from datetime import datetime
from models import db, User, Propuesta, Libro
from routes import editor_bp
from helpers.helpers import role_required

def verificar_editor_asignado(propuesta):
    if propuesta.editor_id and propuesta.editor_id != session['user_id']:
        editor = User.query.get(propuesta.editor_id)
        return False, f'Esta propuesta ya está siendo revisada por {editor.nombre}'
    return True, None

@editor_bp.route('/dashboard/editor')
@role_required('editor')
def dashboard_editor():
    editor = User.query.get(session['user_id'])
    
    if not editor:
        session.clear()
        flash('Tu sesión ha expirado', 'warning')
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
    
    return render_template(
        'dashboard_editor.html',
        editor=editor,
        propuestas=propuestas,
        filtro_actual=filtro,
        stats={
            'total_propuestas': len(todas),
            'aceptadas': sum(1 for p in todas if p.estado == 'aceptada'),
            'en_revision': sum(1 for p in todas if p.estado == 'en_revision'),
            'pendientes': sum(1 for p in todas if p.estado == 'pendiente'),
            'rechazadas': sum(1 for p in todas if p.estado == 'rechazada'),
            'revisadas_por_mi': sum(1 for p in todas if p.editor_id == session['user_id'])
        }
    )

@editor_bp.route('/editor/propuesta/<int:id>')
@role_required('editor')
def ver_propuesta_editor(id):
    propuesta = Propuesta.query.get_or_404(id)
    return render_template('editor_ver_propuesta.html', propuesta=propuesta)

@editor_bp.route('/editor/propuesta/<int:id>/revisar', methods=['POST'])
@role_required('editor')
def revisar_propuesta(id):
    propuesta = Propuesta.query.get_or_404(id)
    accion = request.form.get('accion')
    
    if accion not in ['aceptar', 'rechazar', 'en_revision']:
        flash('Acción no válida', 'error')
        return redirect('/dashboard/editor')
    
    puede_editar, mensaje = verificar_editor_asignado(propuesta)
    if not puede_editar:
        flash(mensaje, 'warning')
        return redirect('/dashboard/editor')
    
    try:
        if accion == 'aceptar':
            propuesta.estado = 'aceptada'
            mensaje_flash = 'Propuesta aceptada'
        elif accion == 'rechazar':
            propuesta.estado = 'rechazada'
            mensaje_flash = 'Propuesta rechazada'
        else:
            propuesta.estado = 'en_revision'
            mensaje_flash = 'Propuesta en revisión'
        
        propuesta.editor_id = session['user_id']
        propuesta.fecha_revision = datetime.utcnow()
        
        db.session.commit()
        flash(mensaje_flash, 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al procesar la propuesta', 'error')
    
    return redirect('/dashboard/editor')

@editor_bp.route('/editor/propuesta/<int:id>/cambiar-estado', methods=['POST'])
@role_required('editor')
def cambiar_estado(id):
    propuesta = Propuesta.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    
    if nuevo_estado not in ['pendiente', 'en_revision', 'aceptada', 'rechazada']:
        flash('Estado no válido', 'error')
        return redirect(f'/editor/propuesta/{id}')
    
    puede_editar, mensaje = verificar_editor_asignado(propuesta)
    if not puede_editar:
        flash(mensaje, 'warning')
        return redirect('/dashboard/editor')
    
    try:
        propuesta.estado = nuevo_estado
        propuesta.editor_id = session['user_id']
        propuesta.fecha_revision = datetime.utcnow()
        db.session.commit()
        flash(f'Estado cambiado a {nuevo_estado}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al cambiar el estado', 'error')
    
    return redirect(f'/editor/propuesta/{id}')

@editor_bp.route('/editor/propuesta/<int:id>/publicar', methods=['POST'])
@role_required('editor')
def publicar_libro(id):
    propuesta = Propuesta.query.get_or_404(id)
    
    if propuesta.estado != 'aceptada':
        flash('Solo se pueden publicar propuestas aceptadas', 'warning')
        return redirect(f'/editor/propuesta/{id}')
    
    if Libro.query.filter_by(propuesta_id=propuesta.id).first():
        flash('Esta propuesta ya está publicada', 'warning')
        return redirect(f'/editor/propuesta/{id}')
    
    precio = request.form.get('precio')
    if not precio:
        flash('Debes especificar un precio', 'error')
        return redirect(f'/editor/propuesta/{id}')
    
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
    
    return redirect('/dashboard/editor')