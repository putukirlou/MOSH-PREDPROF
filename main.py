import os
import sqlite3
from functools import wraps
import datetime
from flask import Flask, render_template, request, current_app, redirect, session
from datetime import datetime, timedelta
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
                if i == 0:  # пропускаем заголовок
                    continue
                eventtype = row[1]
                timestamp = row[2]
                device_id = row[3]
                user_id = row[4]
                details = row[5]
                value = row[6] if len(row) > 6 else " "
                # Используем параметризованный запрос
                query = '''INSERT INTO messages (eventtype, timestamp, device_id, user_id, details, value)
                           VALUES (?, ?, ?, ?, ?, ?);'''
                cursor.execute(query, (eventtype, timestamp, device_id, user_id, details, value))
            connection.commit()
            return redirect(f"/list-messages", 301)
        else:
            args["error"] = "Invalid file type. Only CSV files are allowed."
            return render_template("error.html", args=args)




@app.route("/list-messages", endpoint="listmessages_page", methods=["GET", "POST"])
@connect_db
@authorization
def listmessages(cursor, connection, args):
    args["title"] = "Список сообщений"
    
    # Проверка соединения с базой данных
    print("Соединение с базой данных установлено.")
    
    # Загружаем все сообщения, отсортированные по времени
    query = "SELECT * FROM messages ORDER BY timestamp ASC;"
    cursor.execute(query)
    messages = cursor.fetchall()

    # Проверка, что сообщения были загружены
    print(f"Загружено {len(messages)} сообщений.")

    # Загружаем список всех банкоматов
    query_atm = "SELECT * FROM atm;"
    cursor.execute(query_atm)
    atms = {atm["device_id"]: atm for atm in cursor.fetchall()}

    # Проверка наличия банкоматов
    print(f"Загружено {len(atms)} банкоматов.")

    # Словарь для хранения статуса работы банкоматов и времени
    atm_status = {}

    # Время последней недели и месяца
    now = datetime.now()
    one_week_ago = now - timedelta(weeks=1)
    one_month_ago = now - timedelta(weeks=4)

    # Обрабатываем сообщения, обновляя статусы банкоматов
    print("Начинаем обработку сообщений.")
    for message in messages:
        device_id = message["device_id"]
        timestamp = datetime.strptime(message["timestamp"], "%Y-%m-%d %H:%M:%S")
        status = 1  # По умолчанию считаем, что банкомат работает

        # Проверка значения message
        #print(f"Обрабатываем сообщение: device_id = {device_id}, timestamp = {timestamp}, value = {message['value']}")

        # Проверяем значения в details для определения статуса банкомата
        value = message["value"].strip().capitalize()

        if value in ["Купюра зажевана", "Клавиатура не работает", "Найдены ошибки", "Не работает", 
                     "Нет бумаги", "Нет свободного места", "Нет соединения", "Нуждается в замене", 
                     "Ошибка механизма", "Обновление доступно", "Ошибка питания", "Ошибка связи", 
                     "Ошибка сети", "Ошибка совместимости", "Ошибка чтения", "Плохое", "Потеря соединения", 
                     "Принтер не работает", "Проблема с сетью", "Проблемы с энергоснабжением", 
                     "Профилактическое", "Слабый сигнал", "Техническая ошибка", "Техическая", 
                     "Нет свободного места", "Пустой", "Потеря пакетов"]:
            status = 0  # Требуется механик или не работает
        elif value in ["Нет наличных", "Низкий уровень наличных"]:
            status = 0  # Требуется машина инкассации, банкомат не работает
        elif value in ["Настройки сброшены", "Устройство отключено", "Не удалось", 
                       "Некоторые системы не работают", "Закрыто"]:
            status = 0  # В ремонте, банкомат не работает

        # Проверка статуса
        #print(f"Установлен статус для банкомата {device_id}: {'Работает' if status == 1 else 'Не работает'}")

        # Обновляем статус и добавляем его в историю для вычисления времени
        if device_id not in atm_status:
            atm_status[device_id] = {
                "last_status": status,
                "last_update": timestamp,
                "total_time": 0,  # Общее время работы
                "down_time": 0,   # Общее время неработающего состояния
                "status_history": []
            }

        # Если статус изменился, обновляем время работы/неработы
        if atm_status[device_id]["last_status"] != status:
            time_difference = (timestamp - atm_status[device_id]["last_update"]).total_seconds()

            # Проверка времени изменения статуса
            #print(f"Изменение статуса банкомата {device_id}: время изменения = {time_difference} секунд")

            if atm_status[device_id]["last_status"] == 1:
                atm_status[device_id]["total_time"] += time_difference  # Время работы
            else:
                atm_status[device_id]["down_time"] += time_difference  # Время неработающего состояния

            # Обновляем статус
            atm_status[device_id]["last_status"] = status
            atm_status[device_id]["last_update"] = timestamp

        # Добавляем статус в историю
        atm_status[device_id]["status_history"].append((timestamp, status))

    # Проверка завершения обработки всех сообщений
    #print("Обработка всех сообщений завершена.")

    # Рассчитываем процент времени работы и неработы
    #print("Начинаем расчет процентов для каждого банкомата.")
    for device_id, data in atm_status.items():
        total_time = data["total_time"]
        down_time = data["down_time"]
        total_period = total_time + down_time

        # Проверка перед расчетом процентов
        print(f"Подсчет процентов для банкомата {device_id}: общее время = {total_time}, время простоя = {down_time}")

        if total_period > 0:
            uptime_percent = round((total_time / total_period) * 100, 2)
            downtime_percent = round((down_time / total_period) * 100, 2)
        else:
            uptime_percent = 100
            downtime_percent = 0
        print(uptime_percent,downtime_percent)
        # Получаем данные для последней недели и месяца
        weekly_uptime_time = 0
        monthly_uptime_time = 0
        for timestamp, status in data["status_history"]:
    
            if isinstance(timestamp, str):
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            if timestamp >= one_week_ago:
                if status == 1:
                    weekly_uptime_time += (now - timestamp).total_seconds()

            if timestamp >= one_month_ago:
                if status == 1:
                    monthly_uptime_time += (now - timestamp).total_seconds()
        print(monthly_uptime_time,weekly_uptime_time)
        # Для недельного и месячного периода считаем проценты
        weekly_total_time = (now - one_week_ago).total_seconds()
        monthly_total_time = (now - one_month_ago).total_seconds()

        # Проверка перед расчетом процентов за неделю и месяц
        print(f"Подсчет процентов за неделю и месяц для банкомата {device_id}: неделя = {weekly_uptime_time}, месяц = {monthly_uptime_time}")

        weekly_uptime_percent = round((weekly_uptime_time / weekly_total_time) * 100, 2) if weekly_total_time > 0 else 100
        monthly_uptime_percent = round((monthly_uptime_time / monthly_total_time) * 100, 2) if monthly_total_time > 0 else 100

        data["uptime_percent"] = uptime_percent
        data["downtime_percent"] = downtime_percent
        data["weekly_uptime_percent"] = weekly_uptime_percent
        data["monthly_uptime_percent"] = monthly_uptime_percent

    # Проверка результатов расчетов
    print("Расчет процентов завершен.")

    # Подготавливаем данные для отображения
    atm_list = []
    print("Подготовка данных для вывода на страницу.")
    for device_id, data in atm_status.items():
        atm_list.append({

            "device_id": device_id,
            "last_update": data["last_update"].strftime("%Y-%m-%d %H:%M:%S"),
            "last_status": "Работает" if data["last_status"] == 1 else "Не работает",
            "uptime_percent": f"{data['uptime_percent']}%",
            "downtime_percent": f"{data['downtime_percent']}%",
            "weekly_uptime_percent": f"{data['weekly_uptime_percent']}%",
            "monthly_uptime_percent": f"{data['monthly_uptime_percent']}%"
        })

    print(f"Подготовлено {len(atm_list)} банкоматов для вывода.")
    args["atms"] = atm_list

