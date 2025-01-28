
from flask import render_template, request

def listmessages(cursor, connection, args):

    args["title"] = "Состоянение парка банкоматов"

    query = (
        f"SELECT * FROM messages;"
    )
    cursor.execute(query)
    messages = cursor.fetchall()
    args["messages"] = messages

    if request.method == "GET":
        return render_template("listmessages.html", args=args)
    elif request.method == "POST":
        return render_template("listmessages.html", args=args)