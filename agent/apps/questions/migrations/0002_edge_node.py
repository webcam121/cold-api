# Generated by Django 3.1.6 on 2024-05-22 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('label', models.TextField()),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name': 'Node',
                'verbose_name_plural': 'Nodes',
            },
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('label', models.TextField()),
                ('source_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source', to='questions.node')),
                ('target_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target', to='questions.node')),
            ],
            options={
                'verbose_name': 'Edge',
                'verbose_name_plural': 'Edges',
            },
        ),
    ]
