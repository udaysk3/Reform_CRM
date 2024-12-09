from django.core.management.base import BaseCommand
from user.models import User
from decouple import config

users = [
    {
        'username': 'SystemS',
        'first_name': 'System',
        'last_name': 'S',
        'email': 'systems@reform-group.uk',
        'password': config('Systems_Password'),
    },
    {
        'username': 'UdayB',
        'first_name': 'Uday',
        'last_name': 'B',
        'email': 'burluudaysantoshkumar3@gmail.com',
        'password': config('Uday_Password'),
    },
    {
        'username': 'Sai Gowtham',
        'first_name': 'Sai',
        'last_name': 'P',
        'email': 'puvvulasaigowtham@gmail.com',
        'password':config('Gowtam_Password')
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
                dashboard= True,
                mcustomer= True,
                client= True,
                archive= True,
                admin= True,
                stage= True,
                finance= True,
                council=True,
                hr= True,
                globals= True,
                security= True,
                is_staff= True,
                is_superuser= True,
                customer= True,
                product= True,
                funding_route= True,
                CJ= True,
                QA= True,
                h_dashboard= True,
                h_employee= True,
                h_application= True,
                h_onboarding= True,
                h_timesheet= True,
                h_emp_action= True,
                h_emp_notify= True,
                h_offboarding= True,
                h_org_chart= True,
                knowledge_base= True,
                s_employee= True,
                s_role= True,
                s_client= True,
                suggestions= True,
                suggestion= True,
                new_suggestion= True,
            )
            self.stdout.write(self.style.SUCCESS(f"User {email} created successfully."))

        self.stdout.write(self.style.SUCCESS('All users processed.'))
