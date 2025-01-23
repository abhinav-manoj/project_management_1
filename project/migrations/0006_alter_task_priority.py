# Generated by Django 5.1.4 on 2025-01-20 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_comment_title_alter_file_task_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], default='Low', max_length=50),
        ),
    ]
