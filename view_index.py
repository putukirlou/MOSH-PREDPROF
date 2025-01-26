
from flask import  render_template, request


def index(cursor, connection):
    args = dict()
    args["title"] = "Главная страница"
    args["приветствие"] = "Привет!"
    if request.method == "GET":
        return render_template("index.html", args=args)
    elif request.method == "POST":
        return render_template("index.html")
