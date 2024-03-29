# Generated by Django 4.0.3 on 2022-05-05 19:24

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('loginSystem', '0002_alter_booking_booking_id_alter_club_club_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='booking_id',
            field=models.UUIDField(default=uuid.UUID('7f27c57d-d695-422c-aafa-eccb9ea1df89'), primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='club',
            name='club_id',
            field=models.UUIDField(default=uuid.UUID('7b6f80fe-16c9-49fd-afc7-bcb8cf5787c3'), primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='film',
            name='film_id',
            field=models.UUIDField(default=uuid.UUID('e1b93bc7-e8de-487d-ac2c-f39ced233652'), primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='financeaccount',
            name='account_id',
            field=models.UUIDField(default=uuid.UUID('053a19bf-d098-405b-930b-168a28773488'), primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='screen',
            name='screen_id',
            field=models.UUIDField(default=uuid.UUID('1c1e337f-8b8b-4fc2-a8b2-13dbc364a3b1'), primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='seat',
            name='seat_id',
            field=models.UUIDField(default=uuid.UUID('61a9865b-6f6a-468c-ac51-bb9d46baf254'), primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='showing',
            name='showing_id',
            field=models.UUIDField(default=uuid.UUID('4d869a61-8bd6-42d4-9ccd-189bac2c1b7b'), primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transactionID',
            field=models.UUIDField(default=uuid.UUID('284aeb8e-3cbd-4c7d-8c49-f6ae8ca8d236'), editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
