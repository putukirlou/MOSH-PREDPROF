def listmessages(cursor, connection, args):
    args["title"] = "Список сообщений"
    
    # Получаем все сообщения, отсортированные по времени
    query = "SELECT * FROM messages ORDER BY timestamp;"
    cursor.execute(query)
    messages = cursor.fetchall()
    
    query_atm = "SELECT device_id FROM atm;"
    cursor.execute(query_atm)
    atms = cursor.fetchall()
    
    atm_status = {}
    now = datetime.datetime.now()
    week_ago = now - datetime.timedelta(weeks=1)
    month_ago = now - datetime.timedelta(days=30)
    
    for atm in atms:
        device_id = atm["device_id"]
        query = "SELECT timestamp, details FROM messages WHERE device_id = ? ORDER BY timestamp;"
        cursor.execute(query, (device_id,))
        statuses = cursor.fetchall()
        
        last_status = None
        last_update = None
        week_work_time = 0
        month_work_time = 0
        total_week_time = 0
        total_month_time = 0
        prev_time = None
        prev_status = None
        
        for row in statuses:
            event_time = datetime.datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            status = 0 if "нужен механик" in row["details"].lower() else 1
            
            if prev_time is not None:
                time_diff = (event_time - prev_time).total_seconds()
                if prev_time >= week_ago:
                    total_week_time += time_diff
                    if prev_status == 1:
                        week_work_time += time_diff
                if prev_time >= month_ago:
                    total_month_time += time_diff
                    if prev_status == 1:
                        month_work_time += time_diff
            
            prev_time = event_time
            prev_status = status
            last_status = status
            last_update = event_time
        
        # Если последний статус был "нужен механик", считаем, что банкомат до сих пор сломан
        if last_status == 0 and last_update is not None:
            time_diff = (now - last_update).total_seconds()
            if last_update >= week_ago:
                total_week_time += time_diff
            if last_update >= month_ago:
                total_month_time += time_diff
        
        if total_week_time > 0:
            week_percent = (week_work_time / total_week_time) * 100
        else:
            week_percent = 0
        
        if total_month_time > 0:
            month_percent = (month_work_time / total_month_time) * 100
        else:
            month_percent = 0
        
        atm_status[device_id] = {
            "last_status": last_status,
            "last_update": last_update,
            "week_percent": round(week_percent, 2),
            "month_percent": round(month_percent, 2)
        }
    
    args["atm_status"] = atm_status
    return render_template("listmessages.html", args=args)
