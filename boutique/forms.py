from django import forms
from .models import Article


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = [
            'nom',
            'description',
            'prix',
            'categorie',
            'image',
            'stock',
            'disponible',
        ]

        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du produit'
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prix en FCFA'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'disponible': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }