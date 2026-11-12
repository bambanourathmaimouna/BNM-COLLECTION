from django.db import models


class Commande(models.Model):

    STATUTS = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_preparation', 'En préparation'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    MOYENS_PAIEMENT = [
            ('orange_money', 'Orange Money'),
            ('wave', 'Wave'),
            ('mtn_money', 'MTN Money'),
            ('moov_money', 'Moov Money'),
            ('livraison', 'Paiement à la livraison'),
        ]

    nom_client = models.CharField(max_length=150)

    telephone = models.CharField(max_length=20)

    email = models.EmailField(blank=True)

    adresse = models.TextField()

    ville = models.CharField(max_length=100)

    moyen_paiement = models.CharField( max_length=30,choices=MOYENS_PAIEMENT, default='livraison')

    montant_total = models.DecimalField( max_digits=10,decimal_places=2)

    statut = models.CharField( max_length=20, choices=STATUTS, default='en_attente')

    date_commande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.nom_client}"



class LigneCommande(models.Model):

    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes'
    )

    article = models.ForeignKey(
        'boutique.Article',
        on_delete=models.PROTECT
    )

    quantite = models.PositiveIntegerField()

    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def sous_total(self):
        return self.prix_unitaire * self.quantite

    def __str__(self):
        return f"{self.article.nom} - {self.quantite}"


    