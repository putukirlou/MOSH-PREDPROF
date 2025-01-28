import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, current_app, redirect

def addatm(cursor, connection, args):
    args["title"] = "Добавить банкомат"
    if request.method == "GET":
        return render_template("addatm.html", args=args)
    elif request.method == "POST":
        deviceid=request.form.get("deviceid", "")
        ll=request.form.get("ll", "")
        if not deviceid:
            args["error"] = "Не ввели Device ID"
            return render_template("error.html", args=args)
        query = (
            f"INSERT INTO atm (device_id, ll, status) VALUES ('{deviceid}', '{ll}', 1);"
        )
        cursor.execute(query)
        connection.commit()

        return redirect(f"/listatm", 301)