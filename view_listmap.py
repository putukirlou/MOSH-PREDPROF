
from flask import Flask, render_template, request, current_app, redirect

def listmap(cursor, connection, args):
    args["title"] = "Список машин инкассации"

    query = (
        f"SELECT * FROM cars;"
    )
    cursor.execute(query)
    cars = cursor.fetchall()
    args["cars"] = cars

    if request.method == "GET":
        return render_template("listmap.html", args=args)
    elif request.method == "POST":
        return render_template("listmap.html", args=args)