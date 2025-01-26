from flask import render_template, request

def command(cursor, connection):
    args = dict()
    args["title"] = "Комманда"

    cursor.execute(f"SELECT * FROM atm;")
    atms = cursor.fetchall()
    args["atms"] = atms

    cursor.execute(f"SELECT * FROM cars;")
    cars = cursor.fetchall()
    args["cars"] = cars

    cursor.execute(f"SELECT * FROM messages;")
    messages = cursor.fetchall()
    args["messages"] = messages

    cursor.execute(f"SELECT * FROM mechanics;")
    mechanics = cursor.fetchall()
    args["mechanics"] = mechanics

    cursor.execute(f"SELECT * FROM users;")
    users = cursor.fetchall()
    args["users"] = users

    if request.method == "GET":
        return render_template("command.html", args=args)
    elif request.method == "POST":
        return render_template("command.html", args=args)
