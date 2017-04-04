from cloudkitchen.settings.dev import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('KEFFKAFFE_DB_NAME'),
        'USER': os.getenv('KEFFKAFFE_DB_USER'),
        'PASSWORD': os.getenv('KEFFKAFFE_DB_PASSWORD'),
        'HOST': os.getenv('KEFFKAFFE_DB_HOST'),
        'PORT': os.getenv('KEFFKAFFE_DB_PORT'),
    }
}
