from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from todo.models import Task

class Command(BaseCommand):
    help = "Insert Data to DataBase"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()


    def handle(self, *args, **options):

        user = User.objects.create(
            username = self.fake.user_name(),
            password = 'M32201513m',
            email = self.fake.email(),
            is_active = True,
            first_name = self.fake.name(),
            last_name = self.fake.last_name()
        )
        print(user)

        self.stdout.write(self.style.SUCCESS('Successfully Create User'))

        for i in range(5):
            task = Task.objects.create(
                user = user,
                title = self.fake.paragraph(nb_sentences=1)
            )
        print(task)
        self.stdout.write(self.style.SUCCESS('Successfully Create Task for User'))
