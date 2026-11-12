from django.contrib import admin
from .models import Commande, LigneCommande


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ('article', 'quantite', 'prix_unitaire')


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nom_client',
        'telephone',
        'ville',
        'montant_total',
        'moyen_paiement',
        'statut',
        'date_commande',
    )

    list_filter = (
        'statut',
        'moyen_paiement',
        'date_commande',
    )

    search_fields = (
        'nom_client',
        'telephone',
        'email',
    )

    ordering = ('-date_commande',)

    inlines = [LigneCommandeInline]