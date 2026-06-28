from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, send_from_directory
from flask_login import current_user, login_required
from app.app import db
from app.modulos.models import Modulo
from app.recursos.models import Recurso
from app.utils import guardar_archivo, registrar_log, role_required

bp_recurso = Blueprint("recurso", __name__, template_folder="templates")

def _verificar_propietario(curso):
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes gestionar recursos de un curso que no te pertenece.", "danger")
        return False
    return True

@bp_recurso.route("/modulo/<int:modulo_id>/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def crear(modulo_id):
    modulo = Modulo.query.get(modulo_id)
    if not _verificar_propietario(modulo.curso):
        return redirect(url_for("curso.listar"))

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        tipo = request.form["tipo"]
        url_enlace = request.form.get("url_enlace", "").strip()

        if not titulo:
            flash("El título del recurso es requerido.", "danger")
            return redirect(url_for("recurso.crear", modulo_id=modulo_id))

        ruta_pdf = None
        ruta_video = None

        if tipo == "pdf":
            archivo_pdf = request.files.get("archivo_pdf")
            ruta_pdf = guardar_archivo(archivo_pdf, "recursos")
            if not ruta_pdf:
                flash("Debes subir un archivo PDF.", "danger")
                return redirect(url_for("recurso.crear", modulo_id=modulo_id))

        elif tipo == "video":
            archivo_video = request.files.get("archivo_video")
            ruta_video = guardar_archivo(archivo_video, "recursos")
            if not ruta_video:
                flash("Debes subir un archivo de video.", "danger")
                return redirect(url_for("recurso.crear", modulo_id=modulo_id))

        elif tipo == "enlace":
            if not url_enlace:
                flash("Debes proporcionar una URL para el enlace.", "danger")
                return redirect(url_for("recurso.crear", modulo_id=modulo_id))

        nuevo = Recurso(
            modulo_id=modulo_id,
            titulo=titulo,
            tipo=tipo,
            archivo_pdf=ruta_pdf,
            archivo_video=ruta_video,
            url_enlace=url_enlace if tipo == "enlace" else None,
        )
        db.session.add(nuevo)
        db.session.commit()

        registrar_log("Crear Recurso", f"Recurso '{titulo}' ({tipo}) creado en módulo '{modulo.titulo}'")
        flash("Recurso publicado exitosamente.", "success")
        return redirect(url_for("curso.detalle", id=modulo.curso_id))

    return render_template("recursos/crear.html", modulo=modulo)

@bp_recurso.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def editar(id):
    item = Recurso.query.get(id)
    if not _verificar_propietario(item.modulo.curso):
        return redirect(url_for("curso.listar"))

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        url_enlace = request.form.get("url_enlace", "").strip()

        if not titulo:
            flash("El título del recurso es requerido.", "danger")
            return redirect(url_for("recurso.editar", id=id))

        item.titulo = titulo

        if item.tipo == "pdf":
            archivo_pdf = request.files.get("archivo_pdf")
            nueva_ruta = guardar_archivo(archivo_pdf, "recursos")
            if nueva_ruta:
                item.archivo_pdf = nueva_ruta
        elif item.tipo == "video":
            archivo_video = request.files.get("archivo_video")
            nueva_ruta = guardar_archivo(archivo_video, "recursos")
            if nueva_ruta:
                item.archivo_video = nueva_ruta
        elif item.tipo == "enlace":
            item.url_enlace = url_enlace

        db.session.commit()

        registrar_log("Editar Recurso", f"Recurso ID {id} actualizado: {titulo}")
        flash("Recurso actualizado exitosamente.", "success")
        return redirect(url_for("curso.detalle", id=item.modulo.curso_id))

    return render_template("recursos/editar.html", item=item)

@bp_recurso.route("/delete/<int:id>")
def eliminar(id):
    item = Recurso.query.get(id)

    curso_id = item.modulo.curso_id

    db.session.delete(item)
    db.session.commit()
    registrar_log("Eliminar Recurso", f"Recurso '{item.titulo}' eliminado")
    flash("Recurso eliminado exitosamente.", "success")
    return redirect(url_for("curso.detalle", id=curso_id))

@bp_recurso.route("/descargar/<path:ruta_relativa>")
@login_required
def descargar(ruta_relativa):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], ruta_relativa)

