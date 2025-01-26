from flask import render_template, request,redirect


def mechanics(cursor, connection):
    args = dict()
    args["title"] = "Добавить/удалить механика"
    if request.method == "GET":
        return render_template("mechanics.html", args=args)
    elif request.method == "POST":
        id = request.form.get("id", "")
        name = request.form.get("name", "")
        if not id:
            args["error"] = "Не ввели ID"
            return render_template("error.html", args=args)
        query = (
            f"INSERT INTO mechanics (id, name, status) VALUES ('{id}', '{name}', 1);"
        )
        cursor.execute(query)
        connection.commit()

        return redirect(f"/mechanics", 302)
