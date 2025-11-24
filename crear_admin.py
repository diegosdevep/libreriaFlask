from app import app
from models import db, User
from werkzeug.security import generate_password_hash
import uuid

def crear_admin():
    with app.app_context():
        admin_existente = User.query.filter_by(email='admin@gmail.com').first()
        
        if admin_existente:
            print("⚠️  El admin ya existe")
            print(f"   Email: {admin_existente.email}")
            print(f"   Rol: {admin_existente.rol}")
            return
        
        admin = User(
            id=str(uuid.uuid4()),
            nombre='Administrador',
            email='admin@gmail.com',
            password=generate_password_hash('123123'),
            rol='admin',
            generos_interes=''
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Administrador creado exitosamente")
        print(f"   Email: admin@gmail.com")
        print(f"   Password: 123123")
        print(f"   Rol: admin")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")

if __name__ == '__main__':
    crear_admin()