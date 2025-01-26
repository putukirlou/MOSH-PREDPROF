from flask import render_template, request,redirect


def cars(cursor, connection):
    args = dict()
    args["title"] = "Добавить/удалить машину инкассации"
    if request.method == "GET":
        return render_template("cars.html", args=args)
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

        return redirect(f"/cars", 302)