# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-20 16:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_auto_20160520_0435'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='source',
        ),
        migrations.AlterField(
            model_name='build',
            name='status',
            field=models.CharField(choices=[('BUILDING', 'Building'), ('SUCCESS', 'Success'), ('FAILURE', 'Failure')], default='BUILDING', max_length=100),
        ),
        migrations.AlterField(
            model_name='build',
            name='version',
            field=models.CharField(default='', max_length=100),
        ),
    ]
