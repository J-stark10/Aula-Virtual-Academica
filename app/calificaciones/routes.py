from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.app import db
from app.entregas.models import Entrega, AutoevaluacionConfig, RespuestaAutoevaluacion
from app.calificaciones.models import Calificacion, HistorialCalificacion
from app.calificaciones.helpers import (
    puntos_usados_dimension,
    puntos_disponibles_dimension,
    nota_estudiante_dimension,
    total_tareas_dimension,
    resumen_estudiante_curso,
)
from app.cursos.models import Curso, Inscripcion
from app.tareas.models import Tarea, DIMENSIONES
from app.modulos.models import Modulo
from app.utils import registrar_log, role_required

bp_calificacion = Blueprint("calificacion", __name__, template_folder="templates")

# Calificar / Recalificar una entrega 
@bp_calificacion.route("/entrega/<int:entrega_id>/calificar", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def calificar(entrega_id):
    entrega = Entrega.query.get(entrega_id)
    curso = entrega.tarea.modulo.curso

    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes calificar entregas de un curso que no te pertenece.", "danger")
        return redirect(url_for("curso.listar"))

    if request.method == "POST":
        nota = float(request.form["nota"])
        retroalimentacion = request.form.get("retroalimentacion", "").strip()
        puntaje_maximo = entrega.tarea.puntaje_maximo

        if nota < 0 or nota > puntaje_maximo:
            flash(f"La nota debe estar entre 0 y {puntaje_maximo}.", "danger")
            return redirect(url_for("calificacion.calificar", entrega_id=entrega_id))

        if entrega.calificacion:
            nota_anterior = entrega.calificacion.nota
            entrega.calificacion.nota = nota
            entrega.calificacion.retroalimentacion = retroalimentacion
            entrega.calificacion.docente_id = current_user.id

            if nota != nota_anterior:
                historial = HistorialCalificacion(
                    calificacion_id=entrega.calificacion.id,
                    nota_anterior=nota_anterior,
                    nota_nueva=nota,
                    docente_id=current_user.id,
                )
                db.session.add(historial)
        else:
            nueva_calificacion = Calificacion(
                entrega_id=entrega_id,
                docente_id=current_user.id,
                nota=nota,
                retroalimentacion=retroalimentacion,
            )
            db.session.add(nueva_calificacion)

        entrega.estado = "revisado"
        db.session.commit()

        registrar_log(
            "Calificar Entrega",
            f"Entrega #{entrega_id} calificada con nota {nota}/{puntaje_maximo}",
        )
        flash("Calificación guardada exitosamente.", "success")
        return redirect(url_for("entrega.listar", tarea_id=entrega.tarea_id))

    return render_template("calificaciones/calificar.html", entrega=entrega, DIMENSIONES=DIMENSIONES)


# Vista docente: resumen de notas del curso 
@bp_calificacion.route("/curso/<int:curso_id>/notas")
@login_required
@role_required("admin", "docente")
def ver_notas_curso(curso_id):
    curso = Curso.query.get(curso_id)
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes ver notas de un curso que no te pertenece.", "danger")
        return redirect(url_for("curso.listar"))

    trimestre = request.args.get("trimestre", type=int) or 1

    inscripciones = Inscripcion.query.filter_by(curso_id=curso_id).all()

    # Resumen de puntos disponibles por dimensión para el trimestre
    disponibilidad = {}
    for dim, info in DIMENSIONES.items():
        usados = puntos_usados_dimension(curso_id, trimestre, dim)
        disponibilidad[dim] = {
            "usados": usados,
            "max": info["max"],
            "disponibles": info["max"] - usados,
            "label": info["label"],
        }

    # Notas de cada estudiante
    notas_data = []
    for insc in inscripciones:
        est = insc.estudiante
        fila = {"estudiante": est}
        for dim in DIMENSIONES:
            fila[dim] = nota_estudiante_dimension(est.id, curso_id, trimestre, dim)
        fila["total"] = sum(fila[dim] for dim in DIMENSIONES)
        notas_data.append(fila)

    return render_template(
        "calificaciones/notas_curso.html",
        curso=curso,
        trimestre=trimestre,
        notas_data=notas_data,
        disponibilidad=disponibilidad,
        DIMENSIONES=DIMENSIONES,
    )


#  Vista docente: detalle por estudiante 
@bp_calificacion.route("/curso/<int:curso_id>/estudiante/<int:estudiante_id>")
@login_required
@role_required("admin", "docente")
def detalle_estudiante(curso_id, estudiante_id):
    curso = Curso.query.get(curso_id)
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes ver notas de un curso que no te pertenece.", "danger")
        return redirect(url_for("curso.listar"))
    from app.usuarios.models import Usuario

    estudiante = Usuario.query.get(estudiante_id)

    trimestre = request.args.get("trimestre", type=int) or 1

    tareas = (
        Tarea.query.join(Modulo)
        .filter(Modulo.curso_id == curso_id, Tarea.trimestre == trimestre)
        .order_by(Tarea.dimension, Tarea.fecha_limite)
        .all()
    )

    tareas_con_nota = []
    for t in tareas:
        entrega = Entrega.query.filter_by(
            tarea_id=t.id, estudiante_id=estudiante_id
        ).first()
        nota = None
        retro = None
        if entrega and entrega.calificacion:
            nota = entrega.calificacion.nota
            retro = entrega.calificacion.retroalimentacion
        tareas_con_nota.append({
            "tarea": t,
            "nota": nota,
            "retroalimentacion": retro,
            "max": t.puntaje_maximo,
            "entregada": entrega is not None,
        })

    # Agregar autoevaluacion
    config = AutoevaluacionConfig.query.filter_by(curso_id=curso_id, trimestre=trimestre, activo=True).first()
    if config:
        resp = RespuestaAutoevaluacion.query.filter_by(config_id=config.id, estudiante_id=estudiante_id).first()
        if resp:
            tareas_con_nota.append({
                "tarea": None,
                "nota": resp.nota_final or 0,
                "retroalimentacion": resp.retroalimentacion,
                "max": 5,
                "entregada": True,
                "autoevaluacion_puntaje": resp.puntaje,
                "autoevaluacion": True,
            })

    # Resumen por dimensión
    resumen = {}
    for dim, info in DIMENSIONES.items():
        if dim == "autoevaluacion":
            continue
        subtareas = [tc for tc in tareas_con_nota if tc["tarea"] is not None and tc["tarea"].dimension == dim]
        total_nota = sum(tc["nota"] or 0 for tc in subtareas)
        total_max = sum(tc["max"] for tc in subtareas)
        resumen[dim] = {
            "label": info["label"],
            "subtitle": info["subtitle"],
            "nota": total_nota,
            "max": info["max"],
            "total_tareas": total_max,
            "tareas": [tc for tc in tareas_con_nota if tc["tarea"] is not None and tc["tarea"].dimension == dim],
        }

    return render_template(
        "calificaciones/detalle_estudiante.html",
        curso=curso,
        estudiante=estudiante,
        trimestre=trimestre,
        resumen=resumen,
        DIMENSIONES=DIMENSIONES,
    )


# Mis notas para estudiante 
@bp_calificacion.route("/mis-notas")
@login_required
@role_required("estudiante")
def mis_notas():
    inscripciones = Inscripcion.query.filter_by(estudiante_id=current_user.id).all()

    cursos_notas = []
    for insc in inscripciones:
        curso = insc.curso
        trimestres = []
        nota_final_sum = 0
        nota_final_count = 0
        for t in [1, 2, 3]:
            resumen = resumen_estudiante_curso(current_user.id, curso.id, t)
            total_dim = sum(r["nota"] for r in resumen.values())
            trimestres.append({
                "trimestre": t,
                "resumen": resumen,
                "total": total_dim,
            })
            if total_dim > 0:
                nota_final_sum += total_dim
                nota_final_count += 1

        cursos_notas.append({
            "curso": curso,
            "trimestres": trimestres,
            "nota_final": round(nota_final_sum / nota_final_count, 1) if nota_final_count > 0 else None,
        })

    return render_template(
        "calificaciones/mis_notas.html",
        cursos_notas=cursos_notas,
        DIMENSIONES=DIMENSIONES,
    )

@bp_calificacion.route("/curso/<int:curso_id>/mis-notas")
@login_required
@role_required("estudiante")
def mis_notas_curso(curso_id):
    curso = Curso.query.get(curso_id)
    inscrito = Inscripcion.query.filter_by(curso_id=curso_id, estudiante_id=current_user.id).first()
    if not inscrito:
        flash("No estás inscrito en este curso.", "danger")
        return redirect(url_for("curso.listar"))

    trimestres = []
    nota_final_sum = 0
    nota_final_count = 0
    for t in [1, 2, 3]:
        resumen = resumen_estudiante_curso(current_user.id, curso.id, t)
        total_dim = sum(r["nota"] for r in resumen.values())
        # Tareas con nota para este trimestre
        tareas_con_nota = (
            db.session.query(Tarea, Calificacion)
            .join(Modulo)
            .join(Entrega, Entrega.tarea_id == Tarea.id)
            .join(Calificacion, Calificacion.entrega_id == Entrega.id)
            .filter(
                Modulo.curso_id == curso_id,
                Tarea.trimestre == t,
                Entrega.estudiante_id == current_user.id,
            )
            .order_by(Tarea.dimension, Tarea.fecha_limite)
            .all()
        )
        tareas_data = []
        for tarea, calif in tareas_con_nota:
            tareas_data.append({
                "tarea": tarea,
                "nota": calif.nota,
                "max": tarea.puntaje_maximo,
                "retroalimentacion": calif.retroalimentacion,
                "dimension": DIMENSIONES[tarea.dimension]["label"],
                "dim_key": tarea.dimension,
            })
        # Agregar autoevaluacion
        config = AutoevaluacionConfig.query.filter_by(curso_id=curso_id, trimestre=t, activo=True).first()
        if config:
            resp = RespuestaAutoevaluacion.query.filter_by(config_id=config.id, estudiante_id=current_user.id).first()
            if resp:
                tareas_data.append({
                    "tarea": None,
                    "nota": resp.nota_final or 0,
                    "max": 5,
                    "retroalimentacion": resp.retroalimentacion,
                    "dimension": DIMENSIONES["autoevaluacion"]["label"],
                    "dim_key": "autoevaluacion",
                    "autoevaluacion_puntaje": resp.puntaje,
                })
        trimestres.append({
            "trimestre": t,
            "resumen": resumen,
            "total": total_dim,
            "tareas": tareas_data,
        })
        if total_dim > 0:
            nota_final_sum += total_dim
            nota_final_count += 1

    return render_template(
        "calificaciones/mis_notas_curso.html",
        curso=curso,
        trimestres=trimestres,
        nota_final=round(nota_final_sum / nota_final_count, 1) if nota_final_count > 0 else None,
        DIMENSIONES=DIMENSIONES,
    )
