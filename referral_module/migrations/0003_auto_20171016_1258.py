# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-16 12:58
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referral_module', '0002_auto_20171016_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreferrer',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_referrers', to='referral_module.Campaign'),
        ),
    ]
