from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.app import db
from app.usuarios.models import Usuario
from app.categoria.models import Categoria
from app.cursos.models import Curso, Inscripcion, generar_codigo_unico
from app.tareas.models import Tarea
from app.modulos.models import Modulo
from app.entregas.models import Entrega, AutoevaluacionConfig, RespuestaAutoevaluacion
from app.utils import registrar_log, role_required

bp_curso = Blueprint("curso", __name__, template_folder="templates")


def _cursos_visibles_para(usuario):
    """Devuelve el query de cursos según el rol del usuario autenticado."""
    if usuario.rol == "admin":
        return Curso.query
    if usuario.rol == "docente":
        return Curso.query.filter_by(docente_id=usuario.id)
    # estudiante: solo cursos donde está inscrito
    return (
        Curso.query.join(Inscripcion)
        .filter(Inscripcion.estudiante_id == usuario.id)
    )


@bp_curso.route("/")
@login_required
def listar():
    categoria_id = request.args.get("categoria", type=int)
    query = _cursos_visibles_para(current_user)
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    items = query.order_by(Curso.fecha_creacion.desc()).all()
    categorias = Categoria.query.all()
    return render_template("cursos/listar.html", items=items, categorias=categorias, categoria_filtro=categoria_id)


@bp_curso.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def crear():
    categorias = Categoria.query.all()
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria_id = int(request.form["categoria_id"])

        if not nombre:
            flash("El nombre del curso es requerido.", "danger")
            return redirect(url_for("curso.crear"))

        nuevo = Curso(
            nombre=nombre,
            descripcion=descripcion,
            categoria_id=categoria_id,
            docente_id=current_user.id,
            codigo=generar_codigo_unico(),
        )
        db.session.add(nuevo)
        db.session.commit()

        registrar_log("Crear Curso", f"Curso creado: {nombre}")
        flash(f"Curso creado exitosamente. Código de acceso: {nuevo.codigo}", "success")
        return redirect(url_for("curso.listar"))

    return render_template("cursos/crear.html", categorias=categorias)


@bp_curso.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def editar(id):
    item = Curso.query.get(id)
    if current_user.rol == "docente" and item.docente_id != current_user.id:
        flash("No puedes editar un curso que no te pertenece.", "danger")
        return redirect(url_for("curso.listar"))

    categorias = Categoria.query.all()
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria_id = int(request.form["categoria_id"])
        activo = request.form.get("activo") == "on"

        if not nombre:
            flash("El nombre del curso es requerido.", "danger")
            return redirect(url_for("curso.editar", id=id))

        item.nombre = nombre
        item.descripcion = descripcion
        item.categoria_id = categoria_id
        item.activo = activo
        db.session.commit()

        registrar_log("Editar Curso", f"Curso ID {id} actualizado: {nombre}")
        flash("Curso actualizado exitosamente.", "success")
        return redirect(url_for("curso.listar"))

    return render_template("cursos/editar.html", item=item, categorias=categorias)


@bp_curso.route("/delete/<int:id>")
def eliminar(id):
    item = Curso.query.get(id)
    db.session.delete(item)
    db.session.commit()
    flash("Curso eliminado exitosamente.", "success")
    return redirect(url_for("curso.listar"))


@bp_curso.route("/detalle/<int:id>")
@login_required
def detalle(id):
    curso = Curso.query.get(id)

    es_docente_propietario = current_user.rol == "docente" and curso.docente_id == current_user.id
    es_admin = current_user.rol == "admin"
    es_estudiante_inscrito = any(
        i.estudiante_id == current_user.id for i in curso.inscripciones
    )

    if not (es_docente_propietario or es_admin or es_estudiante_inscrito):
        flash("No tienes acceso a este curso.", "danger")
        return redirect(url_for("curso.listar"))

    autoevaluaciones = {}
    for t in [1, 2, 3]:
        config = AutoevaluacionConfig.query.filter_by(curso_id=id, trimestre=t).first()
        if config:
            respuesta = None
            if current_user.rol == "estudiante":
                respuesta = RespuestaAutoevaluacion.query.filter_by(
                    config_id=config.id, estudiante_id=current_user.id
                ).first()
            autoevaluaciones[t] = {"config": config, "respuesta": respuesta}
        else:
            autoevaluaciones[t] = None

    return render_template("cursos/detalle.html", curso=curso, autoevaluaciones=autoevaluaciones)


# --- Inscripción de estudiantes mediante código ---

