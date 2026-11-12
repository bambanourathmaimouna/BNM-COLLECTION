from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods

from boutique.models import Article
from .models import Commande, LigneCommande

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from boutique.models import Article
from django.db import models


@require_http_methods(["GET", "POST"])

def passer_commande(request):

    panier_session = request.session.get('panier', {})

    if not panier_session:
        messages.error(request, "Votre panier est vide.")
        return redirect('panier')

    if request.method == 'POST':

        nom = request.POST.get('nom', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        email = request.POST.get('email', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        ville = request.POST.get('ville', '').strip()
        moyen_paiement = request.POST.get('moyen_paiement', 'livraison')
        moyens_autorises = [choix[0] for choix in Commande.MOYENS_PAIEMENT]

        if moyen_paiement not in moyens_autorises:
            messages.error(request, "Moyen de paiement invalide.")
            return redirect('passer_commande')

        if not all([nom, telephone, adresse, ville]):
            messages.error( request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('passer_commande')

        try:
            with transaction.atomic():

                articles_a_commander = []
                total = Decimal('0.00')

                for article_id, quantite in panier_session.items():

                    article = Article.objects.select_for_update().get(
                        id=int(article_id),
                        disponible=True
                    )

                    quantite = int(quantite)

                    if quantite <= 0 or quantite > article.stock:
                        raise ValueError(
                            f"Stock insuffisant pour {article.nom}."
                        )

                    sous_total = article.prix * quantite
                    total += sous_total

                    articles_a_commander.append(
                        (article, quantite)
                    )

                commande = Commande.objects.create(
                    nom_client=nom,
                    telephone=telephone,
                    email=email,
                    adresse=adresse,
                    ville=ville,
                    moyen_paiement=moyen_paiement,
                    montant_total=total
                )

                for article, quantite in articles_a_commander:

                    LigneCommande.objects.create(
                        commande=commande,
                        article=article,
                        quantite=quantite,
                        prix_unitaire=article.prix
                    )

                    article.stock -= quantite
                    article.save(update_fields=['stock'])

            request.session['panier'] = {}
            request.session.modified = True

            return render(
                request,
                'commande_confirmee.html',
                {'commande': commande}
            )

        except (Article.DoesNotExist, ValueError, TypeError):
            messages.error(
                request,
                "Un article n'est plus disponible ou son stock est insuffisant. Vérifiez votre panier."
            )
            return render(request, 'passer_commande.html')

    return render(request, 'commande.html')


@staff_member_required
def tableau_de_bord(request):
    chiffre_affaires = Commande.objects.exclude(
        statut='annulee'
    ).aggregate(total=Sum('montant_total'))['total'] or Decimal('0.00')

    nombre_commandes = Commande.objects.count()
    commandes_attente = Commande.objects.filter(statut='en_attente').count()
    commandes_livrees = Commande.objects.filter(statut='livree').count()
    nombre_produits = Article.objects.filter(disponible=True).count()

    # Récupérer les filtres
    statut = request.GET.get('statut', '')
    recherche = request.GET.get('recherche', '').strip()

    # Toutes les commandes
    commandes = Commande.objects.all().order_by('-date_commande')

    # Filtrer par statut
    if statut:
        commandes = commandes.filter(statut=statut)

    # Rechercher un client par nom ou téléphone
    if recherche:
        commandes = commandes.filter(
            models.Q(nom_client__icontains=recherche) |
            models.Q(telephone__icontains=recherche)
        )

    context = {
        'chiffre_affaires': chiffre_affaires,
        'nombre_commandes': nombre_commandes,
        'commandes_attente': commandes_attente,
        'commandes_livrees': commandes_livrees,
        'nombre_produits': nombre_produits,
        'dernieres_commandes': commandes[:10],
        'statuts': Commande.STATUTS,
        'statut_selectionne': statut,
        'recherche': recherche,
    }

    return render(request, 'tableau_de_bord.html', context)

@staff_member_required
def detail_commande(request, commande_id):

    commande = get_object_or_404(
        Commande,
        id=commande_id
    )

    lignes = commande.lignes.select_related(
        'article'
    ).all()

    return render(
        request,
        'detail_commande.html',
        {
            'commande': commande,
            'lignes': lignes,
            'statuts': Commande.STATUTS,
        }
    )


@staff_member_required
@require_POST
def modifier_statut_commande(request, commande_id):

    commande = get_object_or_404(
        Commande,
        id=commande_id
    )

    nouveau_statut = request.POST.get('statut')

    statuts_autorises = [
        choix[0] for choix in Commande.STATUTS
    ]

    if nouveau_statut not in statuts_autorises:

        messages.error(
            request,
            "Statut de commande invalide."
        )

        return redirect(
            'detail_commande',
            commande_id=commande.id
        )

    commande.statut = nouveau_statut
    commande.save(update_fields=['statut'])

    messages.success(
        request,
        "Le statut de la commande a été modifié avec succès."
    )

    return redirect(
        'detail_commande',
        commande_id=commande.id
    )


def suivre_commande(request):
    commande = None
    lignes = None
    erreur = None

    if request.method == 'POST':
        numero = request.POST.get('numero_commande', '').strip()
        telephone = request.POST.get('telephone', '').strip()

        if not numero or not telephone:
            erreur = "Veuillez remplir tous les champs."

        elif not numero.isdigit():
            erreur = "Le numéro de commande est invalide."

        else:
            commande = Commande.objects.filter(id=int(numero)).first()

            # Comparer les numéros en ignorant les espaces,
            # les tirets et le signe +
            if commande:
                telephone_commande = ''.join(
                    caractere for caractere in commande.telephone
                    if caractere.isdigit()
                )

                telephone_saisi = ''.join(
                    caractere for caractere in telephone
                    if caractere.isdigit()
                )

                if telephone_commande != telephone_saisi:
                    commande = None

            if commande is None:
                erreur = (
                    "Aucune commande trouvée. "
                    "Vérifiez votre numéro de commande et votre téléphone."
                )
            else:
                lignes = commande.lignes.select_related('article').all()

    return render(
        request,
        'suivre_commande.html',
        {
            'commande': commande,
            'lignes': lignes,
            'erreur': erreur,
        }
    )



def suivre_commande(request):
    commande = None
    erreur = None

    if request.method == 'POST':
        numero_commande = request.POST.get('numero_commande', '').strip()
        telephone = request.POST.get('telephone', '').strip()

        if not numero_commande or not telephone:
            erreur = "Veuillez remplir tous les champs."
        else:
            try:
                commande = Commande.objects.filter(
                    id=int(numero_commande),
                    telephone=telephone
                ).first()

                if commande is None:
                    erreur = "Aucune commande trouvée. Vérifiez les informations saisies."

            except ValueError:
                erreur = "Le numéro de commande est invalide."

    return render(
        request,
        'suivre_commande.html',
        {
            'commande': commande,
            'erreur': erreur,
        }
    )