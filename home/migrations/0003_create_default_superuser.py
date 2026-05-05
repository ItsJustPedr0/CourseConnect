# Generated migration to create a default superuser on database initialization

from django.db import migrations
import os


def create_default_superuser(apps, schema_editor):
    CustomUser = apps.get_model('home', 'CustomUser')
    
    student_id = os.getenv('SUPERUSER_STUDENT_ID', 'admin')
    email = os.getenv('SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('SUPERUSER_PASSWORD', 'admin123')
    
    if not CustomUser.objects.filter(student_id=student_id).exists():
        CustomUser.objects.create_superuser(
            student_id=student_id,
            email=email,
            password=password
        )


def reverse_superuser(apps, schema_editor):
    CustomUser = apps.get_model('home', 'CustomUser')
    student_id = os.getenv('SUPERUSER_STUDENT_ID', 'admin')
    CustomUser.objects.filter(student_id=student_id).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_customuser_managers_remove_customuser_username'),
    ]

    operations = [
        migrations.RunPython(create_default_superuser, reverse_superuser),
    ]
