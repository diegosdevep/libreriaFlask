from flask import Flask, redirect, session, flash, render_template
from config import Config
from models import db
import firebase_config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from routes import auth_bp, public_bp, autor_bp, editor_bp, admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(autor_bp)
    app.register_blueprint(editor_bp)
    app.register_blueprint(admin_bp)
    
    @app.errorhandler(403)
    def forbidden(e):
        session.clear()
        flash('No tienes permisos para acceder. Inicia sesión nuevamente', 'warning')
        return redirect('/login')
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)