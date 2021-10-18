import os

# settings.pyからそのままコピー
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# settings.pyからそのままコピー
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

ALLOWED_HOSTS = [
    "BSS_APP_WITH_DJANGO.herokuapp.com",
    "127.0.0.1",
]
# ALLOWED_HOSTS = ['*']
DEBUG = True  # ローカルでDebugできるようになります
