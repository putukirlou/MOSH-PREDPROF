import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, current_app

app = Flask(__name__, static_url_path="", static_folder="static", template_folder="templates")


def connect_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            db_path = os.path.join(current_app.root_path, "db", "main.db")
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row

            print("Успещное подклюиличь к SQLite БД.")
            try:
                cursor = connection.cursor()
                result = func(cursor, connection, *args, **kwargs)
            finally:
                connection.close()
                print("Соединение с SQLite БД закрыто.")
        except Exception as ex:
            print("Не удалочь подключиться к SQLite БД.")
            print(ex)
        return result

    return wrapper


@app.route("/", endpoint="index", methods=["GET", "POST"])
@connect_db
def index(cursor, connection):
    return render_template("index.html")


if __name__ == '__main__':
    app.run(port=800, host="127.0.0.1")
