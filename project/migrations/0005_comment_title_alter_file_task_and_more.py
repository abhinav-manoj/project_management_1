# Generated by Django 5.1.3 on 2025-01-16 04:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_alter_comment_task'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='title',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.task'),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='end_date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='priority',
            field=models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Low', max_length=50),
        ),
        migrations.AlterField(
            model_name='project',
            name='team',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='task',
            name='assigned_to',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='environment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='reproducibility',
            field=models.CharField(choices=[('Always', 'Always'), ('Sometime', 'Sometime'), ('Rarely', 'Rarely'), ('Unable to Reproduce', 'Unable to Reproduce')], default='Always', max_length=50),
        ),
        migrations.AlterField(
            model_name='task',
            name='severity',
            field=models.CharField(choices=[('Critical', 'Critical'), ('Major', 'Major'), ('Minor', 'Minor'), ('Trivial', 'Trivial')], default='Critical', max_length=50),
        ),
        migrations.AlterField(
            model_name='task',
            name='steps_to_reproduce',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='tracker_type',
            field=models.CharField(choices=[('Task', 'Task'), ('Bug', 'Bug'), ('Feature request', 'Feature request'), ('Improvement', 'Improvement')], default='Task', max_length=50),
        ),
    ]
