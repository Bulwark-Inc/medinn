from django.db import migrations

def create_groups(apps, schema_editor):
    # Get the Group model
    Group = apps.get_model('auth', 'Group')

    # Define the groups to create
    groups = ['admin', 'student']

    # Create the groups if they don't already exist
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
