from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.app import db
from app.cursos.models import Curso
from app.anuncios.models import Anuncio
from app.utils import registrar_log, role_required

bp_anuncio = Blueprint("anuncio", __name__, template_folder="templates")

def _verificar_propietario(curso):
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes gestionar anuncios de un curso que no te pertenece.", "danger")
        return False
    return True

@bp_anuncio.route("/curso/<int:curso_id>/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def crear(curso_id):
    curso = Curso.query.get(curso_id)
    if not _verificar_propietario(curso):
        return redirect(url_for("curso.listar"))

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        contenido = request.form["contenido"].strip()

        if not titulo or not contenido:
            flash("El título y el contenido son requeridos.", "danger")
            return redirect(url_for("anuncio.crear", curso_id=curso_id))

        nuevo = Anuncio(curso_id=curso_id, titulo=titulo, contenido=contenido)
        db.session.add(nuevo)
        db.session.commit()

        registrar_log("Crear Anuncio", f"Anuncio '{titulo}' publicado en curso '{curso.nombre}'")
        flash("Anuncio publicado exitosamente.", "success")
        return redirect(url_for("curso.detalle", id=curso_id))

    return render_template("anuncios/crear.html", curso=curso)


@bp_anuncio.route("/delete/<int:id>")
def eliminar(id):
    item = Anuncio.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("curso.detalle", id=item.curso_id))
