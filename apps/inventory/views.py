from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth import logout as auth_logout
import csv
from datetime import datetime
from xhtml2pdf import pisa
from io import BytesIO
from .models import Article, MouvementStock, Famille, TypeProduit, Fabricant, ModeleProduit, Emplacement, Fournisseur, Client, Projet, Entrepot
from .forms import ArticleForm, EntreeForm, SortieForm


def logout_view(request):
	auth_logout(request)
	return redirect('login')


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
	articles = Article.objects.select_related('modele','emplacement','famille','type_produit','fabricant')
	q = request.GET.get('q','').strip()
	fam = request.GET.get('famille')
	fab = request.GET.get('fabricant')
	type_id = request.GET.get('type')
	if q:
		articles = articles.filter(description__icontains=q) | articles.filter(numero_serie__icontains=q)
	if fam:
		articles = articles.filter(famille__id=fam)
	if fab:
		articles = articles.filter(fabricant__id=fab)
	if type_id:
		articles = articles.filter(type_produit__id=type_id)
	context = {
		'articles': articles,
		'familles': Famille.objects.all(),
		'fabricants': Fabricant.objects.all(),
		'types': TypeProduit.objects.all(),
		'q': q,
		'fam': fam,
		'fab': fab,
		'type_id': type_id,
	}
	return render(request, 'inventory/article_list.html', context)


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
			mouvement = form.save()
			messages.success(request, "Sortie enregistrée.")
			return redirect('bon_sortie', mouvement_id=mouvement.id)
	else:
		form = SortieForm()
	return render(request, 'inventory/sortie_form.html', {'form': form})


@login_required
def mouvement_list(request):
	mouvements = MouvementStock.objects.select_related('article','client','projet_obj','entrepot')
	q = request.GET.get('q','').strip()
	date_de = request.GET.get('de','')
	date_a = request.GET.get('a','')
	entrepot_id = request.GET.get('entrepot')
	if q:
		mouvements = mouvements.filter(commentaire__icontains=q) | mouvements.filter(destination__icontains=q) | mouvements.filter(projet__icontains=q)
	# Date range filters (YYYY-MM-DD)
	try:
		if date_de:
			mouvements = mouvements.filter(date_mouvement__date__gte=datetime.strptime(date_de,'%Y-%m-%d').date())
		if date_a:
			mouvements = mouvements.filter(date_mouvement__date__lte=datetime.strptime(date_a,'%Y-%m-%d').date())
	except ValueError:
		pass
	if entrepot_id:
		mouvements = mouvements.filter(entrepot__id=entrepot_id)
	return render(request, 'inventory/mouvement_list.html', {'mouvements': mouvements, 'q': q, 'de': date_de, 'a': date_a, 'entrepots': Entrepot.objects.all(), 'entrepot_id': entrepot_id})


