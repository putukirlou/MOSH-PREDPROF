import os
import sqlite3
from functools import wraps
import datetime
from flask import Flask, render_template, request, current_app, redirect, session


from view_addatm import *
from view_addmechanics import *
from view_addcars import *
from view_listatm import *
from view_listmechanics import *
from view_listcars import *
from view_command import *
from view_condition import *
import csv

app = Flask(
    __name__, static_url_path="", static_folder="static", template_folder="templates"
)
app.secret_key = "mosh"

from datetime import datetime, timedelta


def connect_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            db_path = os.path.join(current_app.root_path, 'db', 'main.db')
            connection = sqlite3.connect(db_path)
            connection.row_factory = sqlite3.Row
            print("Успешно подключились к SQLite БД.")
            try:
                cursor = connection.cursor()
                result = func(cursor, connection, *args, **kwargs)
            finally:
                connection.close()
                print("Соединение с SQLite БД закрыто.")
        except Exception as ex:
            print("Не удалось подключиться к SQLite БД.")
            print(ex)
        return result
    return wrapper


def authorization(func):
    def wrapper(cursor, connection):
        args = {}
        args['access'] = 0
        name = session.get("name", "")
        password = session.get("password", "")
        if not (name and password):
            return render_template("login.html", args=args)
        name = name.lower()
        cursor.execute(f"SELECT * FROM users WHERE LOWER(name)='{name}' AND password='{password}';")
        row = cursor.fetchone()
        if row:
            args['access'] = 1
            print("Вход успешен")
            return func(cursor, connection, args)
        else:
            return render_template("login.html", args=args)
        
    return wrapper


@app.route("/", endpoint="index", methods=["GET", "POST"])
@connect_db
def index_route(cursor, connection):
    args = {}
    args["access"] = 0
    args["title"] = "Главная страница"
    args["приветствие"] = "Привет!"

    remember = False
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        remember = request.form.get("remember", False)
    else:
        name = session.get("name", "")
        password = session.get("password", "")
    if not (name and password):
        return render_template("login.html", args=args)
    select_all_rows = (
        f"SELECT * FROM users WHERE LOWER(name)='{name}' AND password='{password}';"
    )
    cursor.execute(select_all_rows)
    row = cursor.fetchone()
    if row:
        args["access"] = 1
        session["name"] = name
        session["password"] = password
        if remember:
            session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(days=7)
        else:
            session.permanent = False
        return render_template("index.html", args=args)
    else:
        return render_template("login.html", args=args)


@app.route("/addatm", endpoint="addatm", methods=["GET", "POST"])
@connect_db
@authorization
def addatm_route(cursor, connection, args):
    return addatm(cursor, connection, args)


@app.route("/addmechanics", endpoint="addmechanics", methods=["GET", "POST"])
@connect_db
@authorization
def addmechanics_route(cursor, connection, args):
    return addmechanics(cursor, connection, args)


@app.route("/addcars", endpoint="addcars", methods=["GET", "POST"])
@connect_db
@authorization
def addcars_route(cursor, connection, args):
    return addcars(cursor, connection, args)


@app.route("/listatm", endpoint="listatm", methods=["GET", "POST"])
@connect_db
@authorization
def listatm_route(cursor, connection, args):
    return listatm(cursor, connection, args)


@app.route("/listmechanics", endpoint="listmechanics", methods=["GET", "POST"])
@connect_db
@authorization
def listmechanics_route(cursor, connection, args):
    return listmechanics(cursor, connection, args)


@app.route("/listcars", endpoint="listcars", methods=["GET", "POST"])
@connect_db
@authorization
def listcars_route(cursor, connection, args):
    return listcars(cursor, connection, args)




@app.route("/condition", endpoint="condition", methods=["GET", "POST"])
@connect_db
@authorization
def condition_route(cursor, connection, args):
    return condition(cursor, connection, args)


@app.route("/command", endpoint="command", methods=["GET", "POST"])
@connect_db
@authorization
def command_route(cursor, connection, args):
    return command(cursor, connection, args)


@app.route("/clearmessages", endpoint="clearmessages", methods=["GET", "POST"])
@connect_db
@authorization
def clearmessages(cursor, connection, args):
    query = "DELETE FROM messages;"
    cursor.execute(query)
    connection.commit()
    return redirect(f"/list-messages", 301)



@app.route("/load-csv", endpoint="loadcsv", methods=["GET", "POST"])
@connect_db
@authorization
def loadcsv(cursor, connection, args):
    args = dict()
    args["title"] = "Загрузить CSV"
    if request.method == "GET":
        return render_template("loadcsv.html", args=args)
    elif request.method == "POST":
        if 'file' not in request.files:
            args["error"] = "No file part"
            return render_template("error.html", args=args)
        file = request.files['file']
        if file.filename == '':
            args["error"] = "No selected file"
            return render_template("error.html", args=args)
        if file and file.filename.endswith('.csv'):
            file_data = file.read().decode('utf-8')
            csv_reader = csv.reader(file_data.splitlines())
            rows = list(csv_reader)
            lines = []
            for i, row in enumerate(rows):
                if i == 0:  
                    continue
                eventtype = row[1]
                timestamp = row[2]
                device_id = row[3]
                user_id = row[4]
                details = row[5]
                value = row[6] if len(row) > 6 else " "

                query = '''INSERT INTO messages (eventtype, timestamp, device_id, user_id, details, value)
                           VALUES (?, ?, ?, ?, ?, ?);'''
                cursor.execute(query, (eventtype, timestamp, device_id, user_id, details, value))
            connection.commit()
            return redirect(f"/list-messages", 301)
        else:
            args["error"] = "Invalid file type. Only CSV files are allowed."
            return render_template("error.html", args=args)


