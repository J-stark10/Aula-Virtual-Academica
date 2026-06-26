import os
from datetime import timezone
from zoneinfo import ZoneInfo
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

BOLIVIA_TZ = ZoneInfo("America/La_Paz")
UTC = timezone.utc

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."
login_manager.login_message_category = "warning"

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "aula-virtual-academica-dev-key-2026")

    db_url = os.environ.get("DATABASE_URL", "sqlite:///aula_virtual.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Carpeta de archivos subidos (PDFs y videos de recursos, entregas de estudiantes)
    app.config["UPLOAD_FOLDER"] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static", "uploads"
    )
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024  # 64 MB máximo por archivo

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        from app.usuarios.models import Usuario
        return Usuario.query.get(int(user_id))
    
    @app.template_filter("bolivia")
    def bolivia_filter(dt):
        if dt is None:
            return ""
        return dt.replace(tzinfo=UTC).astimezone(BOLIVIA_TZ)

    # Import y registro de blueprints
    from app.auth import bp_auth
    from app.categoria.routes import bp_categoria
    from app.core.routes import bp_core
    from app.usuarios.routes import bp_usuario
    from app.cursos.routes import bp_curso
    from app.modulos.routes import bp_modulo
    from app.recursos.routes import bp_recurso
    from app.tareas.routes import bp_tarea
    from app.entregas.routes import bp_entrega
    from app.calificaciones.routes import bp_calificacion
    from app.anuncios.routes import bp_anuncio

    app.register_blueprint(bp_core)
    app.register_blueprint(bp_categoria, url_prefix="/categorias")
    app.register_blueprint(bp_usuario, url_prefix="/usuarios")
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_curso, url_prefix="/cursos")
    app.register_blueprint(bp_modulo, url_prefix="/modulos")
    app.register_blueprint(bp_recurso, url_prefix="/recursos")
    app.register_blueprint(bp_tarea, url_prefix="/tareas")
    app.register_blueprint(bp_entrega, url_prefix="/entregas")
    app.register_blueprint(bp_calificacion, url_prefix="/calificaciones")
    app.register_blueprint(bp_anuncio, url_prefix="/anuncios")

    with app.app_context():
        # Import de modelos para registrarlos en el metadata de SQLAlchemy
        from app.usuarios.models import Usuario, LogActividad
        from app.categoria.models import Categoria
        from app.cursos.models import Curso, Inscripcion
        from app.modulos.models import Modulo
        from app.recursos.models import Recurso
        from app.tareas.models import Tarea
        from app.entregas.models import Entrega, AutoevaluacionConfig, RespuestaAutoevaluacion
        from app.calificaciones.models import Calificacion, HistorialCalificacion
        from app.anuncios.models import Anuncio

        db.create_all()

    return app
