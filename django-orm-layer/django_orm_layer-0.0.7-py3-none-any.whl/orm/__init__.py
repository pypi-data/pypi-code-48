import os
import sys

import django

from .settings import MODULE_DIR, SETTING_NAME

sys.path.append(str(MODULE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{MODULE_DIR.name}.{SETTING_NAME}')

django.setup()
