from datetime import datetime
from app.app import db


class AutoevaluacionConfig(db.Model):
    __tablename__ = "autoevaluaciones_config"

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    trimestre = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=False)

    __table_args__ = (db.UniqueConstraint("curso_id", "trimestre"),)

    curso = db.relationship("Curso", back_populates="autoevaluaciones_config")
    respuestas = db.relationship(
        "RespuestaAutoevaluacion", back_populates="config",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<AutoevaluacionConfig curso={self.curso_id} T{self.trimestre}>"


class RespuestaAutoevaluacion(db.Model):
    __tablename__ = "respuestas_autoevaluacion"

    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey("autoevaluaciones_config.id"), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    puntaje = db.Column(db.Float, nullable=True)
    fecha_respuesta = db.Column(db.DateTime, nullable=True)
    nota_final = db.Column(db.Float, nullable=True)
    retroalimentacion = db.Column(db.Text, nullable=True)
    docente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    fecha_calificacion = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint("config_id", "estudiante_id"),)

    config = db.relationship("AutoevaluacionConfig", back_populates="respuestas")
    estudiante = db.relationship("Usuario", foreign_keys=[estudiante_id])

    docente = db.relationship("Usuario", foreign_keys=[docente_id])
    def __repr__(self):
        return f"<RespuestaAutoevaluacion config={self.config_id} est={self.estudiante_id}>"


class Entrega(db.Model):
    __tablename__ = "entregas"
    __table_args__ = (
        db.UniqueConstraint("tarea_id", "estudiante_id", name="uq_tarea_estudiante"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tarea_id = db.Column(db.Integer, db.ForeignKey("tareas.id"), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    archivo = db.Column(db.String(255), nullable=False)  # ruta relativa en uploads/entregas/
    comentario = db.Column(db.String(255))
    fecha_entrega = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Solo dos estados persistidos: "entregado" o "revisado".
    # "pendiente" (sin entregar) se calcula dinámicamente comparando
    # las inscripciones del curso contra las entregas existentes — no se guarda en BD.
    estado = db.Column(db.String(20), nullable=False, default="entregado")

    tarea = db.relationship("Tarea", back_populates="entregas")
    estudiante = db.relationship("Usuario", back_populates="entregas")
    calificacion = db.relationship(
        "Calificacion", back_populates="entrega", uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Entrega tarea={self.tarea_id} estudiante={self.estudiante_id} [{self.estado}]>"
