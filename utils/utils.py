import os
from werkzeug.utils import secure_filename
from config import Config, allowed_file
from datetime import datetime

def validar_propuesta(titulo, genero, descripcion):
    if not titulo or not genero or not descripcion:
        return False, 'Todos los campos son obligatorios'
    
    if len(titulo) < 3:
        return False, 'El título debe tener al menos 3 caracteres'
    
    if len(descripcion) < 50:
        return False, 'La descripción debe tener al menos 50 caracteres'
    
    return True, None


def guardar_manuscrito(archivo, user_id):
    if not archivo or not archivo.filename:
        return None
    
    if not allowed_file(archivo.filename):
        raise ValueError('Formato de archivo no permitido. Solo PDF, DOC, DOCX, EPUB')
    
    if Config.USE_S3:
        from s3_storage import subir_a_s3
        return subir_a_s3(archivo, user_id)
    
    else:
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(archivo.filename)
        nombre_base, extension = os.path.splitext(filename)
        nuevo_nombre = f"{user_id}_{timestamp}_{nombre_base}{extension}"
        
        filepath = os.path.join(Config.UPLOAD_FOLDER, nuevo_nombre)
        archivo.save(filepath)
        
        return filepath


def eliminar_archivo(filepath):
    if not filepath:
        return False
    
    if filepath.startswith('https://'):
        from s3_storage import eliminar_de_s3
        return eliminar_de_s3(filepath)
    
    elif os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception:
            return False
    
    return False