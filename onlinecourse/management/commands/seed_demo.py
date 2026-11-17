from io import BytesIO

from django.contrib.auth.models import User
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw

from onlinecourse.models import (
    Choice, Course, Enrollment, Instructor, Learner, Lesson, Question
)


class Command(BaseCommand):
    help = "Seed demo data for the online course final project"

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Site',
                'last_name': 'Administrator',
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('Admin12345!')
            admin.save()

        learner_user, created = User.objects.get_or_create(
            username='learner',
            defaults={'first_name': 'Alex', 'last_name': 'Johnson'}
        )
        if created:
            learner_user.set_password('Learner12345!')
            learner_user.save()
        Learner.objects.get_or_create(
            user=learner_user,
            defaults={'occupation': Learner.STUDENT,
                      'social_link': 'https://example.com/alex'}
        )

        instructor_user, created = User.objects.get_or_create(
            username='instructor',
            defaults={'first_name': 'Maria', 'last_name': 'Garcia'}
        )
        if created:
            instructor_user.set_password('Instructor12345!')
            instructor_user.save()
        instructor, _ = Instructor.objects.get_or_create(
            user=instructor_user,
            defaults={'full_time': True, 'total_learners': 1}
        )

        if Course.objects.filter(name='Cloud Computing').exists():
            self.stdout.write('Demo data already present.')
            return

        course = Course(
            name='Cloud Computing',
            description='Learn the fundamentals of cloud computing, '
                        'virtualization, and cloud service models.',
            pub_date=timezone.now().date(),
            total_enrollment=1
        )
        image = Image.new('RGB', (600, 300), (13, 110, 253))
        draw = ImageDraw.Draw(image)
        draw.text((60, 140), 'Cloud Computing', fill=(255, 255, 255))
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        course.image.save('cloud_computing.png', File(buffer), save=False)
        course.save()
        course.instructors.add(instructor)

        lesson1 = Lesson.objects.create(
            title='Introduction to Cloud Computing',
            order=0,
            course=course,
            content='<p>Cloud computing is the on-demand delivery of computing '
                    'resources over the internet. In this lesson you will learn '
                    'about virtualization, scalability, and the main benefits '
                    'of moving workloads to the cloud.</p>'
        )
        lesson2 = Lesson.objects.create(
            title='Cloud Service Models',
            order=1,
            course=course,
            content='<p>This lesson covers the three main cloud service models: '
                    'Infrastructure as a Service (IaaS), Platform as a Service '
                    '(PaaS), and Software as a Service (SaaS).</p>'
        )

        questions = [
            (lesson1,
             'Which cloud service model provides virtual machines and '
             'raw infrastructure?',
             ['Infrastructure as a Service (IaaS)',
              'Software as a Service (SaaS)',
              'Platform as a Service (PaaS)']),
            (lesson1,
             'Which characteristic allows cloud resources to scale '
             'automatically with demand?',
             ['Elasticity', 'Latency', 'Downtime']),
            (lesson2,
             'Which model delivers ready-to-use applications over '
             'the internet?',
             ['Software as a Service (SaaS)',
              'Infrastructure as a Service (IaaS)',
              'Platform as a Service (PaaS)']),
            (lesson2,
             'What does Platform as a Service provide to developers?',
             ['A platform to build, run, and manage applications without '
              'managing the underlying infrastructure',
              'Physical servers only',
              'Desktop operating systems']),
        ]
        for lesson, text, choices in questions:
            question = Question.objects.create(
                lesson=lesson, question_text=text, grade=50)
            for index, choice_text in enumerate(choices):
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=(index == 0)
                )

        Enrollment.objects.get_or_create(
            user=learner_user, course=course,
            defaults={'mode': Enrollment.AUDIT, 'rating': 5.0}
        )

        self.stdout.write(self.style.SUCCESS('Demo data created.'))
