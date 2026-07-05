Project ready.

Location:

{{ project_path }}

Quick start:

cd {{ project_path }}
python -m pip install -r requirements.txt
{% if framework == 'django' %}
python manage.py runserver
{% else %}
python app.py
{% endif %}

If install stops early, fix the requirements issue first; otherwise the framework package
will not be installed and the development server command can report a missing module.

Open:

http://localhost:{{ port if (port and port != 'na') else 8000 }}
http://localhost:{{ port if (port and port != 'na') else 8000 }}/health
