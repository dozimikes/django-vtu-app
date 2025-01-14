# your_project/celery.py

from __future__ import absolute_import, unicode_literals
import os
from lextrol.celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

app = Celery('your_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
