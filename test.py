<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1>{{ title }}</h1>
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th>ID банкомата</th>
                    <th>Последнее обновление</th>
                    <th>Последний статус</th>
                    <th>Процент работы</th>
                    <th>Процент простоя</th>
                    <th>Процент работы за неделю</th>
                    <th>Процент работы за месяц</th>
                </tr>
            </thead>
            <tbody>
                {% for atm in atms %}
                    <tr>
                        <td>{{ atm.device_id }}</td>
                        <td>{{ atm.last_update }}</td>
                        <td>{{ atm.last_status }}</td>
                        <td>{{ atm.uptime_percent }}%</td>
                        <td>{{ atm.downtime_percent }}%</td>
                        <td>{{ atm.weekly_uptime_percent }}%</td>
                        <td>{{ atm.monthly_uptime_percent }}%</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js"></script>
</body>
</html>
