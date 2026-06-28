from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.app import db
from app.cursos.models import Curso
from app.modulos.models import Modulo
from app.utils import registrar_log, role_required

bp_modulo = Blueprint("modulo", __name__, template_folder="templates")


def _verificar_propietario(curso):
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes gestionar módulos de un curso que no te pertenece.", "danger")
        return False
    return True


@bp_modulo.route("/curso/<int:curso_id>/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def crear(curso_id):
    curso = Curso.query.get(curso_id)
    if not _verificar_propietario(curso):
        return redirect(url_for("curso.listar"))

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        descripcion = request.form.get("descripcion", "").strip()
        orden = int(request.form.get("orden", 1))

        if not titulo:
            flash("El título del módulo es requerido.", "danger")
            return redirect(url_for("modulo.crear", curso_id=curso_id))

        nuevo = Modulo(
            curso_id=curso_id, titulo=titulo, descripcion=descripcion, orden=orden
        )
        db.session.add(nuevo)
        db.session.commit()

        registrar_log("Crear Módulo", f"Módulo '{titulo}' creado en curso '{curso.nombre}'")
        flash("Módulo creado exitosamente.", "success")
        return redirect(url_for("curso.detalle", id=curso_id))

    return render_template("modulos/crear.html", curso=curso)


@bp_modulo.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def editar(id):
    item = Modulo.query.get(id)
    if not _verificar_propietario(item.curso):
        return redirect(url_for("curso.listar"))

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        descripcion = request.form.get("descripcion", "").strip()
        orden = int(request.form.get("orden", 1))

        if not titulo:
            flash("El título del módulo es requerido.", "danger")
            return redirect(url_for("modulo.editar", id=id))

        item.titulo = titulo
        item.descripcion = descripcion
        item.orden = orden
        db.session.commit()

        registrar_log("Editar Módulo", f"Módulo ID {id} actualizado: {titulo}")
        flash("Módulo actualizado exitosamente.", "success")
        return redirect(url_for("curso.detalle", id=item.curso_id))

    return render_template("modulos/editar.html", item=item)


@bp_modulo.route("/delete/<int:id>")
def eliminar(id):
    item = Modulo.query.get(id)
    db.session.delete(item)
    db.session.commit()
    registrar_log("Eliminar Módulo", f"Módulo '{item.titulo}' eliminado del curso ID {item.curso_id}")
    flash("Módulo eliminado exitosamente.", "success")
    return redirect(url_for("curso.detalle", id=item.curso_id))
