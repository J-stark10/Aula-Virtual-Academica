from datetime import datetime, timedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from app.app import db
from app.usuarios.models import Usuario, LogActividad
from app.cursos.models import Curso, Inscripcion
from app.entregas.models import Entrega
from app.calificaciones.models import Calificacion
from app.tareas.models import Tarea
from app.anuncios.models import Anuncio

bp_core = Blueprint("core", __name__, template_folder="templates")


@bp_core.route("/")
@login_required
def index():
    if current_user.rol == "admin":
        return _dashboard_admin()
    if current_user.rol == "docente":
        return _dashboard_docente()
    return _dashboard_estudiante()


def _dashboard_admin():
    total_usuarios = Usuario.query.count()
    total_docentes = Usuario.query.filter_by(rol="docente").count()
    total_estudiantes = Usuario.query.filter_by(rol="estudiante").count()
    total_cursos = Curso.query.count()
    total_inscripciones = Inscripcion.query.count()

    # Registros por día (últimos 7 días) para Chart.js
    hoy = datetime.utcnow().date()
    labels = []
    data_registros = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        labels.append(dia.strftime("%d/%m"))
        total_dia = (
            db.session.query(func.count(Usuario.id))
            .filter(func.date(Usuario.fecha_registro) == dia)
            .scalar()
            or 0
        )
        data_registros.append(total_dia)

    recientes_logs = LogActividad.query.order_by(LogActividad.fecha.desc()).limit(8).all()
    ultimos_cursos = Curso.query.order_by(Curso.fecha_creacion.desc()).limit(5).all()

    return render_template(
        "core/dashboard_admin.html",
        total_usuarios=total_usuarios,
        total_docentes=total_docentes,
        total_estudiantes=total_estudiantes,
        total_cursos=total_cursos,
        total_inscripciones=total_inscripciones,
        chart_labels=labels,
        chart_data=data_registros,
        recientes_logs=recientes_logs,
        ultimos_cursos=ultimos_cursos,
    )


def _dashboard_docente():
    cursos = Curso.query.filter_by(docente_id=current_user.id).all()
    curso_ids = [c.id for c in cursos]

    total_cursos = len(cursos)
    total_estudiantes = (
        Inscripcion.query.filter(Inscripcion.curso_id.in_(curso_ids)).count()
        if curso_ids
        else 0
    )

    tareas_ids = [t.id for c in cursos for m in c.modulos for t in m.tareas]
    total_tareas = len(tareas_ids)

    entregas_sin_revisar = (
        Entrega.query.filter(Entrega.tarea_id.in_(tareas_ids), Entrega.estado == "entregado").count()
        if tareas_ids
        else 0
    )

    # Tareas próximas a vencer (siguientes 7 días)
    ahora = datetime.utcnow()
    en_una_semana = ahora + timedelta(days=7)
    tareas_proximas = (
        Tarea.query.filter(
            Tarea.id.in_(tareas_ids),
            Tarea.fecha_limite >= ahora,
            Tarea.fecha_limite <= en_una_semana,
        ).order_by(Tarea.fecha_limite.asc()).all()
        if tareas_ids
        else []
    )

    return render_template(
        "core/dashboard_docente.html",
        cursos=cursos,
        total_cursos=total_cursos,
        total_estudiantes=total_estudiantes,
        total_tareas=total_tareas,
        entregas_sin_revisar=entregas_sin_revisar,
        tareas_proximas=tareas_proximas,
    )


def _dashboard_estudiante():
    inscripciones = Inscripcion.query.filter_by(estudiante_id=current_user.id).all()
    cursos = [i.curso for i in inscripciones]
    curso_ids = [c.id for c in cursos]

    tareas_ids = [t.id for c in cursos for m in c.modulos for t in m.tareas]
    todas_tareas = (
        Tarea.query.filter(Tarea.id.in_(tareas_ids)).all() if tareas_ids else []
    )

    entregas_propias = Entrega.query.filter_by(estudiante_id=current_user.id).all()
    entregadas_ids = {e.tarea_id for e in entregas_propias}

    ahora = datetime.utcnow()
    tareas_pendientes = [
        t for t in todas_tareas if t.id not in entregadas_ids and t.fecha_limite >= ahora
    ]
    tareas_vencidas_sin_entregar = [
        t for t in todas_tareas if t.id not in entregadas_ids and t.fecha_limite < ahora
    ]

    promedio_notas = (
        db.session.query(func.avg(Calificacion.nota))
        .join(Entrega)
        .filter(Entrega.estudiante_id == current_user.id)
        .scalar()
    )

    anuncios_recientes = (
        Anuncio.query.filter(Anuncio.curso_id.in_(curso_ids))
        .order_by(Anuncio.fecha_publicacion.desc())
        .limit(5)
        .all()
        if curso_ids
        else []
    )

    return render_template(
        "core/dashboard_estudiante.html",
        cursos=cursos,
        total_cursos=len(cursos),
        tareas_pendientes=tareas_pendientes,
        tareas_vencidas_sin_entregar=tareas_vencidas_sin_entregar,
        promedio_notas=round(promedio_notas, 1) if promedio_notas else None,
        anuncios_recientes=anuncios_recientes,
    )


