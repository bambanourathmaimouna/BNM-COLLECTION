from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import ArticleForm
from .models import Article
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from urllib.parse import quote
from django.shortcuts import redirect


def accueil(request):
    return render(request, 'accueil.html')


def boutique(request):
    articles = Article.objects.filter(disponible=True).order_by('-date_ajout')

    recherche = request.GET.get('recherche', '').strip()
    categorie = request.GET.get('categorie', '')
    prix_max = request.GET.get('prix_max', '')

    if recherche:
        articles = articles.filter(
            Q(nom__icontains=recherche) |
            Q(description__icontains=recherche)
        )

    if categorie:
        articles = articles.filter(categorie=categorie)

    if prix_max:
        try:
            articles = articles.filter(prix__lte=prix_max)
        except (ValueError, TypeError):
            prix_max = ''

    context = {
        'articles': articles,
        'recherche': recherche,
        'categorie_selectionnee': categorie,
        'prix_max': prix_max,
        'categories': Article._meta.get_field('categorie').choices,
    }

    return render(request, 'boutique.html', context)

def detail_article(request, article_id):
    article = get_object_or_404(
        Article,
        id=article_id,
        disponible=True
    )

    return render(request, 'detail_article.html', {
        'article': article
    })


def panier(request):
    panier_session = request.session.get('panier', {})

    articles_panier = []
    total = 0

    for article_id, quantite in panier_session.items():

        article = Article.objects.filter(
            id=article_id
        ).first()

        if article:
            quantite = int(quantite)
            sous_total = article.prix * quantite

            articles_panier.append({
                'article': article,
                'quantite': quantite,
                'sous_total': sous_total
            })

            total += sous_total

    return render(request, 'panier.html', {
        'articles_panier': articles_panier,
        'total': total
    })


@require_POST
def ajouter_au_panier(request, article_id):

    article = get_object_or_404(
        Article,
        id=article_id,
        disponible=True
    )

    panier_session = request.session.get('panier', {})

    identifiant = str(article.id)

    quantite_actuelle = int(
        panier_session.get(identifiant, 0)
    )

    if quantite_actuelle < article.stock:
        panier_session[identifiant] = quantite_actuelle + 1

    request.session['panier'] = panier_session
    request.session.modified = True

    return redirect('panier')


@require_POST
def retirer_du_panier(request, article_id):

    panier_session = request.session.get('panier', {})

    identifiant = str(article_id)

    if identifiant in panier_session:
        del panier_session[identifiant]

    request.session['panier'] = panier_session
    request.session.modified = True

    return redirect('panier')


# Liste des produits pour l'administration
@staff_member_required
def gestion_produits(request):
    articles = Article.objects.all().order_by('-date_ajout')

    produits_stock_faible = Article.objects.filter(
        stock__lte=5,
        disponible=True
    )

    return render(request, 'gestion_produits.html', {
        'articles': articles,
        'produits_stock_faible': produits_stock_faible,
    })


# Ajouter un produit
@staff_member_required
@require_http_methods(["GET", "POST"])
def ajouter_produit(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Le produit a été ajouté avec succès.")
            return redirect('gestion_produits')
    else:
        form = ArticleForm()

    return render(request, 'formulaire_produit.html', {
        'form': form,
        'titre': 'Ajouter un produit',
    })


# Modifier un produit
@staff_member_required
@require_http_methods(["GET", "POST"])
def modifier_produit(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        form = ArticleForm(
            request.POST,
            request.FILES,
            instance=article
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Le produit a été modifié avec succès.")
            return redirect('gestion_produits')
    else:
        form = ArticleForm(instance=article)

    return render(request, 'formulaire_produit.html', {
        'form': form,
        'titre': 'Modifier un produit',
    })


# Supprimer un produit
@staff_member_required
@require_http_methods(["GET", "POST"])
def supprimer_produit(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == 'POST':
        try:
            article.delete()
            messages.success(request, "Le produit a été supprimé.")
        except ProtectedError:
            messages.error(
                request,
                "Impossible de supprimer ce produit : il figure dans une ancienne commande."
            )

        return redirect('gestion_produits')

    return render(request, 'supprimer_produit.html', {
        'article': article
    })



from django.contrib import messages


def contact(request):
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        email = request.POST.get('email', '').strip()
        sujet = request.POST.get('sujet', '').strip()
        message = request.POST.get('message', '').strip()

        if nom and email and sujet and message:
            texte = (
                f"Bonjour BNM COLLECTION !\n\n"
                f"Nom : {nom}\n"
                f"E-mail : {email}\n"
                f"Sujet : {sujet}\n\n"
                f"Message : {message}"
            )

            url = f"https://wa.me/2250718174118?text={quote(texte)}"
            return redirect(url)

    return render(request, 'contact.html')

def apropos(request):
    return render(request, 'apropos.html')