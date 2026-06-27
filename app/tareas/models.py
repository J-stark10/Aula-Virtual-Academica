from datetime import datetime
from app.app import db


class Tarea(db.Model):
    __tablename__ = "tareas"

    id = db.Column(db.Integer, primary_key=True)
    modulo_id = db.Column(db.Integer, db.ForeignKey("modulos.id"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    instrucciones = db.Column(db.Text)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_limite = db.Column(db.DateTime, nullable=False)
    puntaje_maximo = db.Column(db.Float, default=100.0, nullable=False)

    modulo = db.relationship("Modulo", back_populates="tareas")
    entregas = db.relationship("Entrega", back_populates="tarea", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Tarea {self.titulo}>"
