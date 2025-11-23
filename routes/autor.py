from flask import render_template, request, redirect, session, send_from_directory, current_app, flash
from datetime import datetime
import os
from models import db, User, Propuesta, Libro
from routes import autor_bp
from helpers.helpers import login_required, role_required
from utils.utils import guardar_manuscrito, eliminar_archivo, validar_propuesta


@autor_bp.route('/dashboard/autor')
@role_required('autor')
def dashboard_autor():
    autor = User.query.get(session['user_id'])
    
    if not autor:
        session.clear()
        flash('Tu sesión ha expirado. Por favor inicia sesión nuevamente', 'warning')
        return redirect('/login')
    
    filtro = request.args.get('filtro', 'all')
    query = Propuesta.query.filter_by(autor_id=session['user_id'])
    
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
    
    libros = Libro.query.join(Propuesta).filter(
        Propuesta.autor_id == session['user_id'],
        Libro.estado == 'publicado'
    ).all()
    
    todas_propuestas = Propuesta.query.filter_by(autor_id=session['user_id']).all()
    total_propuestas = len(todas_propuestas)
    propuestas_aceptadas = sum(1 for p in todas_propuestas if p.estado == 'aceptada')
    propuestas_revision = sum(1 for p in todas_propuestas if p.estado == 'en_revision')
    propuestas_pendientes = sum(1 for p in todas_propuestas if p.estado == 'pendiente')
    propuestas_rechazadas = sum(1 for p in todas_propuestas if p.estado == 'rechazada')
    
    tasa_aceptacion = (propuestas_aceptadas / total_propuestas * 100) if total_propuestas > 0 else 0
    
    return render_template(
        'dashboard_autor.html',
        autor=autor,
        propuestas=propuestas,
        libros=libros,
        filtro_actual=filtro,
        stats={
            'total_propuestas': total_propuestas,
            'aceptadas': propuestas_aceptadas,
            'en_revision': propuestas_revision,
            'pendientes': propuestas_pendientes,
            'rechazadas': propuestas_rechazadas,
            'libros_publicados': len(libros),
            'tasa_aceptacion': round(tasa_aceptacion, 1)
        }
    )


@autor_bp.route('/autor/nueva-propuesta', methods=['GET', 'POST'])
@role_required('autor')
def nueva_propuesta():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        genero = request.form.get('genero')
        num_paginas = request.form.get('num_paginas')
        descripcion = request.form.get('descripcion')
        manuscrito_url = request.form.get('manuscrito_url')
        
        valido, error = validar_propuesta(titulo, genero, descripcion)
        if not valido:
            flash(error, 'error')
            return render_template('nueva_propuesta.html')
        
        archivo = request.files.get('manuscrito_file')
        archivo_path = None
        
        try:
            archivo_path = guardar_manuscrito(archivo, session['user_id'])
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('nueva_propuesta.html')
        except Exception:
            flash('Error al guardar el archivo. Intenta nuevamente.', 'error')
            return render_template('nueva_propuesta.html')
        
        if not archivo_path and not manuscrito_url:
            flash('Debes subir un archivo o proporcionar un enlace al manuscrito', 'error')
            return render_template('nueva_propuesta.html')
        
        nueva_propuesta = Propuesta(
            titulo=titulo,
            genero=genero,
            num_paginas=int(num_paginas) if num_paginas else None,
            descripcion=descripcion,
            manuscrito_url=manuscrito_url if manuscrito_url else archivo_path,
            estado='pendiente',
            autor_id=session['user_id']
        )
        
        try:
            db.session.add(nueva_propuesta)
            db.session.commit()
            flash('¡Propuesta enviada exitosamente!', 'success')
            return redirect('/dashboard/autor')
        except Exception:
            db.session.rollback()
            eliminar_archivo(archivo_path)
            flash('Error al enviar la propuesta. Intenta nuevamente.', 'error')
            return render_template('nueva_propuesta.html')
    
    return render_template('nueva_propuesta.html')


