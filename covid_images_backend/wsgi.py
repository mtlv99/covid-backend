import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "covid_images_backend.settings")
application = get_wsgi_application()
