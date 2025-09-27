import os
import sys

# Add your project directory to the sys.path
sys.path.insert(0, "/home1/naviposc/pos.navipos.co.ke")

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_pos.settings'

# Import Django and setup
import django
django.setup()

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()