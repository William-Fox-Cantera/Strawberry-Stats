web: gunicorn strawberry_visualizer.wsgi --log-file -
worker: python manage.py celery worker --loglevel=info