@app.route("/map", endpoint="map", methods=["GET", "POST"])
@connect_db
@authorization
def listmessages(cursor, connection, args):
    args["title"] = "Карта"

    query = (
        f"SELECT * FROM atm;"
    )
    cursor.execute(query)
    atms = cursor.fetchall()
    lines=[]
    for atm in atms:
        lines.append(atm["ll"].replace("%2C", ","))


    url = f"https://static-maps.yandex.ru/v1?ll=37.620070,55.753630&lang=ru_RU&size=450,450&z=10&size=600&pt={'~'.join(lines)}&apikey=f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
    print(url)

    args['image_url'] = url

    return render_template("map.html", args=args)


@app.route("/list-messages", endpoint="listmessages_page", methods=["GET", "POST"])
@connect_db
@authorization
def listmessages(cursor, connection, args):
    args["title"] = "Список сообщений"

    query = (
        f"SELECT * FROM messages ;"
    )
    cursor.execute(query)
    messages = cursor.fetchall()
    print(f"Messages found: {len(messages)}")  
    args["count"] = len(messages)
    args["messages"] = messages[:10000]
    args["title"] = "Список сообщений"
    query = "SELECT * FROM messages;"
    cursor.execute(query)
    messages = cursor.fetchall()


    print(f"Messages found: {len(messages)}")

    args["count"] = len(messages)
    args["messages"] = [dict(message) for message in messages] 


    query_atm = "SELECT * FROM atm;"
    cursor.execute(query_atm)
    atm_data = cursor.fetchall()


    for message in args["messages"]:
        device_id = message["device_id"]

        atm_status = next((atm["status"] for atm in atm_data if atm["device_id"] == device_id), None)

        message["status"] = atm_status
        args["title"] = "Список сообщений банкоматов"


    query = '''
    SELECT m.*
    FROM messages m
    INNER JOIN (
        SELECT device_id, MAX(timestamp) AS latest_timestamp
        FROM messages
        GROUP BY device_id
    ) AS latest_messages
    ON m.device_id = latest_messages.device_id AND m.timestamp = latest_messages.latest_timestamp;
    '''
    
    cursor.execute(query)
    messages = cursor.fetchall()
    args["messages"] = messages

    if request.method == "GET":
        return render_template("listmessages.html", args=args)
    elif request.method == "POST":
        return render_template("listmessages.html", args=args)


def get_atm_uptime(cursor, device_id, start_date, end_date):
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

    query = '''
    SELECT timestamp, value
    FROM messages
    WHERE device_id = ? AND timestamp BETWEEN ? AND ?
    ORDER BY timestamp;
    '''
    cursor.execute(query, (device_id, start_date_str, end_date_str))
    messages = cursor.fetchall()

    if not messages:
        return 0

    formatted_messages = []
    for msg in messages:
        try:
            formatted_messages.append({
                "timestamp": datetime.strptime(msg["timestamp"], '%Y-%m-%d %H:%M:%S'),
                "status": msg["value"]
            })
        except Exception as e:
            print(f"Ошибка преобразования timestamp: {msg['timestamp']} - {e}")

    total_time = 0
    working_time = 0
    last_timestamp = formatted_messages[0]["timestamp"]
    last_status = "Не работает"

    for message in formatted_messages[1:]:
        current_timestamp = message["timestamp"]
        status = message["status"]

        time_diff = (current_timestamp - last_timestamp).total_seconds()

        total_time += time_diff

        if "Работает" in last_status:
            working_time += time_diff

        last_timestamp = current_timestamp
        last_status = status

    if total_time > 0:
        uptime_percentage = (working_time / total_time) * 100
    else:
        uptime_percentage = 0
    print(
        f"Банкомат {device_id}: Общее время = {total_time} сек, Время работы = {working_time} сек, Процент = {uptime_percentage}%")
    return round(uptime_percentage, 2)


