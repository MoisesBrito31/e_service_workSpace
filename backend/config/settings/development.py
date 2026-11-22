from .base import *
import os

DEBUG = True

USE_SQLITE = os.getenv('USE_SQLITE', 'False').lower() in ('true', '1')

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # MySQL Database Configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'eservice_db'),
            'USER': os.getenv('DB_USER', 'eservice_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'eservice_password'),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
