from django.core.management.base import BaseCommand
from kaizen_app.models import Profile

class Command(BaseCommand):
    help = 'Clean department data for coordinator and finance users'

    def handle(self, *args, **options):
        Profile.objects.filter(user_type__in=['coordinator', 'finance']).update(department=None)
        self.stdout.write(self.style.SUCCESS('Successfully cleaned department data'))