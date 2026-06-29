import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = WhiteNoise(get_wsgi_application(), root=str(settings.STATIC_ROOT))

if settings.MEDIA_ROOT.exists():
    application.add_files(str(settings.MEDIA_ROOT), prefix="/media/")

if settings.WP_UPLOADS_ROOT.exists():
    application.add_files(str(settings.WP_UPLOADS_ROOT), prefix="/wp-content/uploads/")
