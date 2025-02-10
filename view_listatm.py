import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, current_app, redirect

def listatm(cursor, connection, args):
    query = (
        f"SELECT * FROM atm;"
    )
    args["title"] = "Список банкоматов"
    cursor.execute(query)
    atms = cursor.fetchall()
    args["atms"] = atms


    if request.method == "GET":
        return render_template("listatm.html", args=args)
    elif request.method == "POST":
        return render_template("listatm.html", args=args)