from pathlib import Path


SECRET_KEY = 'django-insecure-p$_#+@yk$m+#=4cq7w^z3qj=8_pv@--w&e0d!)dq3y0m1h5)+6'
DEBUG = True

ALLOWED_HOSTS = []
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'my_cache_table',
    }
}
