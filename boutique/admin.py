from django.contrib import admin
from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = (
        'nom',
        'categorie',
        'prix',
        'stock',
        'disponible',
    )

    list_filter = ('categorie', 'disponible')

    search_fields = ('nom',)