@autor_bp.route('/autor/propuesta/<int:id>')
@role_required('autor')
def ver_propuesta(id):
    propuesta = Propuesta.query.get_or_404(id)
    
    if propuesta.autor_id != session['user_id']:
        flash('No tienes permisos para ver esta propuesta', 'error')
        return redirect('/dashboard/autor')
    
    return render_template('ver_propuesta.html', propuesta=propuesta)


@autor_bp.route('/autor/propuesta/<int:id>/editar', methods=['GET', 'POST'])
@role_required('autor')
def editar_propuesta(id):
    propuesta = Propuesta.query.get_or_404(id)
    
    if propuesta.autor_id != session['user_id']:
        flash('No tienes permisos para editar esta propuesta', 'error')
        return redirect('/dashboard/autor')
    
    if propuesta.estado != 'pendiente':
        flash('Solo puedes editar propuestas que están pendientes', 'warning')
        return redirect('/dashboard/autor')
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        genero = request.form.get('genero')
        num_paginas = request.form.get('num_paginas')
        descripcion = request.form.get('descripcion')
        manuscrito_url = request.form.get('manuscrito_url')
        
        valido, error = validar_propuesta(titulo, genero, descripcion)
        if not valido:
            flash(error, 'error')
            return render_template('editar_propuesta.html', propuesta=propuesta)
        
        propuesta.titulo = titulo
        propuesta.genero = genero
        propuesta.num_paginas = int(num_paginas) if num_paginas else None
        propuesta.descripcion = descripcion
        
        archivo = request.files.get('manuscrito_file')
        if archivo and archivo.filename:
            try:
                archivo_anterior = propuesta.manuscrito_url
                nuevo_path = guardar_manuscrito(archivo, session['user_id'])
                
                if nuevo_path:
                    eliminar_archivo(archivo_anterior)
                    propuesta.manuscrito_url = nuevo_path
            except ValueError as e:
                flash(str(e), 'error')
                return render_template('editar_propuesta.html', propuesta=propuesta)
            except Exception:
                flash('Error al guardar el archivo. Intenta nuevamente.', 'error')
                return render_template('editar_propuesta.html', propuesta=propuesta)
        elif manuscrito_url:
            propuesta.manuscrito_url = manuscrito_url
        
        try:
            db.session.commit()
            flash('¡Propuesta actualizada exitosamente!', 'success')
            return redirect('/dashboard/autor')
        except Exception:
            db.session.rollback()
            flash('Error al actualizar la propuesta. Intenta nuevamente.', 'error')
            return render_template('editar_propuesta.html', propuesta=propuesta)
    
    return render_template('editar_propuesta.html', propuesta=propuesta)


@autor_bp.route('/autor/propuesta/<int:id>/eliminar', methods=['POST'])
@role_required('autor')
def eliminar_propuesta(id):
    propuesta = Propuesta.query.get_or_404(id)
    
    if propuesta.autor_id != session['user_id']:
        flash('No tienes permisos para eliminar esta propuesta', 'error')
        return redirect('/dashboard/autor')
    
    if propuesta.estado not in ['pendiente', 'rechazada']:
        flash('Solo puedes eliminar propuestas pendientes o rechazadas', 'warning')
        return redirect('/dashboard/autor')
    
    try:
        eliminar_archivo(propuesta.manuscrito_url)
        db.session.delete(propuesta)
        db.session.commit()
        flash('Propuesta eliminada exitosamente', 'success')
    except Exception:
        db.session.rollback()
        flash('Error al eliminar la propuesta. Intenta nuevamente', 'error')
    
    return redirect('/dashboard/autor')


@autor_bp.route('/autor/propuestas')
@role_required('autor')
def autor_propuestas():
    propuestas = Propuesta.query.filter_by(
        autor_id=session['user_id']
    ).order_by(
        Propuesta.fecha_envio.desc()
    ).all()
    
    return render_template('autor_propuestas.html', propuestas=propuestas)


@autor_bp.route('/uploads/manuscritos/<filename>')
@login_required
def uploaded_file(filename):
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        flash('El archivo solicitado no existe', 'error')
        return redirect('/')
    
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)