import paho.mqtt.client as mqtt
from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

from db.connection import db
from models import Kit, User

login = Blueprint("login", __name__, template_folder="templates")


@login.route("/login", methods=["GET", "POST"])
def login_func():
    if request.method == "POST":
        username = request.form["user"]
        password = request.form["password"]
        user = User.validate_user(username, password)

        if user:
            login_user(user)
            session["user"] = user.id
            return redirect(url_for("login.home"))
        else:
            return render_template(
                "login.html", login_message="Erro! Esse usuário não existe!"
            )

    return render_template("login.html")


@login.route("/home")
@login_required
def home():
    admin_query = User.select_from_users(User.role == "admin")
    admin_users = 0 if len(admin_query) <= 0 else len(admin_query)
    operator_query = User.select_from_users(User.role == "operador")
    operator_users = 0 if len(operator_query) <= 0 else len(operator_query)
    statistic_query = User.select_from_users(User.role == "estatistico")
    statistic_users = 0 if len(statistic_query) <= 0 else len(statistic_query)
    kits = Kit.select_all_from_kits()
    return render_template(
        "home.html",
        admin_users=admin_users,
        operator_users=operator_users,
        statistic_users=statistic_users,
        kits=kits,
    )


@login.route("/register_user")
@login_required
def register_user():
    return render_template("users/register_user.html", user=session.get("user"))


@login.route("/add_user", methods=["GET", "POST"])
@login_required
def add_users():
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]
        role = request.form["role"]
        existing_users = User.select_all_from_users()
        print(existing_users)
        existing_users_names = [user.name for user in existing_users]
        if user in existing_users_names:
            return render_template(
                "users/register_user.html",
                error_message="Erro! Esse nome de usuário já existe",
            )
        elif role != "admin" and role != "operador" and role != "estatistico":
            return render_template(
                "users/register_user.html",
                error_message="Erro! O role deve ser: admin, operador ou estatistico",
            )
        else:
            new_user = User(user, password, role)
            db.session.add(new_user)
            db.session.commit()
            return render_template(
                "users/users.html", users=User.select_all_from_users()
            )


@login.route("/users")
@login_required
def list_users():
    users = User.select_all_from_users()
    return render_template("users/users.html", users=users)


@login.route("/delete_user")
@login_required
def remove_user():
    user_id = request.args.get("user_id", None)
    print("USERID:")
    print(user_id)
    User.delete_user_by_id(user_id)
    return redirect("/users")


@login.route("/del_user", methods=["GET", "POST"])
@login_required
def del_user():
    if request.method == "POST":
        user = request.form["user"]
    else:
        user = request.args.get("user", None)
    User.delete_user_by_id(user)
    return redirect("/users")


@login.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
