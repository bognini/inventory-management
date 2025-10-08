from django.db import models
from django.core.validators import MinValueValidator


class Famille(models.Model):
	libelle = models.CharField(max_length=100, unique=True)

	class Meta:
		verbose_name = 'Famille'
		verbose_name_plural = 'Familles'

	def __str__(self) -> str:
		return self.libelle


class TypeProduit(models.Model):
	famille = models.ForeignKey(Famille, on_delete=models.CASCADE, related_name='types')
	libelle = models.CharField(max_length=100)

	class Meta:
		unique_together = ('famille', 'libelle')
		verbose_name = 'Type de produit'
		verbose_name_plural = 'Types de produit'

	def __str__(self) -> str:
		return f"{self.famille} / {self.libelle}"


class Fabricant(models.Model):
	nom = models.CharField(max_length=100, unique=True)

	class Meta:
		verbose_name = 'Fabricant'
		verbose_name_plural = 'Fabricants'

	def __str__(self) -> str:
		return self.nom


class ModeleProduit(models.Model):
	fabricant = models.ForeignKey(Fabricant, on_delete=models.CASCADE, related_name='modeles')
	nom = models.CharField(max_length=100)

	class Meta:
		unique_together = ('fabricant', 'nom')
		verbose_name = 'Modèle'
		verbose_name_plural = 'Modèles'

	def __str__(self) -> str:
		return f"{self.fabricant} {self.nom}"


class Fournisseur(models.Model):
	nom = models.CharField(max_length=100, unique=True)

	class Meta:
		verbose_name = 'Fournisseur'
		verbose_name_plural = 'Fournisseurs'

	def __str__(self) -> str:
		return self.nom


class Entrepot(models.Model):
	nom = models.CharField(max_length=100, unique=True)
	adresse = models.TextField(blank=True)

	class Meta:
		verbose_name = 'Entrepôt'
		verbose_name_plural = 'Entrepôts'

	def __str__(self) -> str:
		return self.nom


class Emplacement(models.Model):
	nom = models.CharField(max_length=100)
	entrepot = models.ForeignKey(Entrepot, on_delete=models.CASCADE, related_name='emplacements')

	class Meta:
		unique_together = ('nom','entrepot')
		verbose_name = 'Emplacement'
		verbose_name_plural = 'Emplacements'

	def __str__(self) -> str:
		return f"{self.entrepot} / {self.nom}"


class Client(models.Model):
	nom = models.CharField(max_length=150, unique=True)
	email = models.EmailField(blank=True)
	telephone = models.CharField(max_length=50, blank=True)
	adresse = models.TextField(blank=True)

	class Meta:
		verbose_name = 'Client'
		verbose_name_plural = 'Clients'

	def __str__(self) -> str:
		return self.nom


class Projet(models.Model):
	titre = models.CharField(max_length=150)
	client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projets')
	code = models.CharField(max_length=50, blank=True)
	actif = models.BooleanField(default=True)

	class Meta:
		verbose_name = 'Projet'
		verbose_name_plural = 'Projets'

	def __str__(self) -> str:
		return f"{self.titre} ({self.client})"


class Article(models.Model):
	famille = models.ForeignKey(Famille, on_delete=models.PROTECT)
	type_produit = models.ForeignKey(TypeProduit, on_delete=models.PROTECT)
	fabricant = models.ForeignKey(Fabricant, on_delete=models.PROTECT)
	modele = models.ForeignKey(ModeleProduit, on_delete=models.PROTECT)
	numero_serie = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	prix_achat = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
	cout_logistique = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)
	prix_desire = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
	emplacement = models.ForeignKey(Emplacement, on_delete=models.PROTECT)
	fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True)
	photo = models.ImageField(upload_to='articles/', blank=True, null=True)
	quantite = models.PositiveIntegerField(default=0)
	cree_le = models.DateTimeField(auto_now_add=True)
	maj_le = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('modele', 'numero_serie')
		verbose_name = 'Article'
		verbose_name_plural = 'Articles'

	def __str__(self) -> str:
		return f"{self.modele} / SN {self.numero_serie}"

	@property
	def cout_total(self):
		return (self.prix_achat or 0) + (self.cout_logistique or 0)


class StockEntrepot(models.Model):
	article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='stocks')
	entrepot = models.ForeignKey(Entrepot, on_delete=models.CASCADE, related_name='stocks')
	quantite = models.PositiveIntegerField(default=0)

	class Meta:
		unique_together = ('article','entrepot')
		verbose_name = 'Stock entrepôt'
		verbose_name_plural = 'Stocks entrepôt'

	def __str__(self) -> str:
		return f"{self.entrepot} - {self.article} : {self.quantite}"


class MouvementStock(models.Model):
	ENTREE = 'ENTREE'
	SORTIE = 'SORTIE'
	TYPE_CHOIX = [
		(ENTREE, 'Entrée'),
		(SORTIE, 'Sortie'),
	]

	article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='mouvements')
	type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOIX)
	quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	entrepot = models.ForeignKey(Entrepot, on_delete=models.PROTECT, null=True, blank=True)
	destination = models.CharField(max_length=255, blank=True)
	projet = models.CharField(max_length=255, blank=True)
	client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
	projet_obj = models.ForeignKey(Projet, on_delete=models.SET_NULL, null=True, blank=True)
	commentaire = models.TextField(blank=True)
	date_mouvement = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-date_mouvement']
		verbose_name = 'Mouvement de stock'
		verbose_name_plural = 'Mouvements de stock'

	def __str__(self) -> str:
		return f"{self.type_mouvement} {self.quantite} x {self.article}"
