
from flask import Flask, render_template, request, current_app, redirect

def listmechanics(cursor, connection):
    args = dict()
    args["title"] = "Список механиков"

    query = (
        f"SELECT * FROM mechanics;"
    )
    cursor.execute(query)
    mechanics = cursor.fetchall()
    args["mechanics"] = mechanics

    if request.method == "GET":
        return render_template("listmechanics.html", args=args)
    elif request.method == "POST":
        return render_template("listmechanics.html", args=args)
