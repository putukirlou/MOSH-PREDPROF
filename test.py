{% extends "base.html" %}
{% block content %}
<!DOCTYPE html>

<html>
  <head>
    <title>Список сообщений</title>
    <meta charset="utf-8">
  </head>
  <body>
    <table>    <style>
      table {
        width: 100%;
        border-collapse: collapse; /* Чтобы убрать лишние промежутки между границами ячеек */
      }
      th, td {
        padding: 10px; /* Добавляем отступы внутри ячеек */
        text-align: left; /* Выравнивание текста в ячейке по левому краю */
        border: 1px solid #ddd; /* Добавляем границу вокруг ячеек */
      }
      th {
        background-color: #f2f2f2; /* Цвет фона для заголовков столбцов */
      }
    </style>
      <tr>
          <th>Банкомат</th>
          <th>Дата последнего статуса</th>
          <th>Последний статус</th>
          <th>Процент работы за неделю</th>
          <th>Процент работы за месяц</th>
      </tr>
      {% for atm in args["atms"] %}
      <tr>
          <td>{{ atm.device_id }}</td>
          <td>{{ atm.last_update }}</td>
          <td>{{ atm.last_status }}</td>
          <td>{{ atm.week_percent }}</td>
          <td>{{ atm.month_percent }}</td>
      </tr>
      {% endfor %}
  </table>

  </body>
</html>

{% endblock %}
