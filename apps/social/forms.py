from django import forms
from apps.social.models import SocialAccount

class SocialAccountForm(forms.ModelForm):
    class Meta:
        model = SocialAccount
        fields = ['platform', 'url', 'is_active']
        widgets = {
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://instagram.com/yourhandle'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
