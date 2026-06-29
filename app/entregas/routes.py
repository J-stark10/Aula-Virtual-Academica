from datetime import datetime
from flask import Blueprint, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from app.app import db
from app.cursos.models import Inscripcion
from app.tareas.models import Tarea
from app.entregas.models import Entrega
from app.utils import guardar_archivo, registrar_log, role_required

bp_entrega = Blueprint("entrega", __name__, template_folder="templates")


@bp_entrega.route("/tarea/<int:tarea_id>/enviar", methods=["GET", "POST"])
@login_required
@role_required("estudiante")
def enviar(tarea_id):
    tarea = Tarea.query.get(tarea_id)
    curso = tarea.modulo.curso

    inscrito = Inscripcion.query.filter_by(
        curso_id=curso.id, estudiante_id=current_user.id
    ).first()
    if not inscrito:
        flash("No estás inscrito en este curso.", "danger")
        return redirect(url_for("curso.listar"))

    entrega_existente = Entrega.query.filter_by(
        tarea_id=tarea_id, estudiante_id=current_user.id
    ).first()

    if request.method == "POST":
        comentario = request.form.get("comentario", "").strip()
        archivo_subido = request.files.get("archivo")

        ruta_archivo = guardar_archivo(archivo_subido, "entregas")
        if not ruta_archivo and not entrega_existente:
            flash("Debes adjuntar un archivo para tu entrega.", "danger")
            return redirect(url_for("entrega.enviar", tarea_id=tarea_id))

        if entrega_existente:
            if ruta_archivo:
                entrega_existente.archivo = ruta_archivo
            entrega_existente.comentario = comentario
            entrega_existente.estado = "entregado"
            entrega_existente.fecha_entrega = datetime.utcnow()
            db.session.commit()
            registrar_log(
                "Reenviar Entrega", f"Entrega actualizada para tarea '{tarea.titulo}'"
            )
            flash("Tu entrega fue actualizada exitosamente.", "success")
        else:
            nueva = Entrega(
                tarea_id=tarea_id,
                estudiante_id=current_user.id,
                archivo=ruta_archivo,
                comentario=comentario,
                estado="entregado",
            )
            db.session.add(nueva)
            db.session.commit()
            registrar_log(
                "Crear Entrega", f"Entrega registrada para tarea '{tarea.titulo}'"
            )
            flash("Tu tarea fue entregada exitosamente.", "success")

        return redirect(url_for("tarea.detalle", id=tarea_id))

    return render_template(
        "entregas/enviar.html", tarea=tarea, entrega_existente=entrega_existente
    )


@bp_entrega.route("/tarea/<int:tarea_id>/listar")
@login_required
@role_required("admin", "docente")
def listar(tarea_id):
    tarea = Tarea.query.get(tarea_id)
    curso = tarea.modulo.curso

    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes ver las entregas de un curso que no te pertenece.", "danger")
        return redirect(url_for("curso.listar"))

    entregas = Entrega.query.filter_by(tarea_id=tarea_id).all()
    entregados_ids = {e.estudiante_id for e in entregas}

    pendientes = [
        insc.estudiante
        for insc in curso.inscripciones
        if insc.estudiante_id not in entregados_ids
    ]

    return render_template(
        "entregas/listar.html", tarea=tarea, entregas=entregas, pendientes=pendientes
    )


@bp_entrega.route("/delete/<int:entrega_id>")
def eliminar(entrega_id):
    entrega = Entrega.query.get(entrega_id)
    db.session.delete(entrega)
    db.session.commit()
    registrar_log("Eliminar Entrega", f"Entrega #{entrega.id} eliminada")
    flash("Entrega eliminada exitosamente.", "success")
    return redirect(url_for("entrega.listar", tarea_id=entrega.tarea_id))


@bp_entrega.route("/descargar/<path:ruta_relativa>")
@login_required
@role_required("admin", "docente")
def descargar(ruta_relativa):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], ruta_relativa)

