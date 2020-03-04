from .base import *

DEBUG = False

DATABASES = {

     'default': {
         'NAME': 'smap_production',
         'ENGINE': 'django.db.backends.mysql',
         'USER': 'spendmetr',
         'PASSWORD': 'spend_db_local',
         'HOST': 'localhost',
         'PORT': '',
     }
}
