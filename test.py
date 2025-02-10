{% extends "base.html" %} {% block content %}


<div class="container mt-5">
    <h2>Банкоматы</h2>
    <div class="map-container">
        <img src="{{ args['image_url'] }}" alt="Map" class="img-fluid">
        <h2>Список сломаных банкоматов:</h2>
        <ul>
            {% for atm in args['atm_list'] %}
                <li>{{ atm|safe }}</li>  <!-- Используем safe для отображения HTML-ссылок -->
            {% endfor %}
        </ul>
    </div>
</div>



{% endblock %}
