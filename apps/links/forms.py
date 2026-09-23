from django import forms
from apps.links.models import Link

class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['title', 'url', 'description', 'thumbnail', 'icon', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. My Latest YouTube Video'}),
            'url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://youtube.com/watch?v=...'}),
            'description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Brief description (optional)'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-input-file', 'accept': 'image/*'}),
            'icon': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
