{% if venv_enabled in [True, 'yes', 'y', 'true'] %}
Activate venv:

source venv/bin/activate   (Linux / macOS)
venv\Scripts\activate      (Windows)
{% else %}
Virtual environment skipped.

Install requirements in your active environment before running the app:

python -m pip install -r requirements.txt
{% endif %}