# Возвращаем шаблон с данными
    return render_template("listmessages.html", args=args)

@app.route("/map", endpoint="map", methods=["GET", "POST"])
@connect_db
@authorization
def listmessages(cursor, connection, args):
    args["title"] = "Карта"

    query = (
        f"SELECT * FROM atm"
    )
    cursor.execute(query)
    atms = cursor.fetchall()
    lines = []
    atm_links = []  # Список для хранения ссылок на банкоматы

    for atm in atms:
        coordinates = atm["ll"].replace("%2C", ",")
        lines.append(coordinates)
        # Генерация ссылки для Яндекс.Карт
        atm_link = f"https://yandex.ru/maps/?ll={coordinates}&z=18"
        atm_links.append(atm_link)  # Добавляем ссылку в список

    url = f"https://static-maps.yandex.ru/v1?ll=37.620070,55.753630&lang=ru_RU&size=450,450&z=10&size=600&pt={'~'.join(lines)}&apikey=f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
    print(url)

    args['image_url'] = url

    atm_list = []
    for atm, link in zip(atms, atm_links):  # Используем zip для объединения банкоматов и ссылок
        atm_list.append(f'Банкомат {atm["id"]}: <a href="{link}" target="_blank">{atm["ll"].replace("%2C", ",")}</a>')

    # Передаем список в args для отображения в шаблоне
    args['atm_list'] = atm_list

    return render_template("map.html", args=args)

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