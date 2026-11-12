from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('boutique/', views.boutique, name='boutique'),
    path( 'article/<int:article_id>/', views.detail_article, name='detail_article' ),
    path('panier/', views.panier, name='panier'),
    path( 'panier/ajouter/<int:article_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path( 'panier/retirer/<int:article_id>/', views.retirer_du_panier, name='retirer_du_panier'),
    path('gestion-produits/', views.gestion_produits, name='gestion_produits'),
    path('produit/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produit/modifier/<int:article_id>/', views.modifier_produit, name='modifier_produit'),
    path('produit/supprimer/<int:article_id>/', views.supprimer_produit, name='supprimer_produit'),
    path('contact/', views.contact, name='contact'),
    path('a-propos/', views.apropos, name='apropos'),
    ]