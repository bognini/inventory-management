from django.urls import path
from . import views

urlpatterns = [
	path('', views.dashboard, name='dashboard'),
	path('articles/', views.article_list, name='article_list'),
	path('articles/nouveau/', views.article_create, name='article_create'),
	path('mouvements/', views.mouvement_list, name='mouvement_list'),
	path('mouvements/entree/', views.entree_stock, name='entree_stock'),
	path('mouvements/sortie/', views.sortie_stock, name='sortie_stock'),
]