@app.route("/uptime", endpoint="uptime", methods=["GET"])
@connect_db
@authorization
def uptime(cursor, connection, args):
    args["title"] = "Процент времени работы банкоматов"

    now = datetime.now()
    one_week_ago = now - timedelta(weeks=1)
    one_month_ago = now - timedelta(days=30)

    one_month_ago_str = one_month_ago.strftime("%Y-%m-%d %H:%M:%S")

    query = '''
    SELECT device_id, value, timestamp 
    FROM messages 
    WHERE timestamp >= ? 
    ORDER BY device_id, timestamp;
    '''
    cursor.execute(query, (one_month_ago_str,))
    statuses = cursor.fetchall()

    if not statuses:
        args["error"] = "Нет данных за последний месяц"
        return render_template("error.html", args=args)

    atm_statuses = {}
    for row in statuses:
        device_id = row["device_id"]

        status = row["value"].strip().lower()
        try:
            timestamp = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Ошибка преобразования timestamp: {row['timestamp']} - {e}")
            continue

        if device_id not in atm_statuses:
            atm_statuses[device_id] = []
        atm_statuses[device_id].append({"value": status, "timestamp": timestamp})

    uptimes = []

    for device_id, status_list in atm_statuses.items():

        status_list.sort(key=lambda x: x["timestamp"])

        total_week = 0
        total_month = 0
        working_week = 0
        working_month = 0

        for i in range(len(status_list) - 1):
            start_time = status_list[i]["timestamp"]
            end_time = status_list[i + 1]["timestamp"]
            time_diff = (end_time - start_time).total_seconds()

            if start_time >= one_week_ago:
                total_week += time_diff
                if status_list[i]["value"] == "работает":
                    working_week += time_diff

            total_month += time_diff
            if status_list[i]["value"] == "работает":
                working_month += time_diff

        uptime_week = (working_week / total_week * 100) if total_week > 0 else 0
        uptime_month = (working_month / total_month * 100) if total_month > 0 else 0

        print(
            f"Банкомат {device_id}: Общее время (неделя) = {total_week} сек, Время работы = {working_week} сек, Процент = {uptime_week}%")
        print(
            f"Банкомат {device_id}: Общее время (месяц) = {total_month} сек, Время работы = {working_month} сек, Процент = {uptime_month}%")

        uptimes.append({
            "device_id": device_id,
            "uptime_week": uptime_week,
            "uptime_month": uptime_month
        })

    args["uptimes"] = uptimes
    return render_template("uptime.html", args=args)
@app.route("/list-messages-atm", endpoint="list-messages-atm", methods=["GET", "POST"])
@connect_db
@authorization
def listmechanicsatm(cursor, connection, args):
    args["title"] = "Список сообщений банкоматов"

    query = (
        f"SELECT * FROM messages;"
    )
    cursor.execute(query)
    messages = cursor.fetchall()
    args["messages"] = messages

    if request.method == "GET":
        return render_template("listmessagesatm.html", args=args)
    elif request.method == "POST":
        return render_template("listmessagesatm.html", args=args)

@app.route("/deleteatm", endpoint="deleteatm", methods=["GET", "POST"])
@connect_db
@authorization
def deleteatm(cursor, connection, args):
    args = dict()
    args["title"] = "Удалить банкомат"
    id = request.args.get("id")
    if not id:
        args["error"] = "Номер банкомата пустой"
        return render_template("error.html", args=args)

    query = (
        f"DELETE FROM atm WHERE id={id};"
    )
    cursor.execute(query)
    connection.commit()

    return redirect(f"/listmeatm", 301)


@app.route("/editatm", endpoint="editatm", methods=["GET", "POST"])
@connect_db
@authorization
def editatm(cursor, connection, args):
    args = dict()
    args["title"] = "Редактировать координаты"
    if request.method == "GET":
        id = request.args.get("id")
        if not id:
            args["error"] = "Номер банкомата пустой"
            return render_template("error.html", args=args)

        args["id"] = id
        return render_template("editatm.html", args=args)
    elif request.method == "POST":
        ll = request.form.get("ll", "")
        id = request.form.get("id", "")
        if not ll:
            args["error"] = "Не ввели Device ID"
            return render_template("error.html", args=args)
        query = (
            f"UPDATE atm SET ll = '{ll}' WHERE id={id};"
        )
        cursor.execute(query)
        connection.commit()

        return redirect(f"/listatm", 301)


@app.route("/deletemechanics", endpoint="deletemechanics", methods=["GET", "POST"])
@connect_db
@authorization
def deletemechanics(cursor, connection, args):
    args = dict()
    args["title"] = "Удалить механика"
    id = request.args.get("id")
    if not id:
        args["error"] = "Номер банкомата пустой"
        return render_template("error.html", args=args)

    query = (
        f"DELETE FROM mechanics WHERE id={id};"
    )
    cursor.execute(query)
    connection.commit()

    return redirect(f"/listmechanics", 302)


@app.route("/deletecars", endpoint="deletemecars", methods=["GET", "POST"])
@connect_db
@authorization
def deletecars(cursor, connection, args):
    args = dict()
    args["title"] = "Удалить машину"
    id = request.args.get("id")
    if not id:
        args["error"] = "Номер машины пустой"
        return render_template("error.html", args=args)

    query = (
        f"DELETE FROM cars WHERE id={id};"
    )
    cursor.execute(query)
    connection.commit()

    return redirect(f"/listcars", 302)


@app.route("/exit")
def exit_from_profile():
    session.pop("email", None)
    session.pop("name", None)
    session.pop("password", None)
    return redirect("/", 301)

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
