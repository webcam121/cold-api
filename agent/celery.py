from __future__ import absolute_import

import os
from time import time

import requests
from celery import Celery, signals
from celery.schedules import crontab
from django.conf import settings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


app = Celery('agent')

tasks = {}

slack_hook_url = 'https://hooks.slack.com/services/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'


@signals.task_prerun.connect
def task_prerun_handler(signal, sender, task_id, task, args, kwargs, **extras):
    tasks[task_id] = time()


@signals.task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, state=None, **kwargs):
    username = 'agent-production-celery-task-alert' if settings.ENVIRONMENT == 'production' else 'agent-staging-celery-task-alert'
    task_url = f'{settings.SITE_URL}/admin/django_celery_results/taskresult/?q={task_id}'

    try:
        task_runtime = time() - tasks.pop(task_id)
        if task_runtime > 120:
            requests.post(
                url=slack_hook_url,
                json={
                    'username': username,
                    'text': f'Task <{task_url}|{task.__name__}> run time is {task_runtime} seconds.',
                    'channel': 'celery-task-runtime-alert',
                },
            )
    except KeyError:
        pass

    if state == 'FAILURE':
        msg = f'Task <{task_url}|{task.__name__}> failed.'
        requests.post(
            url=slack_hook_url,
            json={
                'username': username,
                'text': msg,
                'channel': 'celery-alert',
            },
        )


@app.task(name="celery_beat_health_check")
def celery_beat_health_check():
    if settings.STATUS_CAKE_PUSH_URL is not None:
        requests.get(settings.STATUS_CAKE_PUSH_URL)


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# Celery configuration settings
app.conf.task_default_retry_delay = (60, 600, 3600)  # Retry after 1 min, 10 min, and 1 hour


app.conf.beat_schedule = {
    # 'every_day_send_delivery_email': {
    #     'task': 'agent.apps.deliveries.tasks.send_delivery_email_task',
    #     'schedule': crontab(minute=0, hour=16),
    # },
    # 'every_1h_send_abandoned_cart_notification_for_accounts_created_between_24_25_hrs_ago': {
    #     'task': 'agent.apps.notifications.tasks.send_abandoned_cart_notification_for_accounts_created_between_24_25_hrs_ago',  # noqa
    #     'schedule': crontab(minute=0),
    # },
    # 'every_1hr_check_scheduled_call_1': {
    #     'task': 'agent.apps.call_schedules.tasks.check_scheduled_call_task',
    #     'schedule': crontab(minute=29),
    # },
    # 'every_1hr_check_scheduled_call_2': {
    #     'task': 'agent.apps.call_schedules.tasks.check_scheduled_call_task',
    #     'schedule': crontab(minute=59),
    # },
    # 'every_1h_send_schedule_reminder_email_notification_to_giver': {
    #     'task': 'agent.apps.notifications.tasks.send_schedule_reminder_email_to_giver',  # noqa
    #     'schedule': crontab(minute=0),
    # },
    # 'every_1h_send_schedule_reminder_email_notification_to_receiver': {
    #     'task': 'agent.apps.notifications.tasks.send_schedule_reminder_email_to_receiver',  # noqa
    #     'schedule': crontab(minute=0),
    # },
    # 'every_day_check_free_trial_user_plans': {
    #     'task': 'agent.apps.memberships.tasks.check_free_trial_user_plans',
    #     'schedule': crontab(minute=0, hour=14),
    # },
    # 'every_minute_run_eta_tasks': {
    #     'task': 'agent.apps.eta_tasks.tasks.run_eta_tasks',
    #     'schedule': 60,
    # },
}
