# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-07 15:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('huddle_board', '0004_auto_20170807_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='board',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='huddle_board.Board', verbose_name='board'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='observation',
            name='card',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='observations', to='huddle_board.Card', verbose_name='card'),
            preserve_default=False,
        ),
    ]