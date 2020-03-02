from .base import *

DEBUG = False
ALLOWED_HOSTS = ['34.215.243.218',]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')