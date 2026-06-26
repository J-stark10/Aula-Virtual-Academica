from datetime import datetime
from flask_login import UserMixin
from app.app import db


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="estudiante")
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    logs = db.relationship("LogActividad", back_populates="usuario", cascade="all, delete-orphan")
    cursos_dictados = db.relationship("Curso", back_populates="docente")
    inscripciones = db.relationship("Inscripcion", back_populates="estudiante", cascade="all, delete-orphan")
    calificaciones_realizadas = db.relationship("Calificacion", back_populates="docente")
    entregas = db.relationship("Entrega", back_populates="estudiante", cascade="all, delete-orphan")

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<Usuario {self.email} [{self.rol}]>"


class LogActividad(db.Model):
    __tablename__ = "logs_actividad"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    accion = db.Column(db.String(100), nullable=False)
    detalles = db.Column(db.String(255), nullable=True)

    usuario = db.relationship("Usuario", back_populates="logs")

    def __repr__(self):
        return f"<LogActividad {self.accion} por Usuario #{self.usuario_id}>"
