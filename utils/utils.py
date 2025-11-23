from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app, flash
import os

def guardar_manuscrito(archivo, user_id):
    from config import allowed_file
    
    if not archivo or archivo.filename == '':
        return None
    
    if not allowed_file(archivo.filename):
        raise ValueError('Solo se permiten archivos PDF, DOC, DOCX o EPUB')
    
    filename = secure_filename(archivo.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"{user_id}_{timestamp}_{filename}"
    archivo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], nombre_archivo)
    
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    archivo.save(archivo_path)
    
    return archivo_path

def eliminar_archivo(file_path):
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

def validar_propuesta(titulo, genero, descripcion):
    if not all([titulo, genero, descripcion]):
        return False, 'Título, género y descripción son obligatorios'
    
    if len(descripcion) < 50:
        return False, 'La descripción debe tener al menos 50 caracteres'
    
    if len(titulo) > 200:
        return False, 'El título no puede exceder 200 caracteres'
    
    return True, None