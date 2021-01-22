"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from dj_static import Cling
from django.core.wsgi import get_wsgi_application
#from whitenoise.django import DjangoWhiteNoise


#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings") #変更

application = get_wsgi_application()

"""
application = Cling(get_wsgi_application())
application = DjangoWhiteNoise(application)
"""
