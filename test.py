@app.route("/list-messages", endpoint="listmessages_page", methods=["GET", "POST"])
@connect_db
@authorization
def listmessages(cursor, connection, args):
    args["title"] = "Список сообщений"

    # 1. Удаляем старые сообщения: оставляем только по одной (с максимальным id) для каждого device_id.
    delete_query = '''
    DELETE FROM messages
    WHERE id NOT IN (
        SELECT latest_id FROM (
            SELECT MAX(id) AS latest_id
            FROM messages
            GROUP BY device_id
        )
    );
    '''
    cursor.execute(delete_query)
    connection.commit()

    # 2. Выбираем только последнее сообщение для каждого банкомата.
    query_latest = '''
    SELECT m.*
    FROM messages m
    INNER JOIN (
        SELECT device_id, MAX(timestamp) AS latest_timestamp
        FROM messages
        GROUP BY device_id
    ) AS latest_messages
    ON m.device_id = latest_messages.device_id AND m.timestamp = latest_messages.latest_timestamp;
    '''
    cursor.execute(query_latest)
    messages = cursor.fetchall()
    messages = [dict(m) for m in messages]

    # 3. Функция для классификации статуса
    def classify_status(status_text):
        s = status_text.strip().capitalize()
        if s in ["Купюра зажевана", "Клавиатура не работает", "Найдены ошибки", "Не работает",
                 "Нет бумаги", "Нет свободного места", "Нет соединения", "Нуждается в замене",
                 "Ошибка механизма", "Обновление доступно", "Ошибка питания", "Ошибка связи",
                 "Ошибка сети", "Ошибка совместимости", "Ошибка чтения", "Плохое",
                 "Потеря соединения", "Принтер не работает", "Проблема с сетью",
                 "Проблемы с энергоснабжением", "Профилактическое", "Слабый сигнал",
                 "Техническая ошибка", "Техическая", "Пустой", "Потеря пакетов"]:
            return "Требуется механик"
        elif s in ["Нет наличных", "Низкий уровень наличных"]:
            return "Требуется машина инкассации"
        elif s in ["Настройки сброшены", "Устройство отключено", "Не удалось",
                   "Некоторые системы не работают", "Закрыто"]:
            return "В ремонте"
        else:
            return "Работает"

    # 4. Для каждого последнего сообщения вычисляем новый статус и добавляем его в запись.
    for m in messages:
        m["classified_status"] = classify_status(m["value"])

    args["messages"] = messages
    args["count"] = len(messages)

    return render_template("listmessages.html", args=args)



{% extends "base.html" %}
{% block content %}
<!DOCTYPE html>
<html>
  <head>
    <title>Список сообщений</title>
    <meta charset="utf-8">
    <style>
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th, td {
        padding: 10px;
        text-align: left;
        border: 1px solid #ddd;
      }
      th {
        background-color: #f2f2f2;
      }
    </style>
  </head>
  <body>
    <table id="myTable">
      <thead>
        <tr>
          <th onclick="sortTable(0)">Device ID</th>
          <th onclick="sortTable(1)">Timestamp</th>
          <th onclick="sortTable(2)">Status</th>
        </tr>
      </thead>
      <tbody>
        {% for item in args['messages'] %}
        <tr>
          <td>{{ item["device_id"] }}</td>
          <td>{{ item["timestamp"] }}</td>
          <td>{{ item["classified_status"] }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <script>
      function sortTable(columnIndex) {
          const table = document.getElementById("myTable");
          const rows = Array.from(table.rows).slice(1);
          const direction = table.dataset.sortDirection === "asc" ? -1 : 1; 
          const sortedRows = rows.sort((a, b) => {
              const aText = a.cells[columnIndex].innerText;
              const bText = b.cells[columnIndex].innerText;
              if (!isNaN(aText) && !isNaN(bText)) {
                  return (parseFloat(aText) - parseFloat(bText)) * direction;
              }
              return aText.localeCompare(bText) * direction;
          });
          table.dataset.sortDirection = direction === 1 ? "asc" : "desc";
          const tbody = table.querySelector("tbody");
          tbody.innerHTML = "";
          sortedRows.forEach(row => tbody.appendChild(row));
      }
    </script>
  </body>
</html>
{% endblock %}
