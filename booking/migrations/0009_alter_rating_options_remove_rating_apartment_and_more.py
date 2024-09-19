# Generated by Django 5.1.1 on 2024-09-19 09:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_rating_is_deleted_alter_reservation_is_deleted'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rating',
            options={'ordering': ['-updated_at'], 'verbose_name': 'Rating', 'verbose_name_plural': 'Ratings'},
        ),
        migrations.RemoveField(
            model_name='rating',
            name='apartment',
        ),
        migrations.AddField(
            model_name='rating',
            name='reservation',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='booking.reservation', verbose_name='Reservation'),
            preserve_default=False,
        ),
    ]
