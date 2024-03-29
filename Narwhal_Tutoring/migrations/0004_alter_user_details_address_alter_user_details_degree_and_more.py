# Generated by Django 4.2.3 on 2024-02-16 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Narwhal_Tutoring', '0003_alter_user_details_degree_alter_user_details_pfp_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_details',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='degree',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='description',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='pfp_url',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='student1_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='student2_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='student3_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='suburb',
            field=models.CharField(blank=True, max_length=127, null=True),
        ),
        migrations.AlterField(
            model_name='user_details',
            name='university',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
