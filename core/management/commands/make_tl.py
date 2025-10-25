from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Promote a user to Team Lead (staff)'

    def add_arguments(self, parser):
        parser.add_argument('username')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User {username} promoted to Team Lead'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User not found'))
