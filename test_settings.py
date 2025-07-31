"""
Test settings for running tests locally without database connection issues
"""

from filmgozin_server.settings import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable email sending during tests
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable password validation for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Use a simple secret key for testing
SECRET_KEY = 'test-secret-key-for-testing-only'

# Disable debug for testing
DEBUG = False

# Disable static files collection
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage' 