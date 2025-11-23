from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(128), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    generos_interes = db.Column(db.String(300))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    propuestas = db.relationship('Propuesta', 
                                  foreign_keys='Propuesta.autor_id',
                                  backref='autor', 
                                  lazy=True)
    
    propuestas_editadas = db.relationship('Propuesta',
                                          foreign_keys='Propuesta.editor_id',
                                          backref='editor',
                                          lazy=True)


class Propuesta(db.Model):
    __tablename__ = 'propuestas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    genero = db.Column(db.String(50), nullable=False)
    num_paginas = db.Column(db.Integer)
    manuscrito_url = db.Column(db.String(300))
    estado = db.Column(db.String(20), default='pendiente')
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_revision = db.Column(db.DateTime)
    
    autor_id = db.Column(db.String(128), db.ForeignKey('users.id'), nullable=False)  # ✅ Cambiado a String
    editor_id = db.Column(db.String(128), db.ForeignKey('users.id'))  # ✅ Ya estaba bien


class Libro(db.Model):
    __tablename__ = 'libros'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor_nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    genero = db.Column(db.String(50))
    precio = db.Column(db.Float)
    estado = db.Column(db.String(20), default='publicado')
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    propuesta_id = db.Column(db.Integer, db.ForeignKey('propuestas.id'))