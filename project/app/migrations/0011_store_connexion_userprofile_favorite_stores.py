# Generated by Django 4.2.5 on 2023-10-03 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_merge_20231003_2237'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='connexion',
            field=models.PositiveIntegerField(default=0, verbose_name='단골'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='favorite_stores',
            field=models.ManyToManyField(to='app.store'),
        ),
    ]
