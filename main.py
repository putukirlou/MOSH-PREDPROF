import os
import sqlite3
from functools import wraps
from flask import Flask, current_app, request, redirect, session


from view_addatm import *
from view_addmechanics import *
from view_addcars import *
from view_listatm import *
from view_listmechanics import *
from view_listcars import *
from view_listmessages import *
from view_command import *

app = Flask(
    __name__, static_url_path="", static_folder="static", template_folder="templates"
)
app.secret_key = "mosh"


def connect_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            db_path = os.path.join(current_app.root_path, 'db', 'main (2).db')
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            print("Успешно подключились к SQLite БД.")
            try:
                cursor = connection.cursor()
                result = func(cursor, connection, *args, **kwargs)
            finally:
                connection.close()
                print("Соединение с SQLite БД закрыто.")
        except Exception as ex:
            print("Не удалось подключиться к SQLite БД.")
            print(ex)
        return result

    return wrapper


def authorization(func):
    def wrapper(cursor, connection):
        args = {}
        args['access'] = 0
        name = session.get("name", "")
        password = session.get("password", "")
        if not (name and password):
            return render_template("login.html", args=args)
        name = name.lower()
        cursor.execute(f"SELECT * FROM users WHERE LOWER(name)='{name}' AND password='{password}';")
        row = cursor.fetchone()
        if row:
            args['access'] = 1
            print("Вход успешен")
            return func(cursor, connection, args)
        else:
            return render_template("login.html", args=args)

    return wrapper


@app.route("/", endpoint="index", methods=["GET", "POST"])
@connect_db
def index_route(cursor, connection):
    args = {}
    args["access"] = 0
    args["title"] = "Главная страница"
    args["приветствие"] = "Привет!"

    remember = False
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        remember = request.form.get("remember", False)
    else:
        name = session.get("name", "")
        password = session.get("password", "")
    if not (name and password):
        return render_template("login.html", args=args)
    select_all_rows = (
        f"SELECT * FROM users WHERE LOWER(name)='{name}' AND password='{password}';"
    )
    cursor.execute(select_all_rows)
    row = cursor.fetchone()
    if row:
        args["access"] = 1
        session["name"] = name
        session["password"] = password
        if remember:
            session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(days=7)
        else:
            session.permanent = False
        return render_template("index.html", args=args)
    else:
        return render_template("login.html", args=args)


@app.route("/addatm", endpoint="addatm", methods=["GET", "POST"])
@connect_db
@authorization
def addatm_route(cursor, connection, args):
    return addatm(cursor, connection, args)


@app.route("/addmechanics", endpoint="addmechanics", methods=["GET", "POST"])
@connect_db
@authorization
def mechanics_route(cursor, connection, args):
    return mechanics(cursor, connection, args)


@app.route("/addcars", endpoint="addcars", methods=["GET", "POST"])
@connect_db
@authorization
def cars_route(cursor, connection, args):
    return cars(cursor, connection, args)


@app.route("/listatm", endpoint="listatm", methods=["GET", "POST"])
@connect_db
@authorization
def listatm_route(cursor, connection, args):
    return listatm(cursor, connection, args)


@app.route("/listmechanics", endpoint="listmechanics", methods=["GET", "POST"])
@connect_db
@authorization
def listmechanics_route(cursor, connection, args):
    return listmechanics(cursor, connection, args)


@app.route("/listcars", endpoint="listcars", methods=["GET", "POST"])
@connect_db
@authorization
def listcars_route(cursor, connection, args):
    return listcars(cursor, connection, args)


@app.route("/listmessages", endpoint="listmessages", methods=["GET", "POST"])
@connect_db
@authorization
def listmessages_route(cursor, connection, args):
    return listmessages(cursor, connection, args)


@app.route("/command", endpoint="command", methods=["GET", "POST"])
@connect_db
@authorization
def command_route(cursor, connection, args):
    return command(cursor, connection, args)


@app.route("/map", endpoint="map", methods=["GET", "POST"])
@connect_db
def map_route(cursor, connection, args):
    return map(cursor, connection, args)


@app.route("/deleteatm", endpoint="deleteatm", methods=["GET", "POST"])
@connect_db
@authorization
def deleteatm(cursor, connection, args):
    args = dict()
    args["title"] = "Удалить банкомат"
    id = request.args.get("id")
    if not id:
        args["error"] = "Номер банкомата пустой"
        return render_template("error.html", args=args)

    query = (
        f"DELETE FROM atm WHERE id={id};"
    )
    cursor.execute(query)
    connection.commit()

    return redirect(f"/listmeatm", 301)


@app.route("/editatm", endpoint="editatm", methods=["GET", "POST"])
@connect_db
@authorization
def editatm(cursor, connection, args):
    args = dict()
    args["title"] = "Редактировать координаты"
    if request.method == "GET":
        id = request.args.get("id")
        if not id:
            args["error"] = "Номер банкомата пустой"
            return render_template("error.html", args=args)

        args["id"] = id
        return render_template("editatm.html", args=args)
    elif request.method == "POST":
        ll = request.form.get("ll", "")
        id = request.form.get("id", "")
        if not ll:
            args["error"] = "Не ввели Device ID"
            return render_template("error.html", args=args)
        query = (
            f"UPDATE atm SET ll = '{ll}' WHERE id={id};"
        )
        cursor.execute(query)
        connection.commit()

        return redirect(f"/listatm", 301)


@app.route("/deletemechanics", endpoint="deletemechanics", methods=["GET", "POST"])
@connect_db
@authorization
def deletemechanics(cursor, connection, args):
    args = dict()
    args["title"] = "Удалить механика"
    id = request.args.get("id")
    if not id:
        args["error"] = "Номер банкомата пустой"
        return render_template("error.html", args=args)

    query = (
        f"DELETE FROM mechanics WHERE id={id};"
    )
    cursor.execute(query)
    connection.commit()

    return redirect(f"/listmechanics", 302)


@app.route("/deletecars", endpoint="deletemecars", methods=["GET", "POST"])
@connect_db
@authorization
def deletecars(cursor, connection, args):
    args = dict()
    args["title"] = "Удалить машину"
    id = request.args.get("id")
    if not id:
        args["error"] = "Номер машины пустой"
        return render_template("error.html", args=args)

    query = (
        f"DELETE FROM cars WHERE id={id};"
    )
    cursor.execute(query)
    connection.commit()

    return redirect(f"/listcars", 302)


@app.route("/exit")
def exit_from_profile():
    session.pop("email", None)
    session.pop("name", None)
    session.pop("password", None)
    return redirect("/", 301)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
