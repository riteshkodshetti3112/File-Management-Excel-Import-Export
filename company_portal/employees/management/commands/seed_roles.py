from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

ROLES = ['HR', 'Manager', 'Employee']


class Command(BaseCommand):
    help = "Creates the default role groups: HR, Manager, Employee."

    def handle(self, *args, **options):
        for role in ROLES:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group: {role}"))
            else:
                self.stdout.write(f"Group already exists: {role}")
