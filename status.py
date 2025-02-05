import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, current_app, redirect

def status(cursor, connection, args):
    args["title"] = "Список банкоматов"

    query = (
        f"SELECT * FROM atm;"
    )
    cursor.execute(query)
    status = cursor.fetchall()
    args["status"] = status



