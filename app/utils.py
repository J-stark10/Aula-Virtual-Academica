import os
import time
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename

from app.app import db
from app.supabase_client import supabase
from app.usuarios.models import LogActividad

def role_required(*roles):

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

    try:
        usuario_id = current_user.id if current_user.is_authenticated else None
        entrada = LogActividad(usuario_id=usuario_id, accion=accion, detalles=detalles)
        db.session.add(entrada)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error registrando log de actividad: {e}")


def guardar_archivo(file_storage, subcarpeta):
    if not file_storage or file_storage.filename == "":
        return None

    nombre_seguro = secure_filename(file_storage.filename)
    nombre_final = f"{int(time.time())}_{nombre_seguro}"

    ruta = f"{subcarpeta}/{nombre_final}"

    file_storage.stream.seek(0)

    supabase.storage.from_("uploads").upload(
        path=ruta,
        file=file_storage.stream.read(),
        file_options={
            "content-type": file_storage.content_type
        }
    )

    return ruta
