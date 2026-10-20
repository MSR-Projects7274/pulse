from django.core.management.base import BaseCommand

from pulse.departments.models import Department


class Command(BaseCommand):
    help = 'Create the default Pulse departments.'

    def handle(self, *args, **options):
        # Define the default discussion areas created for a fresh database.
        departments = [
            ('General', 'General Discussions'),
            ('Development', 'Coding and Project Ideas'),
            ('Ideas', 'Brainstorming Sessions'),
            ('Announcements', 'Good News Everyone!'),
            ('Off-Topic', 'Everything Else'),
        ]

        # update_or_create keeps the command safe to run repeatedly.
        for name, description in departments:
            department, created = Department.objects.update_or_create(
                name=name,
                defaults={'description': description},
            )

            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(f'{action}: {department.name}')
            )
