import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, current_app, redirect


def addcars(cursor, connection, args):

    args["title"] = "Добавить/удалить машину инкассации"
    if request.method == "GET":
        return render_template("addcars.html", args=args)
    elif request.method == "POST":
        id = request.form.get("id", "")
        name = request.form.get("name", "")
        if not id:
            args["error"] = "Не ввели ID"
            return render_template("error.html", args=args)
        query = (
            f"INSERT INTO cars (id, name, status) VALUES ('{id}', '{name}', 1);"
        )
        cursor.execute(query)
        connection.commit()

        return redirect(f"/listcars", 302)
