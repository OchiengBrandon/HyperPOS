# HyperPOS - Advanced Point of Sale System

A comprehensive Django-based Point of Sale (POS) system designed for small to medium businesses. HyperPOS offers intuitive sales processing, inventory management, customer relationship tools, and detailed analytics.

## Features

- **Intuitive Sales Interface**: Quick transaction processing with user-friendly design
- **Real-time Analytics**: Comprehensive reporting and dashboards
- **Inventory Management**: Automatic stock tracking with low-stock alerts
- **Customer Relationship**: Customer profiles and loyalty programs
- **Multiple Payment Options**: Support for various payment methods
- **Cloud-Based System**: Secure cloud solution with automatic backups
- **Multi-user Support**: Employee management with role-based access

## Tech Stack

- **Backend**: Django 4.2.5, Python 3.13+
- **Database**: MySQL (PyMySQL driver)
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Django Auth with custom user management
- **API**: Django REST Framework
- **Environment**: Environment-based configuration

## Quick Start

### Prerequisites

- Python 3.13+
- MySQL Server
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/OchiengBrandon/HyperPOS.git
   cd HyperPOS
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\\Scripts\\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MySQL Database**
   - Create a MySQL database named `hyperpos_local`
   - Update the `.env` file with your MySQL credentials

5. **Configure Environment Variables**
   ```bash
   # Update .env file with your settings
   DATABASE_NAME=hyperpos_local
   DATABASE_USER=root
   DATABASE_PASSWORD=your_password
   DATABASE_HOST=localhost
   DATABASE_PORT=3306
   ```

6. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Access the Application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/
   - POS System: http://127.0.0.1:8000/pos/

## Production Deployment (cPanel)

### Prerequisites
- cPanel hosting account with Python support
- MySQL database access
- Domain: pos.navipos.co.ke

### Deployment Steps

1. **Upload Files**
   - Upload all project files to your cPanel file manager
   - Place files in the document root: `/pos.navipos.co.ke/`

2. **Setup MySQL Database**
   - Create MySQL database via cPanel
   - Create database user with full privileges
   - Note the database name, username, and password

3. **Configure Environment**
   - Copy `.env.cpanel` to `.env`
   - Update the following settings:
   ```bash
   ENVIRONMENT=production
   SECRET_KEY=your-super-secret-production-key
   DEBUG=False
   ALLOWED_HOSTS=pos.navipos.co.ke,www.pos.navipos.co.ke,navipos.co.ke
   
   # Database settings (from cPanel MySQL)
   DATABASE_NAME=navipos_hyperpos
   DATABASE_USER=navipos_posuser
   DATABASE_PASSWORD=your_database_password
   
   # Email settings (from your hosting provider)
   EMAIL_HOST=mail.navipos.co.ke
   EMAIL_HOST_USER=noreply@navipos.co.ke
   EMAIL_HOST_PASSWORD=your_email_password
   
   # File paths
   STATIC_ROOT=/pos.navipos.co.ke/static
   MEDIA_ROOT=/pos.navipos.co.ke/media
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt --user
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Configure Web Server**
   - Set up WSGI configuration in cPanel
   - Point to `django_pos.wsgi:application`
   - Ensure Python path includes your project directory

### Environment Configuration

The application automatically detects the environment and configures itself accordingly:

- **Development**: Uses local MySQL, debug mode enabled, permissive CORS
- **Production**: Uses production MySQL, debug disabled, secure headers, restricted CORS

### File Structure

```
HyperPOS/
├── core/                   # Main app for landing page
├── pos_app/               # POS application logic
├── django_pos/            # Django project settings
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
├── templates/             # HTML templates
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .env.cpanel           # Production environment template
├── .gitignore            # Git ignore rules
└── manage.py             # Django management script
```

### Key URLs

- `/` - Landing page with features and demo access
- `/pos/` - POS system dashboard
- `/pos/login/` - User authentication
- `/pos/register/` - User registration
- `/demo/` - Demo access (redirects to login)
- `/admin/` - Django admin panel

### Security Features

- Environment-based configuration
- Secure headers in production
- CSRF protection
- SQL injection protection via Django ORM
- User authentication and authorization
- Secure password handling

### Support

- **Email**: brandonochieng72@gmail.com
- **Phone**: +254 (705) 980-652
- **Address**: Moi Avenue, Bungoma, TC 10101
- **Hours**: Mon-SAT: 9AM - 5PM EST

### Author

**Brandon Ochieng**
- GitHub: [@OchiengBrandon](https://github.com/OchiengBrandon)
- Email: brandonochieng72@gmail.com
- Location: Bungoma, Kenya

### Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Copyright & License

Copyright © 2025 Brandon Ochieng. All rights reserved.

This project is proprietary software developed by Brandon Ochieng. Unauthorized copying, modification, distribution, or use of this software, via any medium, is strictly prohibited without explicit written permission from the copyright owner.

**Commercial License Required** - Contact brandonochieng72@gmail.com for licensing inquiries.

---

**HyperPOS** - Transform Your Business Today!

*Developed with ❤️ by Brandon Ochieng*