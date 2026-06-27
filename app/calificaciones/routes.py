from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.app import db
from app.entregas.models import Entrega
from app.calificaciones.models import Calificacion
from app.cursos.models import Curso, Inscripcion
from app.tareas.models import Tarea
from app.modulos.models import Modulo
from app.utils import registrar_log, role_required

bp_calificacion = Blueprint("calificacion", __name__, template_folder="templates")

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
            entrega.calificacion.nota = nota
            entrega.calificacion.retroalimentacion = retroalimentacion
            entrega.calificacion.docente_id = current_user.id
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

    return render_template("calificaciones/calificar.html", entrega=entrega)

def nota_final_estudiante(estudiante_id, curso_id):
    modulos = Modulo.query.filter_by(curso_id=curso_id).all()
    nota_total = 0
    max_total = 0
    for modulo in modulos:
        tareas = Tarea.query.filter_by(modulo_id=modulo.id).all()
        for tarea in tareas:
            entrega = Entrega.query.filter_by(
                tarea_id=tarea.id, estudiante_id=estudiante_id
            ).first()
            if entrega and entrega.calificacion:
                max_total += tarea.puntaje_maximo
                nota_total += entrega.calificacion.nota
    return round((nota_total / max_total) * 100, 1) if max_total > 0 else None


@bp_calificacion.route("/curso/<int:curso_id>/notas")
@login_required
@role_required("admin", "docente")
def ver_notas_curso(curso_id):
    curso = Curso.query.get(curso_id)
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes ver notas de un curso que no te pertenece.", "danger")
        return redirect(url_for("curso.listar"))

    inscripciones = Inscripcion.query.filter_by(curso_id=curso_id).all()

    notas_data = []
    for insc in inscripciones:
        est = insc.estudiante
        nota_final = nota_final_estudiante(est.id, curso_id)
        notas_data.append({
            "estudiante": est,
            "nota_final": nota_final,
        })

    return render_template(
        "calificaciones/notas_curso.html",
        curso=curso,
        notas_data=notas_data,
    )


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

    modulos = Modulo.query.filter_by(curso_id=curso_id).all()
    modulo_ids = [m.id for m in modulos]

    tareas = (
        Tarea.query.filter(Tarea.modulo_id.in_(modulo_ids))
        .order_by(Tarea.fecha_limite)
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

    nota_final = nota_final_estudiante(estudiante_id, curso_id)

    return render_template(
        "calificaciones/detalle_estudiante.html",
        curso=curso,
        estudiante=estudiante,
        tareas_con_nota=tareas_con_nota,
        nota_final=nota_final,
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

    modulos = Modulo.query.filter_by(curso_id=curso.id).all()
    modulo_ids = [m.id for m in modulos]
    tareas = (
        Tarea.query.filter(Tarea.modulo_id.in_(modulo_ids))
        .order_by(Tarea.fecha_limite)
        .all()
    )

    tareas_data = []
    for tarea in tareas:
        entrega = Entrega.query.filter_by(
            tarea_id=tarea.id, estudiante_id=current_user.id
        ).first()
        if entrega and entrega.calificacion:
            tareas_data.append({
                "tarea": tarea,
                "nota": entrega.calificacion.nota,
                "max": tarea.puntaje_maximo,
                "retroalimentacion": entrega.calificacion.retroalimentacion,
            })

    nota_final = nota_final_estudiante(current_user.id, curso_id)

    return render_template(
        "calificaciones/mis_notas_curso.html",
        curso=curso,
        tareas=tareas_data,
        nota_final=nota_final,
    )