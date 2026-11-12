from django.urls import path
from . import views

urlpatterns = [

    path(
        'passer-commande/',
        views.passer_commande,
        name='passer_commande'
    ),

    path(
        'tableau-de-bord/',
        views.tableau_de_bord,
        name='tableau_de_bord'
    ),

    path(
        'commande/<int:commande_id>/',
        views.detail_commande,
        name='detail_commande'
    ),

    path(
        'commande/<int:commande_id>/modifier-statut/',
        views.modifier_statut_commande,
        name='modifier_statut_commande'
    ),

path('suivre-commande/', views.suivre_commande, name='suivre_commande'),

]