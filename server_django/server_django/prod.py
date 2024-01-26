from .settings import *
from load_env import load_dotenv

load_dotenv = load_dotenv

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['mush.by', 'www.mush.by']

# correct collecting staticfiles
MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# define the correct URLs:
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

try:
    from .local import *
except ImportError:
    pass