@login_required
@user_passes_test(lambda u: is_marketing(u) or is_admin(u))
def article_export_csv(request):
	response = HttpResponse(content_type='text/csv; charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="articles.csv"'
	writer = csv.writer(response)
	writer.writerow(['famille','type','fabricant','modele','numero_serie','description','prix_achat','cout_logistique','prix_desire','emplacement','fournisseur','quantite'])
	for a in Article.objects.select_related('famille','type_produit','fabricant','modele','emplacement','fournisseur'):
		writer.writerow([
			a.famille.libelle,
			a.type_produit.libelle,
			a.fabricant.nom,
			a.modele.nom,
			a.numero_serie,
			a.description,
			a.prix_achat,
			a.cout_logistique,
			a.prix_desire,
			a.emplacement.nom,
			a.fournisseur.nom if a.fournisseur else '',
			a.quantite,
		])
	return response


@login_required
@user_passes_test(lambda u: is_marketing(u) or is_admin(u))
def mouvement_export_csv(request):
	response = HttpResponse(content_type='text/csv; charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="mouvements.csv"'
	writer = csv.writer(response)
	writer.writerow(['date','type','article','quantite','entrepot','client','projet','destination','projet_texte','commentaire'])
	for m in MouvementStock.objects.select_related('article','client','projet_obj','entrepot'):
		writer.writerow([
			m.date_mouvement.isoformat(),
			m.type_mouvement,
			str(m.article),
			m.quantite,
			m.entrepot.nom if m.entrepot else '',
			m.client.nom if m.client else '',
			m.projet_obj.titre if m.projet_obj else '',
			m.destination,
			m.projet,
			m.commentaire,
		])
	return response


@login_required
@user_passes_test(lambda u: is_marketing(u) or is_admin(u))
def article_import_csv(request):
	if request.method == 'POST' and request.FILES.get('fichier'):
		f = request.FILES['fichier']
		decoded = f.read().decode('utf-8').splitlines()
		reader = csv.DictReader(decoded)
		created = 0
		for row in reader:
			famille, _ = Famille.objects.get_or_create(libelle=row['famille'].strip())
			type_produit, _ = TypeProduit.objects.get_or_create(famille=famille, libelle=row['type'].strip())
			fabricant, _ = Fabricant.objects.get_or_create(nom=row['fabricant'].strip())
			modele, _ = ModeleProduit.objects.get_or_create(fabricant=fabricant, nom=row['modele'].strip())
			emplacement, _ = Emplacement.objects.get_or_create(nom=row['emplacement'].strip())
			fournisseur = None
			if row.get('fournisseur'):
				fournisseur, _ = Fournisseur.objects.get_or_create(nom=row['fournisseur'].strip())
			article, created_flag = Article.objects.get_or_create(
				modele=modele,
				numero_serie=row['numero_serie'].strip(),
				defaults={
					'famille': famille,
					'type_produit': type_produit,
					'fabricant': fabricant,
					'description': row.get('description',''),
					'prix_achat': row.get('prix_achat') or 0,
					'cout_logistique': row.get('cout_logistique') or 0,
					'prix_desire': max(float(row.get('prix_desire') or 0), float(row.get('prix_achat') or 0) + float(row.get('cout_logistique') or 0)),
					'emplacement': emplacement,
					'fournisseur': fournisseur,
					'quantite': int(row.get('quantite') or 0),
				}
			)
			if created_flag:
				created += 1
		messages.success(request, f"Import terminé. Nouveaux articles: {created}.")
		return redirect('article_list')
	return render(request, 'inventory/article_import.html')


@login_required
@user_passes_test(lambda u: is_marketing(u) or is_admin(u))
def bon_sortie(request, mouvement_id:int):
	m = get_object_or_404(MouvementStock, pk=mouvement_id)
	return render(request, 'inventory/bon_sortie.html', {'m': m})


@login_required
@user_passes_test(lambda u: is_marketing(u) or is_admin(u))
def bon_sortie_pdf(request, mouvement_id:int):
	m = get_object_or_404(MouvementStock, pk=mouvement_id)
	html = render_to_string('inventory/bon_sortie.html', {'m': m})
	result = BytesIO()
	pdf = pisa.CreatePDF(src=html, dest=result)
	if pdf.err:
		return HttpResponse('Erreur de génération PDF', status=500)
	response = HttpResponse(result.getvalue(), content_type='application/pdf')
	response['Content-Disposition'] = f'attachment; filename=bon-sortie-{mouvement_id}.pdf'
	return response


@login_required
def clients_directory(request):
	clients = Client.objects.all()
	return render(request, 'inventory/clients.html', {'clients': clients})


@login_required
def projets_directory(request):
	projets = Projet.objects.select_related('client').all()
	return render(request, 'inventory/projets.html', {'projets': projets})


@login_required
def clients_export_csv(request):
	response = HttpResponse(content_type='text/csv; charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="clients.csv"'
	writer = csv.writer(response)
	writer.writerow(['nom','email','telephone','adresse'])
	for c in Client.objects.all():
		writer.writerow([c.nom,c.email,c.telephone,c.adresse])
	return response


@login_required
def projets_export_csv(request):
	response = HttpResponse(content_type='text/csv; charset=utf-8')
	response['Content-Disposition'] = 'attachment; filename="projets.csv"'
	writer = csv.writer(response)
	writer.writerow(['titre','client','code','actif'])
	for p in Projet.objects.select_related('client').all():
		writer.writerow([p.titre, p.client.nom, p.code, p.actif])
	return response
