
from flask import render_template, request

def listatm(cursor, connection):
    args = dict()
    args["title"] = "Список банкоматов"

    query = (
        f"SELECT * FROM atm;"
    )
    cursor.execute(query)
    atms = cursor.fetchall()
    args["atms"] = atms

    if request.method == "GET":
        return render_template("listatm.html", args=args)
    elif request.method == "POST":
        return render_template("listatm.html", args=args)