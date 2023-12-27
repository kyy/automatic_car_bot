import os

from .settings import *
from load_env import load_dotenv

load_dotenv = load_dotenv

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# correct collecting staticfiles
MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# define the correct URLs:
STATIC_URL = "server_django/static/"
MEDIA_URL = "server_django/media/"
STATIC_ROOT = '/home/mydomenb/repositories/automatic_car_bot/server_django/static/'
MEDIA_ROOT = '/home/mydomenb/repositories/automatic_car_bot/server_django/media/'

try:
    from .local import *
except ImportError:
    pass
