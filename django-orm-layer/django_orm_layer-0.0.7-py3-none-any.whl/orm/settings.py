from pathlib import Path

MODULE_DIR = Path(__file__).absolute().parent

SETTING_NAME = 'settings'

SECRET_KEY = 'cs(f9j+@hjg39ag2p53^9t#*_thm^2@-y=_#h8z_$jk44-*9z4'

INSTALLED_APPS = [
    # uncomment the following two lines if you want to use the buildin User model and others.
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',

    f'{MODULE_DIR.name}.example_1',
    f'{MODULE_DIR.name}.example_2',
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# ENGINE:
# 'django.db.backends.postgresql'
# 'django.db.backends.mysql'
# 'django.db.backends.sqlite3'
# 'django.db.backends.oracle'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(MODULE_DIR.joinpath('../db.sqlite3')),
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'test_django',
#         'USER': 'postgres',
#         'PASSWORD': '',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'mydatabase',
#         'USER': 'mydatabaseuser',
#         'PASSWORD': 'mypassword',
#         'HOST': '127.0.0.1',
#         'PORT': '3306',
#     }
# }
