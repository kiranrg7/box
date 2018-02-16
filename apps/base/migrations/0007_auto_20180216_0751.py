# Generated by Django 2.0.2 on 2018-02-16 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20180216_0700'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='paid_till',
        ),
        migrations.AddField(
            model_name='profile',
            name='boxes_remaining',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='interests',
            field=models.CharField(blank=True, max_length=1024),
        ),
    ]
