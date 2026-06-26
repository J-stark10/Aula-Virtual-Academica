from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.app import bcrypt, db
from app.usuarios.models import Usuario
from app.utils import registrar_log, role_required

bp_usuario = Blueprint("usuario", __name__, template_folder="templates")


@bp_usuario.route("")
@login_required
@role_required("admin")
def listar():
    rol_filtro = request.args.get("rol", "")
    query = Usuario.query
    if rol_filtro:
        query = query.filter_by(rol=rol_filtro)
    items = query.order_by(Usuario.fecha_registro.desc()).all()
    return render_template("usuario/listar.html", items=items, rol_filtro=rol_filtro)


@bp_usuario.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def crear():
    if request.method == "POST":
        nombre_completo = request.form["nombre_completo"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        rol = request.form["rol"]

        if Usuario.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado.", "danger")
            return redirect(url_for("usuario.crear"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        nuevo = Usuario(
            nombre_completo=nombre_completo, email=email, password=hashed_password, rol=rol
        )
        db.session.add(nuevo)
        db.session.commit()

        registrar_log("Crear Usuario", f"Usuario {email} creado con rol {rol} por administrador")
        flash("Usuario creado exitosamente.", "success")
        return redirect(url_for("usuario.listar"))

    return render_template("usuario/crear.html")


@bp_usuario.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def editar(id):
    usuario = Usuario.query.get(id)
    if request.method == "POST":
        nombre_completo = request.form["nombre_completo"].strip()
        email = request.form["email"].strip().lower()
        rol = request.form["rol"]
        password = request.form.get("password", "").strip()

        if not nombre_completo or not email:
            flash("El nombre y el correo son requeridos.", "danger")
            return redirect(url_for("usuario.editar", id=id))

        if email != usuario.email and Usuario.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado por otro usuario.", "danger")
            return redirect(url_for("usuario.editar", id=id))

        usuario.nombre_completo = nombre_completo
        usuario.email = email
        usuario.rol = rol
        if password:
            usuario.password = bcrypt.generate_password_hash(password).decode("utf-8")

        db.session.commit()
        registrar_log("Editar Usuario", f"Usuario {email} actualizado con rol {rol}")
        flash("Usuario actualizado exitosamente.", "success")
        return redirect(url_for("usuario.listar"))

    return render_template("usuario/editar.html", usuario=usuario)


@bp_usuario.route("/toggle/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def toggle(id):
    usuario = Usuario.query.get(id)
    if usuario.id == current_user.id:
        flash("No puedes desactivar tu propia cuenta.", "danger")
        return redirect(url_for("usuario.listar"))

    usuario.activo = not usuario.activo
    db.session.commit()

    estado = "activado" if usuario.activo else "desactivado"
    registrar_log("Cambiar Estado Usuario", f"Usuario {usuario.email} {estado}")
    flash(f"Usuario {estado} exitosamente.", "info")
    return redirect(url_for("usuario.listar"))


@bp_usuario.route("/delete/<int:id>")
def eliminar(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado exitosamente.", "success")
    return redirect(url_for("usuario.listar"))
