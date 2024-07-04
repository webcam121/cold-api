# Generated by Django 3.1.6 on 2024-05-16 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CallSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('call_title', models.CharField(blank=True, max_length=255, null=True)),
                ('started_at', models.DateTimeField()),
                ('pause_start_date', models.DateField(blank=True, null=True)),
                ('pause_end_date', models.DateField(blank=True, null=True)),
                ('frequency_unit', models.CharField(choices=[('DAY', 'Day'), ('WEEK', 'Week'), ('MONTH', 'Month')], help_text='Frequency unit for scheduling', max_length=55)),
                ('frequency_interval', models.IntegerField(default=1, help_text='Interval for scheduling frequency')),
                ('time_zone', models.CharField(choices=[('US/Eastern', 'US/Eastern'), ('US/Central', 'US/Central'), ('US/Mountain', 'US/Mountain'), ('US/Pacific', 'US/Pacific')], default='US/Eastern', help_text='Timezone to use for scheduling', max_length=50)),
                ('is_recurring', models.BooleanField(default=True, help_text='Is this a recurring schedule?')),
                ('description', models.TextField(blank=True, null=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='call_schedule', to='accounts.giftreceiver')),
            ],
            options={
                'verbose_name': 'Call Schedule',
                'verbose_name_plural': 'Call Schedules',
            },
        ),
        migrations.CreateModel(
            name='CallScheduleLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('scheduled_time', models.DateTimeField()),
                ('status', models.CharField(max_length=55)),
                ('call_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='call_schedule_log', to='call_schedules.callschedule')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='call_schedule_log', to='accounts.giftreceiver')),
            ],
            options={
                'verbose_name': 'Call Schedule Log',
                'verbose_name_plural': 'Call Schedule Logs',
            },
        ),
    ]
