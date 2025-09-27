#!/usr/bin/env python
"""
Debug script to check static files configuration on cPanel
Run this on the server to diagnose static files issues
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, '/home1/naviposc/pos.navipos.co.ke')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_pos.settings')

try:
    django.setup()
    from django.conf import settings
    from django.contrib.staticfiles.finders import find
    
    print("=== Django Static Files Debug ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS: {getattr(settings, 'STATICFILES_DIRS', 'Not set')}")
    print(f"MIDDLEWARE: {settings.MIDDLEWARE}")
    print()
    
    # Check if static root exists and has files
    static_root = Path(settings.STATIC_ROOT)
    print(f"Static root exists: {static_root.exists()}")
    if static_root.exists():
        print(f"Static root permissions: {oct(static_root.stat().st_mode)[-3:]}")
        css_files = list(static_root.glob('**/*.css'))
        js_files = list(static_root.glob('**/*.js'))
        print(f"CSS files found: {len(css_files)}")
        print(f"JS files found: {len(js_files)}")
        
        # Check for specific files that are failing
        core_css = static_root / 'css' / 'core.css'
        scripts_js = static_root / 'js' / 'scripts.js'
        
        print(f"core.css exists: {core_css.exists()}")
        print(f"scripts.js exists: {scripts_js.exists()}")
        
        if core_css.exists():
            print(f"core.css permissions: {oct(core_css.stat().st_mode)[-3:]}")
            print(f"core.css size: {core_css.stat().st_size} bytes")
            
        if scripts_js.exists():
            print(f"scripts.js permissions: {oct(scripts_js.stat().st_mode)[-3:]}")
            print(f"scripts.js size: {scripts_js.stat().st_size} bytes")
    
    print()
    print("=== Django Finders Test ===")
    # Test Django's static files finders
    css_path = find('css/core.css')
    js_path = find('js/scripts.js')
    print(f"Django finds core.css at: {css_path}")
    print(f"Django finds scripts.js at: {js_path}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()