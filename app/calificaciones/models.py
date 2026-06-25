from datetime import datetime
from app.app import db

class Calificacion(db.Model):
    __tablename__ = "calificaciones"

    id = db.Column(db.Integer, primary_key=True)
    entrega_id = db.Column(db.Integer, db.ForeignKey("entregas.id"), nullable=False, unique=True)
    docente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    retroalimentacion = db.Column(db.String(500))
    fecha_calificacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    entrega = db.relationship("Entrega", back_populates="calificacion")
    docente = db.relationship("Usuario", back_populates="calificaciones_realizadas")
    historial = db.relationship("HistorialCalificacion", back_populates="calificacion", cascade="all, delete-orphan", order_by="HistorialCalificacion.fecha_cambio.desc()")

    def __repr__(self):
        return f"<Calificacion entrega={self.entrega_id} nota={self.nota}>"

class HistorialCalificacion(db.Model):
    __tablename__ = "historial_calificaciones"

    id = db.Column(db.Integer, primary_key=True)
    calificacion_id = db.Column(db.Integer, db.ForeignKey("calificaciones.id"), nullable=False)
    nota_anterior = db.Column(db.Float, nullable=False)
    nota_nueva = db.Column(db.Float, nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    calificacion = db.relationship("Calificacion", back_populates="historial")
    docente = db.relationship("Usuario")

    def __repr__(self):
        return f"<Historial calificacion={self.calificacion_id} {self.nota_anterior}->{self.nota_nueva}>"
