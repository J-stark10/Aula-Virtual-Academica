from datetime import datetime
from app.app import db


class Recurso(db.Model):
    __tablename__ = "recursos"

    id = db.Column(db.Integer, primary_key=True)
    modulo_id = db.Column(db.Integer, db.ForeignKey("modulos.id"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default="pdf")  # pdf | video | enlace
    archivo_pdf = db.Column(db.String(255))     # ruta relativa dentro de uploads/
    archivo_video = db.Column(db.String(255))   # ruta relativa dentro de uploads/
    url_enlace = db.Column(db.String(255))       # para recursos tipo enlace externo
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    modulo = db.relationship("Modulo", back_populates="recursos")

    def __repr__(self):
        return f"<Recurso {self.titulo} ({self.tipo})>"
