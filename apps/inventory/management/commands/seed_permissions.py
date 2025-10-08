from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.inventory import models as inv

MATRIX = {
	'Administrateurs': {
		'*': ['add', 'change', 'delete', 'view']
	},
	'Marketing': {
		inv.Article: ['add', 'change', 'view'],
		inv.MouvementStock: ['add', 'change', 'view'],
		inv.Client: ['add', 'change', 'view'],
		inv.Projet: ['add', 'change', 'view'],
		inv.Famille: ['view'],
		inv.TypeProduit: ['view'],
		inv.Fabricant: ['view'],
		inv.ModeleProduit: ['view'],
		inv.Fournisseur: ['view'],
		inv.Emplacement: ['view'],
	},
	'Techniciens': {
		'*': ['view']
	}
}

class Command(BaseCommand):
	help = 'Assigne les permissions par défaut aux groupes.'

	def handle(self, *args, **options):
		for group_name, rules in MATRIX.items():
			group, _ = Group.objects.get_or_create(name=group_name)
			wanted_perms = set()
			if '*' in rules:
				# All models of this app
				for model in [inv.Famille, inv.TypeProduit, inv.Fabricant, inv.ModeleProduit, inv.Fournisseur, inv.Emplacement, inv.Client, inv.Projet, inv.Article, inv.MouvementStock]:
					ct = ContentType.objects.get_for_model(model)
					for action in rules['*']:
						codename = f"{action}_{model._meta.model_name}"
						perm = Permission.objects.get(content_type=ct, codename=codename)
						wanted_perms.add(perm)
			# Specific models
			for model, actions in rules.items():
				if model == '*':
					continue
				ct = ContentType.objects.get_for_model(model)
				for action in actions:
					codename = f"{action}_{model._meta.model_name}"
					perm = Permission.objects.get(content_type=ct, codename=codename)
					wanted_perms.add(perm)
			group.permissions.set(list(wanted_perms))
			self.stdout.write(self.style.SUCCESS(f"Permissions assignées pour {group_name} ({len(wanted_perms)})"))
