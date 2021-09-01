from __future__ import absolute_import, unicode_literals
from datetime import timezone
import os

from celery import Celery
import celery
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealTimeStockNotify.settings')

app = Celery('RealTimeStockNotify')
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')
app.config_from_object(settings, namespace = 'CELERY')

app.conf.beat_schedule = {
    'every-10-seconds' : {
        'task' : 'Stocks.tasks.update_stocks',
        'schedule' : 10,
        'args' : (['RELIANCE.NS', 'BAJAJFINSV.NS'],)
    },
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')