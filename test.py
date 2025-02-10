from datetime import datetime, timedelta

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

    # Словарь для хранения статуса работы банкоматов и времени
    atm_status = {}

    # Время последней недели и месяца
    now = datetime.now()
    one_week_ago = now - timedelta(weeks=1)
    one_month_ago = now - timedelta(weeks=4)

    # Обрабатываем сообщения, обновляя статусы банкоматов
    for message in messages:
        device_id = message["device_id"]
        timestamp = datetime.strptime(message["timestamp"], "%Y-%m-%d %H:%M:%S")
        status = 1  # По умолчанию считаем, что банкомат работает

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

            if atm_status[device_id]["last_status"] == 1:
                atm_status[device_id]["total_time"] += time_difference  # Время работы
            else:
                atm_status[device_id]["down_time"] += time_difference  # Время неработающего состояния

            # Обновляем статус
            atm_status[device_id]["last_status"] = status
            atm_status[device_id]["last_update"] = timestamp

        # Добавляем статус в историю
        atm_status[device_id]["status_history"].append((timestamp, status))

    # Рассчитываем процент времени работы и неработы
    for device_id, data in atm_status.items():
        total_time = data["total_time"]
        down_time = data["down_time"]
        total_period = total_time + down_time

        if total_period > 0:
            uptime_percent = round((total_time / total_period) * 100, 2)
            downtime_percent = round((down_time / total_period) * 100, 2)
        else:
            uptime_percent = 100
            downtime_percent = 0

        # Получаем данные для последней недели и месяца
        weekly_uptime_time = 0
        monthly_uptime_time = 0
        for timestamp, status in data["status_history"]:
            if timestamp >= one_week_ago:
                if status == 1:
                    weekly_uptime_time += (now - timestamp).total_seconds()
            if timestamp >= one_month_ago:
                if status == 1:
                    monthly_uptime_time += (now - timestamp).total_seconds()

        # Для недельного и месячного периода считаем проценты
        weekly_total_time = (now - one_week_ago).total_seconds()
        monthly_total_time = (now - one_month_ago).total_seconds()

        weekly_uptime_percent = round((weekly_uptime_time / weekly_total_time) * 100, 2) if weekly_total_time > 0 else 100
        monthly_uptime_percent = round((monthly_uptime_time / monthly_total_time) * 100, 2) if monthly_total_time > 0 else 100

        data["uptime_percent"] = uptime_percent
        data["downtime_percent"] = downtime_percent
        data["weekly_uptime_percent"] = weekly_uptime_percent
        data["monthly_uptime_percent"] = monthly_uptime_percent

    # Подготавливаем данные для отображения
    atm_list = []
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

    args["atms"] = atm_list

    return render_template("listmessages.html", args=args)
