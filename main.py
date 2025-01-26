import os
import sqlite3
from functools import wraps
from flask import Flask, current_app

from view_index import *
from view_addatm import *
from view_addmechanics import *
from view_addcars import *
from view_listatm import *
from view_listmechanics import *
from view_listcars import *
from view_command import *



app = Flask(
    __name__, static_url_path="", static_folder="static", template_folder="templates"
)


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


@app.route("/", endpoint="index", methods=["GET", "POST"])
@connect_db
def index_route(cursor, connection):
    return index(cursor, connection)


@app.route("/addatm", endpoint="addatm", methods=["GET", "POST"])
@connect_db
def addatm_route(cursor, connection):
    return addatm(cursor, connection)

@app.route("/addmechanics", endpoint="addmechanics", methods=["GET", "POST"])
@connect_db
def mechanics_route(cursor, connection):
    return mechanics(cursor, connection)

@app.route("/addcars", endpoint="addcars", methods=["GET", "POST"])
@connect_db
def cars_route(cursor, connection):
    return cars(cursor, connection)

@app.route("/listatm", endpoint="listatm", methods=["GET", "POST"])
@connect_db
def listatm_route(cursor, connection):
    return listatm(cursor, connection)

@app.route("/listmechanics", endpoint="listmechanics", methods=["GET", "POST"])
@connect_db
def listmechanics_route(cursor, connection):
    return listmechanics(cursor, connection)

@app.route("/listcars", endpoint="listcars", methods=["GET", "POST"])
@connect_db
def listcars_route(cursor, connection):
    return listcars(cursor, connection)


@app.route("/command", endpoint="command", methods=["GET", "POST"])
@connect_db
def command_route(cursor, connection):
    return command(cursor, connection)


@app.route("/cars", endpoint="cars", methods=["GET", "POST"])
@connect_db
def cars_route(cursor, connection):
    return cars(cursor, connection)


@app.route("/map", endpoint="map", methods=["GET", "POST"])
@connect_db
def map_route(cursor, connection):
    return map(cursor, connection)




@app.route("/deleteatm", endpoint="deleteatm", methods=["GET", "POST"])
@connect_db
def deleteatm(cursor, connection):
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
def editatm(cursor, connection):
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
def deletemechanics(cursor, connection):
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
def deletecars(cursor, connection):
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



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
