# Generated by Django 4.2.3 on 2024-02-14 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Narwhal_Tutoring', '0002_user_details_delete_timeslot_delete_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_details',
            name='degree',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='pfp_url',
            field=models.CharField(blank=True, max_length=104, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='student2_name',
            field=models.CharField(blank=True, max_length=101, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='student3_name',
            field=models.CharField(blank=True, max_length=102, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='suburb',
            field=models.CharField(blank=True, max_length=103, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='university',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
