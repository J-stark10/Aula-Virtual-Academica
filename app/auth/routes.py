from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.app import bcrypt, db
from app.auth import bp_auth
from app.usuarios.models import Usuario
from app.utils import registrar_log

@bp_auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre_completo = request.form["nombre_completo"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if Usuario.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado.", "danger")
            return redirect(url_for("auth.register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        es_primero = Usuario.query.count() == 0
        rol = "admin" if es_primero else "estudiante"

        nuevo_usuario = Usuario(
            nombre_completo=nombre_completo,
            email=email,
            password=hashed_password,
            rol=rol,
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        registrar_log("Registro de usuario", f"Usuario {email} registrado con rol {rol}",)

        flash("Cuenta creada correctamente. Inicia sesión para continuar.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@bp_auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("core.index"))

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and bcrypt.check_password_hash(usuario.password, password):
            if not usuario.activo:
                flash("Tu cuenta está inactiva. Contacta al administrador.", "danger")
                return redirect(url_for("auth.login"))

            login_user(usuario)
            registrar_log("Inicio de sesión", f"Usuario {email} ingresó al sistema")
            flash(f"¡Bienvenido, {usuario.nombre_completo}!", "success")
            return redirect(url_for("core.index"))

        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("auth/login.html")


@bp_auth.route("/logout")
@login_required
def logout():
    email = current_user.email
    logout_user()
    registrar_log("Cierre de sesión", f"Usuario {email} salió del sistema")
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))

