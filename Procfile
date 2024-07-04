web: gunicorn --bind 127.0.0.1:8000 --workers=1 --threads=15 agent.wsgi:application
celery_worker: celery -A agent worker --pool=gevent --concurrency=500 --loglevel=INFO