@app.route("/list-messages", endpoint="listmessages_page", methods=["GET", "POST"])
@connect_db
@authorization
def listmessages(cursor, connection, args):
    args["title"] = "Список сообщений"

    # Загружаем все сообщения, отсортированные по времени
    query = "SELECT * FROM messages ORDER BY timestamp ASC;"
    cursor.execute(query)
    messages = cursor.fetchall()

    # Загружаем список всех банкоматов
    query_atm = "SELECT * FROM atm;"
    cursor.execute(query_atm)
    atms = {atm["device_id"]: atm for atm in cursor.fetchall()}

    # Словарь для хранения статуса работы банкоматов
    atm_status = {}

    # Обрабатываем сообщения, обновляя статусы банкоматов
    for message in messages:
        device_id = message["device_id"]
        timestamp = datetime.datetime.strptime(message["timestamp"], "%Y-%m-%d %H:%M:%S")
        status = 0 if "нужен механик" in message["details"].lower() else 1

        # Обновляем статус и последнюю дату для каждого банкомата
        if device_id not in atm_status:
            atm_status[device_id] = {
                "last_status": status,
                "last_update": timestamp,
                "status_history": []
            }
        atm_status[device_id]["last_status"] = status
        atm_status[device_id]["last_update"] = timestamp
        atm_status[device_id]["status_history"].append((timestamp, status))

    # Рассчитываем процент работы за неделю и месяц
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)
    month_ago = now - datetime.timedelta(days=30)

    for device_id, data in atm_status.items():
        week_statuses = [s for t, s in data["status_history"] if t >= week_ago]
        month_statuses = [s for t, s in data["status_history"] if t >= month_ago]

        week_percent = round(sum(week_statuses) / len(week_statuses) * 100, 2) if week_statuses else 0
        month_percent = round(sum(month_statuses) / len(month_statuses) * 100, 2) if month_statuses else 0

        data["week_percent"] = week_percent
        data["month_percent"] = month_percent

    # Подготавливаем данные для отображения
    atm_list = []
    for device_id, data in atm_status.items():
        atm_list.append({
            "device_id": device_id,
            "last_update": data["last_update"].strftime("%Y-%m-%d %H:%M:%S"),
            "last_status": "Работает" if data["last_status"] == 1 else "Не работает",
            "week_percent": f"{data['week_percent']}%",
            "month_percent": f"{data['month_percent']}%"
        })

    args["atms"] = atm_list

    return render_template("listmessages.html", args=args)
