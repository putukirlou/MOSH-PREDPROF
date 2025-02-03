import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, current_app, redirect

def listatm(cursor, connection, args):
    args["title"] = "Список банкоматов"

    query = (
        f"SELECT * FROM atm;"
    )
    cursor.execute(query)
    atms = cursor.fetchall()
    args["atms"] = atms
    
    query = (
        f"SELECT value FROM messages;"
    )
    cursor.execute(query)
    value = cursor.fetchall()
    args["value"] = value
    
    query = (
        f"SELECT status FROM atm;"
    )
    cursor.execute(query)
    status = cursor.fetchall()
    args["status"] = status

    def update_task_status(vaule, status):

        cursor.execute('UPDATE status SET status = ? WHERE vaule = Настройки сброшены","Устройство отключено","Не удалось","Некоторые системы не работают","Закрыто"',("На ремонте"))
        connection.commit()

    if request.method == "GET":
        return render_template("listatm.html", args=args)
    elif request.method == "POST":
        return render_template("listatm.html", args=args)