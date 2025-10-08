from django import forms
from .models import Article, MouvementStock

class ArticleForm(forms.ModelForm):
	serials_bulk = forms.CharField(label='Numéro(s) de série (un par ligne)', widget=forms.Textarea, required=False)

	class Meta:
		model = Article
		fields = ['famille','type_produit','fabricant','modele','numero_serie','description','prix_achat','cout_logistique','prix_desire','emplacement','fournisseur','photo']

	def clean(self):
		cleaned = super().clean()
		prix_achat = cleaned.get('prix_achat') or 0
		cout_log = cleaned.get('cout_logistique') or 0
		prix_desire = cleaned.get('prix_desire') or 0
		if prix_desire < prix_achat + cout_log:
			raise forms.ValidationError("Le prix désiré ne peut pas être inférieur au coût total (achat + logistique).")
		return cleaned

class EntreeForm(forms.ModelForm):
	class Meta:
		model = MouvementStock
		fields = ['article','quantite','commentaire']

	def save(self, commit=True):
		instance = super().save(commit=False)
		instance.type_mouvement = MouvementStock.ENTREE
		if commit:
			instance.save()
			article = instance.article
			article.quantite += instance.quantite
			article.save()
		return instance

class SortieForm(forms.ModelForm):
	class Meta:
		model = MouvementStock
		fields = ['article','quantite','destination','projet','commentaire']

	def clean(self):
		cleaned = super().clean()
		article = cleaned.get('article')
		quantite = cleaned.get('quantite') or 0
		if article and quantite > article.quantite:
			raise forms.ValidationError("Quantité demandée supérieure au stock disponible.")
		return cleaned

	def save(self, commit=True):
		instance = super().save(commit=False)
		instance.type_mouvement = MouvementStock.SORTIE
		if commit:
			instance.save()
			article = instance.article
			article.quantite -= instance.quantite
			article.save()
		return instance
