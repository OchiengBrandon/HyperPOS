# HyperPOS cPanel Deployment Guide

## Prerequisites
- cPanel hosting account with Python support
- MySQL database created in cPanel
- Domain: pos.navipos.co.ke

## Step 1: Upload Files
1. Upload all project files to `/home1/naviposc/pos.navipos.co.ke/`
2. Ensure the virtual environment is set up: `/home1/naviposc/virtualenv/pos.navipos.co.ke/3.13/`

## Step 2: Environment Configuration
1. Copy `.env.cpanel` to `.env` in the project root:
   ```bash
   cp .env.cpanel .env
   ```

2. Update the `.env` file with your actual credentials:
   - `SECRET_KEY`: Generate a new secret key
   - `DATABASE_NAME`: Your cPanel MySQL database name  
   - `DATABASE_USER`: Your cPanel MySQL username
   - `DATABASE_PASSWORD`: Your cPanel MySQL password
   - `EMAIL_HOST_PASSWORD`: Your email password

## Step 3: Install Dependencies
```bash
cd /home1/naviposc/pos.navipos.co.ke
pip install -r requirements.txt
```

## Step 4: Static Files Collection
```bash
python manage.py collectstatic --noinput
```

This should create static files in: `/home1/naviposc/pos.navipos.co.ke/static/`

## Step 5: Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 6: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

## Step 7: Configure Web Server

### Create .htaccess in domain root (pos.navipos.co.ke)
```apache
RewriteEngine On

# Serve static files directly
RewriteRule ^static/(.*)$ /home1/naviposc/pos.navipos.co.ke/static/$1 [L]
RewriteRule ^media/(.*)$ /home1/naviposc/pos.navipos.co.ke/media/$1 [L]

# Pass everything else to Django
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /cgi-bin/django.cgi/$1 [QSA,L]
```

### Create django.cgi in cgi-bin directory
```python
#!/home1/naviposc/virtualenv/pos.navipos.co.ke/3.13/bin/python
import os
import sys

# Add project directory to Python path
sys.path.insert(0, '/home1/naviposc/pos.navipos.co.ke')

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_pos.settings'

# Setup Django
import django
django.setup()

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# For cPanel CGI
def application_wrapper(environ, start_response):
    return application(environ, start_response)

if __name__ == '__main__':
    from wsgiref.handlers import CGIHandler
    CGIHandler().run(application)
```

## Step 8: Set Permissions
```bash
chmod +x /home1/naviposc/public_html/cgi-bin/django.cgi
chmod 755 /home1/naviposc/pos.navipos.co.ke/static/
chmod 755 /home1/naviposc/pos.navipos.co.ke/media/
```

## Troubleshooting

### Static Files Not Loading (404 or MIME Type Errors)
1. Verify static files exist: `ls -la /home1/naviposc/pos.navipos.co.ke/static/`
2. Run collectstatic again: `python manage.py collectstatic --noinput --clear`
3. Check .htaccess rules are correct
4. Verify web server has read permissions on static directory

### Database Connection Issues
1. Check database credentials in `.env`
2. Verify database exists in cPanel
3. Test connection: `python manage.py dbshell`

### Permission Errors
1. Check file permissions: `chmod 644` for files, `chmod 755` for directories
2. Ensure virtual environment is accessible
3. Check that cgi-bin/django.cgi is executable: `chmod +x`

## Important Notes
- Always backup your database before migrations
- Test in a staging environment first
- Monitor error logs in cPanel for issues
- Static files are served directly by the web server, not Django