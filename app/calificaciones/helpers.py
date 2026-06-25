from sqlalchemy import func
from app.app import db
from app.tareas.models import Tarea, DIMENSIONES
from app.modulos.models import Modulo
from app.entregas.models import Entrega, AutoevaluacionConfig, RespuestaAutoevaluacion
from app.calificaciones.models import Calificacion

def puntos_usados_dimension(curso_id, trimestre, dimension):
    """Suma de puntajes máximos de tareas creadas en una dimensión para un trimestre."""
    return (
        db.session.query(func.sum(Tarea.puntaje_maximo))
        .join(Modulo)
        .filter(
            Modulo.curso_id == curso_id,
            Tarea.trimestre == trimestre,
            Tarea.dimension == dimension,
        )
        .scalar()
        or 0
    )

def puntos_disponibles_dimension(curso_id, trimestre, dimension):
    """Puntos restantes para crear tareas en una dimensión."""
    usado = puntos_usados_dimension(curso_id, trimestre, dimension)
    return max(0, DIMENSIONES[dimension]["max"] - usado)

def nota_estudiante_dimension(estudiante_id, curso_id, trimestre, dimension):
    """Suma de notas del estudiante en todas las tareas calificadas de una dimensión."""
    nota_tareas = (
        db.session.query(func.sum(Calificacion.nota))
        .join(Entrega)
        .join(Tarea)
        .join(Modulo)
        .filter(
            Modulo.curso_id == curso_id,
            Tarea.trimestre == trimestre,
            Tarea.dimension == dimension,
            Entrega.estudiante_id == estudiante_id,
        )
        .scalar()
        or 0
    )

    if dimension == "autoevaluacion":
        nota_autoev = (
            db.session.query(func.sum(RespuestaAutoevaluacion.nota_final))
            .join(AutoevaluacionConfig)
            .filter(
                AutoevaluacionConfig.curso_id == curso_id,
                AutoevaluacionConfig.trimestre == trimestre,
                RespuestaAutoevaluacion.estudiante_id == estudiante_id,
                RespuestaAutoevaluacion.nota_final.isnot(None),
            )
            .scalar()
            or 0
        )
        return nota_tareas + nota_autoev

    return nota_tareas

def total_tareas_dimension(curso_id, trimestre, dimension):
    """Suma del puntaje máximo de todas las tareas en una dimensión (para mostrar en tabla)."""
    total = (
        db.session.query(func.sum(Tarea.puntaje_maximo))
        .join(Modulo)
        .filter(
            Modulo.curso_id == curso_id,
            Tarea.trimestre == trimestre,
            Tarea.dimension == dimension,
        )
        .scalar()
        or 0
    )

    if dimension == "autoevaluacion":
        tiene_config = AutoevaluacionConfig.query.filter_by(
            curso_id=curso_id, trimestre=trimestre, activo=True
        ).first()
        if tiene_config:
            total += DIMENSIONES["autoevaluacion"]["max"]

    return total

def resumen_estudiante_curso(estudiante_id, curso_id, trimestre):
    """Devuelve dict con las notas del estudiante por dimensión."""
    resultado = {}
    for dim, info in DIMENSIONES.items():
        nota = nota_estudiante_dimension(estudiante_id, curso_id, trimestre, dim)
        total = total_tareas_dimension(curso_id, trimestre, dim)
        resultado[dim] = {
            "nota": nota,
            "max": info["max"],
            "label": info["label"],
            "subtitle": info["subtitle"],
            "total_tareas": total,
        }
    return resultado
