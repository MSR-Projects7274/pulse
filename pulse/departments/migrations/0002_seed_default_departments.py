from django.db import migrations


def seed_default_departments(apps, schema_editor):
    Department = apps.get_model('departments', 'Department')

    departments = [
        ('General', 'General Discussions'),
        ('Development', 'Coding and Project Ideas'),
        ('Ideas', 'Brainstorming Sessions'),
        ('Announcements', 'Good News Everyone!'),
        ('Off-Topic', 'Everything Else'),
    ]

    for name, description in departments:
        Department.objects.update_or_create(
            name=name,
            defaults={'description': description},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            seed_default_departments,
            migrations.RunPython.noop,
        ),
    ]
