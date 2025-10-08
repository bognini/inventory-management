from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Article, MouvementStock
from .forms import ArticleForm, EntreeForm, SortieForm


def is_admin(user):
	return user.is_superuser or user.groups.filter(name__in=['Administrateurs']).exists()


def is_marketing(user):
	return user.is_superuser or user.groups.filter(name__in=['Marketing']).exists()


def is_technicien(user):
	return user.is_superuser or user.groups.filter(name__in=['Techniciens']).exists()


@login_required
def dashboard(request):
	context = {
		'total_articles': Article.objects.count(),
		'total_quantite': sum(a.quantite for a in Article.objects.all()),
		'derniers_mouvements': MouvementStock.objects.select_related('article')[:10],
	}
	return render(request, 'inventory/dashboard.html', context)


@login_required
@user_passes_test(lambda u: is_marketing(u) or is_admin(u))
def article_create(request):
	if request.method == 'POST':
		form = ArticleForm(request.POST, request.FILES)
		if form.is_valid():
			serials_bulk = form.cleaned_data.get('serials_bulk')
			if serials_bulk:
				serials = [s.strip() for s in serials_bulk.splitlines() if s.strip()]
				created = 0
				for sn in serials:
					article = form.save(commit=False)
					article.numero_serie = sn
					article.pk = None
					article.save()
					created += 1
				messages.success(request, f"{created} article(s) créés.")
				return redirect('article_list')
			else:
				form.save()
				messages.success(request, "Article créé.")
				return redirect('article_list')
	else:
		form = ArticleForm()
	return render(request, 'inventory/article_form.html', {'form': form})


@login_required
def article_list(request):
	articles = Article.objects.select_related('modele','emplacement')
	return render(request, 'inventory/article_list.html', {'articles': articles})


@login_required
@user_passes_test(lambda u: is_marketing(u) or is_admin(u))
def entree_stock(request):
	if request.method == 'POST':
		form = EntreeForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Entrée enregistrée.")
			return redirect('mouvement_list')
	else:
		form = EntreeForm()
	return render(request, 'inventory/entree_form.html', {'form': form})


@login_required
@user_passes_test(lambda u: is_marketing(u) or is_admin(u))
def sortie_stock(request):
	if request.method == 'POST':
		form = SortieForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Sortie enregistrée.")
			return redirect('mouvement_list')
	else:
		form = SortieForm()
	return render(request, 'inventory/sortie_form.html', {'form': form})


@login_required
def mouvement_list(request):
	mouvements = MouvementStock.objects.select_related('article')
	return render(request, 'inventory/mouvement_list.html', {'mouvements': mouvements})
