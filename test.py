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
    query_atm = "SELECT DISTINCT device_id FROM atm;"
    cursor.execute(query_atm)
    all_atms = {atm["device_id"]: {"status_history": []} for atm in cursor.fetchall()}

    # Обрабатываем сообщения, обновляя статусы банкоматов
    for message in messages:
        device_id = message["device_id"]
        timestamp = datetime.datetime.strptime(message["timestamp"], "%Y-%m-%d %H:%M:%S")
        status = 0 if "нужен механик" in message["details"].lower() else 1

        if device_id in all_atms:
            all_atms[device_id]["status_history"].append((timestamp, status))
            all_atms[device_id]["last_status"] = status
            all_atms[device_id]["last_update"] = timestamp

    # Текущая дата
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(days=7)
    month_ago = now - datetime.timedelta(days=30)

    for device_id, data in all_atms.items():
        statuses = data["status_history"]

        # Заполняем временные интервалы, если статусов мало
        if not statuses:
            data["week_percent"] = 0
            data["month_percent"] = 0
            continue

        # Если банкомат не получал сообщений недавно, но раньше работал, добавляем виртуальный статус
        last_time, last_status = statuses[-1]
        if last_time < now:
            statuses.append((now, last_status))

        # Подсчет времени работы за неделю и месяц
        week_work_time = 0
        month_work_time = 0
        total_week_time = 0
        total_month_time = 0

        for i in range(1, len(statuses)):
            prev_time, prev_status = statuses[i - 1]
            curr_time, _ = statuses[i]

            # Длительность интервала
            duration = (curr_time - prev_time).total_seconds()

            # Если этот интервал попадает в неделю
            if prev_time >= week_ago:
                total_week_time += duration
                if prev_status == 1:
                    week_work_time += duration

            # Если этот интервал попадает в месяц
            if prev_time >= month_ago:
                total_month_time += duration
                if prev_status == 1:
                    month_work_time += duration

        # Чтобы избежать деления на ноль
        if total_week_time > 0:
            data["week_percent"] = round((week_work_time / total_week_time) * 100, 2)
        else:
            data["week_percent"] = 0

        if total_month_time > 0:
            data["month_percent"] = round((month_work_time / total_month_time) * 100, 2)
        else:
            data["month_percent"] = 0

    # Подготавливаем данные для отображения
    atm_list = []
    for device_id, data in all_atms.items():
        if "last_update" in data:
            atm_list.append({
                "device_id": device_id,
                "last_update": data["last_update"].strftime("%Y-%m-%d %H:%M:%S"),
                "last_status": "Работает" if data["last_status"] == 1 else "Не работает",
                "week_percent": f"{data['week_percent']}%",
                "month_percent": f"{data['month_percent']}%"
            })

    args["atms"] = atm_list

    return render_template("listmessages.html", args=args)
