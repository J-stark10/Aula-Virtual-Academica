from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from app.app import db
from app.categorias.models import Categoria
from app.utils import registrar_log, role_required

bp_categoria = Blueprint("categoria", __name__, template_folder="templates")


@bp_categoria.route("")
@login_required
@role_required("admin")
def listar():
    items = Categoria.query.all()
    return render_template("categoria/listar.html", items=items)


@bp_categoria.route("/create", methods=["GET", "POST"])
@login_required
@role_required("admin")
def crear():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not nombre:
            flash("El nombre de la categoría es requerido.", "danger")
            return redirect(url_for("categoria.crear"))

        if Categoria.query.filter_by(nombre=nombre).first():
            flash("Ya existe una categoría con ese nombre.", "danger")
            return redirect(url_for("categoria.crear"))

        nueva = Categoria(nombre=nombre, descripcion=descripcion)
        db.session.add(nueva)
        db.session.commit()

        registrar_log("Crear Categoría", f"Categoría '{nombre}' creada")
        flash("Categoría creada exitosamente.", "success")
        return redirect(url_for("categoria.listar"))

    return render_template("categoria/crear.html")


@bp_categoria.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def editar(id):
    item = Categoria.query.get(id)
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        descripcion = request.form.get("descripcion", "").strip()

        if not nombre:
            flash("El nombre de la categoría es requerido.", "danger")
            return redirect(url_for("categoria.editar", id=id))

        if nombre != item.nombre and Categoria.query.filter_by(nombre=nombre).first():
            flash("Ya existe una categoría con ese nombre.", "danger")
            return redirect(url_for("categoria.editar", id=id))

        item.nombre = nombre
        item.descripcion = descripcion
        db.session.commit()

        registrar_log("Editar Categoría", f"Categoría ID {id} actualizada: {nombre}")
        flash("Categoría actualizada exitosamente.", "success")
        return redirect(url_for("categoria.listar"))

    return render_template("categoria/editar.html", item=item)


@bp_categoria.route("/delete/<int:id>")
def eliminar(id):
    item = Categoria.query.get(id)
    db.session.delete(item)
    db.session.commit()
    registrar_log("Eliminar Categoría", f"Categoría '{item.nombre}' eliminada")
    flash("Categoría eliminada exitosamente.", "success")
    return redirect(url_for("categoria.listar"))
