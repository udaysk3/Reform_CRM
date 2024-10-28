from django.core.management.base import BaseCommand
from user.models import User

users = [
    {
        'username': 'OliverH',
        'first_name': 'Oliver',
        'last_name': 'H',
        'email': 'Oliver.h@reform-group.uk',
        'password': 'Oliver@123',
    },
    {
        'username': 'SystemS',
        'first_name': 'System',
        'last_name': 'S',
        'email': 'systems@reform-group.uk',
        'password': 'Systems@123',
    },
    {
        'username': 'UdayB',
        'first_name': 'Uday',
        'last_name': 'B',
        'email': 'burluudaysantoshkumar3@gmail.com',
        'password': 'Uday@123',
    },
]

class Command(BaseCommand):
    help = 'Create users only once'

    def handle(self, *args, **options):
        for user_data in users:
            email = user_data['email']
            username = user_data['username']

            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"User with email {email} already exists. Skipping."))
                continue

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"User with username {username} already exists. Skipping."))
                continue

            User.objects.create_user(
                username=username,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=email,
                password=user_data['password'],
            )
            self.stdout.write(self.style.SUCCESS(f"User {email} created successfully."))

        self.stdout.write(self.style.SUCCESS('All users processed.'))
