import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'searchtool.settings')

app = Celery('searchtool')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
