<table>
  <thead>
    <tr>
      <th>Device ID</th>
      <th>Последнее обновление</th>
      <th>Статус</th>
      <th>Процент работы</th>
      <th>Процент неработы</th>
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
      <td>{{ atm.uptime_percent }}</td>
      <td>{{ atm.downtime_percent }}</td>
      <td>{{ atm.weekly_uptime_percent }}</td>
      <td>{{ atm.monthly_uptime_percent }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
