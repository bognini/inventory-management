from django.contrib import admin
from .models import (
	Famille, TypeProduit, Fabricant, ModeleProduit,
	Fournisseur, Emplacement, Article, MouvementStock,
)

@admin.register(Famille)
class FamilleAdmin(admin.ModelAdmin):
	search_fields = ['libelle']

@admin.register(TypeProduit)
class TypeProduitAdmin(admin.ModelAdmin):
	list_display = ['libelle', 'famille']
	list_filter = ['famille']
	search_fields = ['libelle']

@admin.register(Fabricant)
class FabricantAdmin(admin.ModelAdmin):
	search_fields = ['nom']

@admin.register(ModeleProduit)
class ModeleProduitAdmin(admin.ModelAdmin):
	list_display = ['nom', 'fabricant']
	list_filter = ['fabricant']
	search_fields = ['nom']

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
	search_fields = ['nom']

@admin.register(Emplacement)
class EmplacementAdmin(admin.ModelAdmin):
	search_fields = ['nom']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
	list_display = ['modele', 'numero_serie', 'quantite', 'emplacement', 'fournisseur', 'prix_achat', 'cout_logistique', 'prix_desire']
	list_filter = ['famille', 'type_produit', 'fabricant', 'modele', 'emplacement']
	search_fields = ['numero_serie', 'description']

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
	list_display = ['type_mouvement', 'article', 'quantite', 'destination', 'projet', 'date_mouvement']
	list_filter = ['type_mouvement', 'date_mouvement']
	search_fields = ['destination', 'projet', 'commentaire']
