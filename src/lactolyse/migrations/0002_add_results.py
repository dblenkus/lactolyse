# Generated by Django 2.0.6 on 2018-06-11 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('lactolyse', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='lactatethresholdanalyses',
            name='result_at2',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='lactatethresholdanalyses',
            name='result_at4',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='lactatethresholdanalyses',
            name='result_cross',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='lactatethresholdanalyses',
            name='result_dmax',
            field=models.IntegerField(null=True),
        ),
    ]
