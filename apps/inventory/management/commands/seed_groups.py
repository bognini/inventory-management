from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

DEFAULT_GROUPS = [
	'Administrateurs',
	'Marketing',
	'Techniciens',
]

class Command(BaseCommand):
	help = 'Crée les groupes par défaut (Administrateurs, Marketing, Techniciens).'

	def handle(self, *args, **options):
		created = 0
		for name in DEFAULT_GROUPS:
			group, was_created = Group.objects.get_or_create(name=name)
			if was_created:
				created += 1
		self.stdout.write(self.style.SUCCESS(f'Groupes en place. Nouveaux créés: {created}'))
