import os
from functools import wraps
from flask import current_app, flash, redirect, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename
from app.app import db
from app.usuario.models import LogActividad


def role_required(*roles):
    """Restringe el acceso a una vista según el rol del usuario autenticado."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.rol not in roles:
                flash("No tienes permiso para acceder a esta sección.", "danger")
                return redirect(url_for("core.index"))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def registrar_log(accion, detalles=None):
    """Registra una acción en la bitácora de actividad del sistema."""
    try:
        usuario_id = current_user.id if current_user.is_authenticated else None
        entrada = LogActividad(usuario_id=usuario_id, accion=accion, detalles=detalles)
        db.session.add(entrada)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error registrando log de actividad: {e}")


def guardar_archivo(file_storage, subcarpeta):
    """
    Guarda un archivo subido (FileStorage) dentro de uploads/<subcarpeta>/
    con un nombre único, y devuelve la ruta relativa para almacenar en BD.
    Devuelve None si no se proporcionó archivo.
    """
    if not file_storage or file_storage.filename == "":
        return None

    nombre_seguro = secure_filename(file_storage.filename)
    nombre_final = f"{int(__import__('time').time())}_{nombre_seguro}"

    carpeta_destino = os.path.join(current_app.config["UPLOAD_FOLDER"], subcarpeta)
    os.makedirs(carpeta_destino, exist_ok=True)

    ruta_absoluta = os.path.join(carpeta_destino, nombre_final)
    file_storage.save(ruta_absoluta)

    # Ruta relativa que se guarda en la base de datos (subcarpeta/nombre_final)
    return f"{subcarpeta}/{nombre_final}"
