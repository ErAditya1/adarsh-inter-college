from django.core.management.base import BaseCommand
from nouapp.models import User, Teacher, Student

class Command(BaseCommand):
    help = 'Deletes dummy users created by Faker'

    def handle(self, *args, **kwargs):
        # Delete Students and their linked users
        students = Student.objects.filter(user__email__contains='@')  # You can narrow this down further
        for student in students:
            user = student.user
            student.delete()
            user.delete()

        # Delete Teachers and their linked users
        teachers = Teacher.objects.filter(user__email__contains='@')  # Adjust if needed
        for teacher in teachers:
            user = teacher.user
            teacher.delete()
            user.delete()

        self.stdout.write(self.style.SUCCESS('Dummy data deleted successfully.'))