@bp_curso.route("/unirse", methods=["GET", "POST"])
@login_required
@role_required("estudiante")
def unirse():
    if request.method == "POST":
        codigo = request.form["codigo"].strip()

        if not codigo or not codigo.isdigit() or len(codigo) != 6:
            flash("El código debe tener 6 dígitos.", "danger")
            return redirect(url_for("curso.unirse"))

        curso = Curso.query.filter_by(codigo=codigo, activo=True).first()
        if not curso:
            flash("Código inválido o el curso no está activo.", "danger")
            return redirect(url_for("curso.unirse"))

        ya_inscrito = Inscripcion.query.filter_by(
            curso_id=curso.id, estudiante_id=current_user.id
        ).first()
        if ya_inscrito:
            flash("Ya estás inscrito en este curso.", "warning")
            return redirect(url_for("curso.listar"))

        nueva = Inscripcion(curso_id=curso.id, estudiante_id=current_user.id)
        db.session.add(nueva)
        db.session.commit()

        registrar_log(
            "Inscribir Estudiante",
            f"Estudiante {current_user.email} inscrito por código en curso '{curso.nombre}'",
        )
        flash(f"Te has inscrito exitosamente al curso '{curso.nombre}'.", "success")
        return redirect(url_for("curso.listar"))

    return render_template("cursos/unirse.html")


# --- Gestión de inscripciones (solo docentes/admin, muestra el código) ---

@bp_curso.route("/<int:curso_id>/autoevaluacion/activar", methods=["POST"])
@login_required
@role_required("admin", "docente")
def activar_autoevaluacion(curso_id):
    curso = Curso.query.get(curso_id)
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes gestionar este curso.", "danger")
        return redirect(url_for("curso.listar"))

    trimestre = request.form.get("trimestre", type=int) or 1

    config = AutoevaluacionConfig.query.filter_by(curso_id=curso_id, trimestre=trimestre).first()
    if config:
        if config.activo:
            flash(f"La autoevaluación del {trimestre}° Trimestre ya está activa.", "warning")
        else:
            config.activo = True
            db.session.commit()
            registrar_log("Activar Autoevaluación", f"Autoevaluación T{trimestre} activada en curso '{curso.nombre}'")
            flash(f"Autoevaluación del {trimestre}° Trimestre activada.", "success")
    else:
        config = AutoevaluacionConfig(curso_id=curso_id, trimestre=trimestre, activo=True)
        db.session.add(config)
        db.session.commit()
        registrar_log("Activar Autoevaluación", f"Autoevaluación T{trimestre} activada en curso '{curso.nombre}'")
        flash(f"Autoevaluación del {trimestre}° Trimestre activada exitosamente.", "success")

    return redirect(url_for("curso.detalle", id=curso_id))


@bp_curso.route("/<int:curso_id>/autoevaluacion/desactivar", methods=["POST"])
@login_required
@role_required("admin", "docente")
def desactivar_autoevaluacion(curso_id):
    curso = Curso.query.get(curso_id)
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes gestionar este curso.", "danger")
        return redirect(url_for("curso.listar"))

    trimestre = request.form.get("trimestre", type=int) or 1

    config = AutoevaluacionConfig.query.filter_by(curso_id=curso_id, trimestre=trimestre).first()
    if config:
        config.activo = False
        db.session.commit()
        registrar_log("Desactivar Autoevaluación", f"Autoevaluación T{trimestre} desactivada en curso '{curso.nombre}'")
        flash(f"Autoevaluación del {trimestre}° Trimestre desactivada. Los estudiantes ya no pueden modificarla.", "success")
    else:
        flash("No hay autoevaluación activa para este trimestre.", "warning")

    return redirect(url_for("curso.detalle", id=curso_id))


