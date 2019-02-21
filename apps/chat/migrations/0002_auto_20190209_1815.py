# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-09 18:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='requests',
            field=models.ManyToManyField(related_name='_user_requests_+', to='chat.User'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=127, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='pic_url',
            field=models.TextField(blank=True),
        ),
    ]
