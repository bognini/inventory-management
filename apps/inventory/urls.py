from django.urls import path
from . import views

urlpatterns = [
	path('', views.dashboard, name='dashboard'),
	path('articles/', views.article_list, name='article_list'),
	path('articles/nouveau/', views.article_create, name='article_create'),
	path('articles/export.csv', views.article_export_csv, name='article_export_csv'),
	path('articles/importer/', views.article_import_csv, name='article_import_csv'),
	path('mouvements/', views.mouvement_list, name='mouvement_list'),
	path('mouvements/entree/', views.entree_stock, name='entree_stock'),
	path('mouvements/sortie/', views.sortie_stock, name='sortie_stock'),
	path('mouvements/export.csv', views.mouvement_export_csv, name='mouvement_export_csv'),
	path('mouvements/bon/<int:mouvement_id>/', views.bon_sortie, name='bon_sortie'),
	path('mouvements/bon/<int:mouvement_id>/pdf/', views.bon_sortie_pdf, name='bon_sortie_pdf'),
	path('repertoire/clients/', views.clients_directory, name='clients_directory'),
	path('repertoire/projets/', views.projets_directory, name='projets_directory'),
	path('repertoire/clients/export.csv', views.clients_export_csv, name='clients_export_csv'),
	path('repertoire/projets/export.csv', views.projets_export_csv, name='projets_export_csv'),
]