@bp_curso.route("/<int:curso_id>/autoevaluacion/<int:trimestre>", methods=["GET", "POST"])
@login_required
@role_required("estudiante")
def autoevaluacion_form(curso_id, trimestre):
    curso = Curso.query.get(curso_id)
    inscrito = Inscripcion.query.filter_by(curso_id=curso_id, estudiante_id=current_user.id).first()
    if not inscrito:
        flash("No estás inscrito en este curso.", "danger")
        return redirect(url_for("curso.listar"))

    config = AutoevaluacionConfig.query.filter_by(curso_id=curso_id, trimestre=trimestre).first()
    if not config or not config.activo:
        flash("La autoevaluación no está activa para este trimestre.", "warning")
        return redirect(url_for("curso.detalle", id=curso_id))

    respuesta = RespuestaAutoevaluacion.query.filter_by(config_id=config.id, estudiante_id=current_user.id).first()

    if request.method == "POST":
        puntaje = request.form.get("puntaje_autoevaluacion", type=float)
        if puntaje is None or puntaje < 0 or puntaje > 5:
            flash("El puntaje debe estar entre 0 y 5.", "danger")
            return redirect(url_for("curso.autoevaluacion_form", curso_id=curso_id, trimestre=trimestre))

        if respuesta:
            respuesta.puntaje = puntaje
            respuesta.fecha_respuesta = datetime.utcnow()
        else:
            respuesta = RespuestaAutoevaluacion(
                config_id=config.id,
                estudiante_id=current_user.id,
                puntaje=puntaje,
                fecha_respuesta=datetime.utcnow(),
            )
            db.session.add(respuesta)
        db.session.commit()
        registrar_log("Autoevaluación", f"Estudiante autoevaluado en curso '{curso.nombre}' T{trimestre}: {puntaje}/5")
        flash("Tu autoevaluación fue guardada exitosamente.", "success")
        return redirect(url_for("curso.detalle", id=curso_id))

    return render_template("entregas/autoevaluacion.html", curso=curso, trimestre=trimestre, respuesta=respuesta)


@bp_curso.route("/<int:curso_id>/autoevaluaciones/<int:trimestre>")
@login_required
@role_required("admin", "docente")
def ver_autoevaluaciones(curso_id, trimestre):
    curso = Curso.query.get(curso_id)
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes ver las autoevaluaciones de un curso que no te pertenece.", "danger")
        return redirect(url_for("curso.listar"))

    config = AutoevaluacionConfig.query.filter_by(curso_id=curso_id, trimestre=trimestre).first()
    respuestas = []
    if config:
        respuestas = RespuestaAutoevaluacion.query.filter_by(config_id=config.id).all()

    pendientes = []
    if config:
        respondidos_ids = {r.estudiante_id for r in respuestas}
        pendientes = [
            insc.estudiante
            for insc in curso.inscripciones
            if insc.estudiante_id not in respondidos_ids
        ]

    return render_template(
        "cursos/autoevaluaciones.html",
        curso=curso, trimestre=trimestre, config=config,
        respuestas=respuestas, pendientes=pendientes,
    )


@bp_curso.route("/autoevaluacion/calificar/<int:respuesta_id>", methods=["GET", "POST"])
@login_required
@role_required("admin", "docente")
def calificar_autoevaluacion(respuesta_id):
    respuesta = RespuestaAutoevaluacion.query.get(respuesta_id)
    config = respuesta.config
    curso = config.curso

    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes calificar autoevaluaciones de un curso que no te pertenece.", "danger")
        return redirect(url_for("curso.listar"))

    if request.method == "POST":
        nota = request.form.get("nota_final", type=float)
        retro = request.form.get("retroalimentacion", "").strip()

        if nota is None or nota < 0 or nota > 5:
            flash(f"La nota debe estar entre 0 y 5.", "danger")
            return redirect(url_for("curso.calificar_autoevaluacion", respuesta_id=respuesta_id))

        respuesta.nota_final = nota
        respuesta.retroalimentacion = retro
        respuesta.docente_id = current_user.id
        respuesta.fecha_calificacion = datetime.utcnow()
        db.session.commit()
        registrar_log("Calificar Autoevaluación", f"Autoevaluación de {respuesta.estudiante.nombre_completo} calificada: {nota}/5")
        flash("Calificación guardada exitosamente.", "success")
        return redirect(url_for("curso.ver_autoevaluaciones", curso_id=curso.id, trimestre=config.trimestre))

    return render_template("cursos/calificar_autoevaluacion.html", respuesta=respuesta, config=config, curso=curso)


@bp_curso.route("/inscripciones/<int:id>")
@login_required
@role_required("admin", "docente")
def inscripciones(id):
    curso = Curso.query.get(id)
    if current_user.rol == "docente" and curso.docente_id != current_user.id:
        flash("No puedes gestionar inscripciones de un curso que no te pertenece.", "danger")
        return redirect(url_for("curso.listar"))

    return render_template("cursos/inscripciones.html", curso=curso)


@bp_curso.route("/inscripciones/<int:id>/delete/<int:inscripcion_id>")
def eliminar_inscripcion(id, inscripcion_id):
    inscripcion = Inscripcion.query.get(inscripcion_id)
    db.session.delete(inscripcion)
    db.session.commit()
    return redirect(url_for("curso.inscripciones", id=id))
