from datetime import datetime
from app.app import db

class Anuncio(db.Model):
    __tablename__ = "anuncios"

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    curso = db.relationship("Curso", back_populates="anuncios")

    def __repr__(self):
        return f"<Anuncio {self.titulo} (curso={self.curso_id})>"
