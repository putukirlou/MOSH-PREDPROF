import datetime

def listmessages(atms_data):
    # Логирование входных данных
    print("Входные данные (банкоматы):", atms_data)

    # Считываем текущую дату для расчетов
    now = datetime.datetime.now()
    one_week_ago = now - datetime.timedelta(weeks=1)
    one_month_ago = now - datetime.timedelta(days=30)
    
    # Пример расчета для каждого банкомата
    for atm in atms_data:
        # Логируем текущий банкомат
        print(f"Обрабатываем банкомат {atm['device_id']}")

        # Инициализация переменных
        uptime_seconds = 0
        downtime_seconds = 0
        week_uptime_seconds = 0
        month_uptime_seconds = 0
        
        # Логируем последние статусы
        print(f"Последний статус: {atm['last_status']}")
        print(f"Последнее обновление: {atm['last_update']}")

        # Пример временных меток для расчетов
        last_update = datetime.datetime.strptime(atm['last_update'], "%Y-%m-%d %H:%M:%S")
        status_duration = (now - last_update).total_seconds()

        # Логируем разницу во времени
        print(f"Время с последнего обновления: {status_duration} секунд")

        # Если банкомат работает
        if atm['last_status'] == "Работает":
            uptime_seconds = status_duration
        else:
            downtime_seconds = status_duration

        # Логируем времена работы и простоя
        print(f"Время работы: {uptime_seconds} секунд")
        print(f"Время простоя: {downtime_seconds} секунд")

        # Если банкомат был с проблемами в течение последней недели/месяца
        if last_update >= one_week_ago:
            week_uptime_seconds = uptime_seconds
        if last_update >= one_month_ago:
            month_uptime_seconds = uptime_seconds

        # Логируем проценты работы
        total_time = uptime_seconds + downtime_seconds
        if total_time > 0:
            uptime_percent = (uptime_seconds / total_time) * 100
            downtime_percent = (downtime_seconds / total_time) * 100
        else:
            uptime_percent = downtime_percent = 0
        
        # Логируем проценты
        print(f"Процент работы: {uptime_percent}%")
        print(f"Процент простоя: {downtime_percent}%")
        
        # Проценты за неделю и месяц
        total_time_week = week_uptime_seconds + (downtime_seconds if last_update >= one_week_ago else 0)
        total_time_month = month_uptime_seconds + (downtime_seconds if last_update >= one_month_ago else 0)

        weekly_uptime_percent = (week_uptime_seconds / total_time_week) * 100 if total_time_week > 0 else 0
        monthly_uptime_percent = (month_uptime_seconds / total_time_month) * 100 if total_time_month > 0 else 0

        # Логируем проценты за неделю и месяц
        print(f"Процент работы за неделю: {weekly_uptime_percent}%")
        print(f"Процент работы за месяц: {monthly_uptime_percent}%")

        # Обновляем данные банкомата
        atm['uptime_percent'] = uptime_percent
        atm['downtime_percent'] = downtime_percent
        atm['weekly_uptime_percent'] = weekly_uptime_percent
        atm['monthly_uptime_percent'] = monthly_uptime_percent

        print(f"Обновленные данные для банкомата {atm['device_id']}: {atm}")

    # Возвращаем обновленные данные для дальнейшего использования
    return atms_data
