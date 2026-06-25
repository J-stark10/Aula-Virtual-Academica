from app.app import db


class Modulo(db.Model):
    __tablename__ = "modulos"

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.String(255))
    orden = db.Column(db.Integer, default=1, nullable=False)

    curso = db.relationship("Curso", back_populates="modulos")
    recursos = db.relationship(
        "Recurso", back_populates="modulo", cascade="all, delete-orphan",
        order_by="Recurso.id",
    )
    tareas = db.relationship(
        "Tarea", back_populates="modulo", cascade="all, delete-orphan",
        order_by="Tarea.fecha_limite",
    )

    def __repr__(self):
        return f"<Modulo {self.titulo} (curso={self.curso_id})>"
