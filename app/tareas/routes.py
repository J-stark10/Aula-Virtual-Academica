from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.app import db
from app.modulos.models import Modulo
from app.tareas.models import Tarea, DIMENSIONES
from app.calificaciones.helpers import puntos_usados_dimension, puntos_disponibles_dimension
from app.utils import registrar_log, role_required

bp_tarea = Blueprint("tarea", __name__, template_folder="templates")


def _verificar_propietario(curso):
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes gestionar tareas de un curso que no te pertenece.", "danger")
        return False
    return True


@bp_tarea.route("/modulo/<int:modulo_id>/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def crear(modulo_id):
    modulo = Modulo.query.get(modulo_id)
    if not _verificar_propietario(modulo.curso):
        return redirect(url_for("curso.listar"))

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        instrucciones = request.form.get("instrucciones", "").strip()
        fecha_limite_str = request.form["fecha_limite"]
        puntaje_maximo = float(request.form.get("puntaje_maximo", 100))
        trimestre = int(request.form.get("trimestre", 1))
        dimension = request.form.get("dimension", "saber")

        if not titulo or not fecha_limite_str:
            flash("El título y la fecha límite son requeridos.", "danger")
            return redirect(url_for("tarea.crear", modulo_id=modulo_id))

        if dimension not in DIMENSIONES:
            flash("Dimensión inválida.", "danger")
            return redirect(url_for("tarea.crear", modulo_id=modulo_id))

        disponibles = puntos_disponibles_dimension(modulo.curso_id, trimestre, dimension)
        if puntaje_maximo > disponibles:
            flash(
                f"No es posible crear la tarea. Solo quedan {disponibles:.0f} puntos "
                f"disponibles para la dimensión {DIMENSIONES[dimension]['label']} en este trimestre.",
                "danger",
            )
            return redirect(url_for("tarea.crear", modulo_id=modulo_id))

        fecha_limite = datetime.strptime(fecha_limite_str, "%Y-%m-%dT%H:%M")

        nueva = Tarea(
            modulo_id=modulo_id,
            titulo=titulo,
            instrucciones=instrucciones,
            fecha_limite=fecha_limite,
            puntaje_maximo=puntaje_maximo,
            trimestre=trimestre,
            dimension=dimension,
        )
        db.session.add(nueva)
        db.session.commit()

        registrar_log("Crear Tarea", f"Tarea '{titulo}' creada en módulo '{modulo.titulo}'")
        flash("Tarea publicada exitosamente.", "success")
        return redirect(url_for("curso.detalle", id=modulo.curso_id))

    disponibles_por_trimestre = {}
    for t in [1, 2, 3]:
        disponibles_por_trimestre[t] = {}
        for dim, info in DIMENSIONES.items():
            disponibles_por_trimestre[t][dim] = {
                "usados": puntos_usados_dimension(modulo.curso_id, t, dim),
                "max": info["max"],
                "label": info["label"],
            }

    return render_template(
        "tareas/crear.html", modulo=modulo,
        disponibles_por_trimestre=disponibles_por_trimestre,
        DIMENSIONES=DIMENSIONES,
    )


@bp_tarea.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def editar(id):
    item = Tarea.query.get(id)
    if not _verificar_propietario(item.modulo.curso):
        return redirect(url_for("curso.listar"))

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        instrucciones = request.form.get("instrucciones", "").strip()
        fecha_limite_str = request.form["fecha_limite"]
        puntaje_maximo = float(request.form.get("puntaje_maximo", 100))
        trimestre = int(request.form.get("trimestre", 1))
        dimension = request.form.get("dimension", item.dimension)

        if not titulo or not fecha_limite_str:
            flash("El título y la fecha límite son requeridos.", "danger")
            return redirect(url_for("tarea.editar", id=id))

        if dimension not in DIMENSIONES:
            flash("Dimensión inválida.", "danger")
            return redirect(url_for("tarea.editar", id=id))

        curso_id = item.modulo.curso_id
        if dimension == item.dimension and trimestre == item.trimestre:
            diff = puntaje_maximo - item.puntaje_maximo
            disponibles = puntos_disponibles_dimension(curso_id, trimestre, dimension)
            if diff > 0 and diff > disponibles:
                flash(
                    f"No es posible actualizar la tarea. Solo quedan {disponibles:.0f} puntos "
                    f"disponibles para la dimensión {DIMENSIONES[dimension]['label']} en este trimestre.",
                    "danger",
                )
                return redirect(url_for("tarea.editar", id=id))

        item.titulo = titulo
        item.instrucciones = instrucciones
        item.fecha_limite = datetime.strptime(fecha_limite_str, "%Y-%m-%dT%H:%M")
        item.puntaje_maximo = puntaje_maximo
        item.trimestre = trimestre
        item.dimension = dimension
        db.session.commit()

        registrar_log("Editar Tarea", f"Tarea ID {id} actualizada: {titulo}")
        flash("Tarea actualizada exitosamente.", "success")
        return redirect(url_for("curso.detalle", id=curso_id))

    return render_template("tareas/editar.html", item=item, DIMENSIONES=DIMENSIONES)


@bp_tarea.route("/delete/<int:id>")
def eliminar(id):
    item = Tarea.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("curso.detalle", id=item.modulo.curso_id))


@bp_tarea.route("/detalle/<int:id>")
@login_required
def detalle(id):
    item = Tarea.query.get(id)
    curso = item.modulo.curso

    es_docente_propietario = current_user.rol == "docente" and curso.docente_id == current_user.id
    es_admin = current_user.rol == "admin"
    es_estudiante_inscrito = any(
        i.estudiante_id == current_user.id for i in curso.inscripciones
    )

    if not (es_docente_propietario or es_admin or es_estudiante_inscrito):
        flash("No tienes acceso a esta tarea.", "danger")
        return redirect(url_for("curso.listar"))

    entrega_propia = None
    if current_user.rol == "estudiante":
        entrega_propia = next(
            (e for e in item.entregas if e.estudiante_id == current_user.id), None
        )

    return render_template(
        "tareas/detalle.html", item=item, entrega_propia=entrega_propia, DIMENSIONES=DIMENSIONES
    )
