from django.db import models


class Article(models.Model):

    CATEGORIES = [
        ('hijab', 'Hijabs et foulards'),
        ('abaya', 'Abayas et robes'),
        ('ensemble', 'Ensembles'),
        ('enfant', 'Collection enfants'),
    ]

    nom = models.CharField(max_length=200)

    description = models.TextField()

    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    categorie = models.CharField(
        max_length=20,
        choices=CATEGORIES
    )

    image = models.ImageField(
        upload_to='articles/'
    )

    stock = models.PositiveIntegerField(default=0)

    disponible = models.BooleanField(default=True)

    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom