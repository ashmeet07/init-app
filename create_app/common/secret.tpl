SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-init-app-local-dev-key-change-me",
)
DEBUG = os.environ.get("DEBUG", "1").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = [
    host
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "localhost 127.0.0.1 [::1]",
    ).replace(",", " ").split()
    if host
]
