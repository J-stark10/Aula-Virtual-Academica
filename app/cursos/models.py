import random
import string
from datetime import datetime
from app.app import db


def generar_codigo_unico():
    while True:
        codigo = "".join(random.choices(string.digits, k=6))
        if not Curso.query.filter_by(codigo=codigo).first():
            return codigo


class Curso(db.Model):
    __tablename__ = "cursos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.String(255))
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    docente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    codigo = db.Column(db.String(6), unique=True, nullable=False, default=generar_codigo_unico)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    categoria = db.relationship("Categoria", back_populates="cursos")
    docente = db.relationship("Usuario", back_populates="cursos_dictados")
    inscripciones = db.relationship("Inscripcion", back_populates="curso", cascade="all, delete-orphan")
    modulos = db.relationship("Modulo", back_populates="curso", cascade="all, delete-orphan", order_by="Modulo.orden")
    anuncios = db.relationship("Anuncio", back_populates="curso", cascade="all, delete-orphan")
    autoevaluaciones_config = db.relationship("AutoevaluacionConfig", back_populates="curso", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Curso {self.nombre}>"


class Inscripcion(db.Model):
    __tablename__ = "inscripciones"
    __table_args__ = (
        db.UniqueConstraint("curso_id", "estudiante_id", name="uq_curso_estudiante"),
    )

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    curso = db.relationship("Curso", back_populates="inscripciones")
    estudiante = db.relationship("Usuario", back_populates="inscripciones")

    def __repr__(self):
        return f"<Inscripcion curso={self.curso_id} estudiante={self.estudiante_id}>"
