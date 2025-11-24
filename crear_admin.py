from app import app
from models import db, User
from werkzeug.security import generate_password_hash
import uuid

def crear_usuarios():
    with app.app_context():
        admin_existente = User.query.filter_by(email='admin@gmail.com').first()
        editor1_existente = User.query.filter_by(email='editor1@gmail.com').first()
        editor2_existente = User.query.filter_by(email='editor2@gmail.com').first()
        
        usuarios_creados = []
        
        if admin_existente:
            print("El admin ya existe")
        else:
            admin = User(
                id=str(uuid.uuid4()),
                nombre='Administrador',
                email='admin@gmail.com',
                password=generate_password_hash('123123'),
                rol='admin',
                generos_interes=''
            )
            db.session.add(admin)
            usuarios_creados.append(('admin@gmail.com', '123123', 'admin'))
        
        if editor1_existente:
            print("El editor1 ya existe")
        else:
            editor1 = User(
                id=str(uuid.uuid4()),
                nombre='María García',
                email='editor1@gmail.com',
                password=generate_password_hash('123123'),
                rol='editor',
                generos_interes='Ficción, Misterio, Thriller'
            )
            db.session.add(editor1)
            usuarios_creados.append(('editor1@gmail.com', '123123', 'editor'))
        
        if editor2_existente:
            print("El editor2 ya existe")
        else:
            editor2 = User(
                id=str(uuid.uuid4()),
                nombre='Carlos Martínez',
                email='editor2@gmail.com',
                password=generate_password_hash('123123'),
                rol='editor',
                generos_interes='No Ficción, Ciencia, Tecnología'
            )
            db.session.add(editor2)
            usuarios_creados.append(('editor2@gmail.com', '123123', 'editor'))
        
        if usuarios_creados:
            db.session.commit()
            print("\nUsuarios creados exitosamente:\n")

if __name__ == '__main__':
    crear_usuarios()