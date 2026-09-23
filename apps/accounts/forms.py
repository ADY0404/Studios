from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.validators import validate_username

class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        validators=[validate_username],
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'username_handle'})
    )
    display_name = forms.CharField(
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Eddie Scott'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'name@example.com'})
    )

    class Meta:
        model = User
        fields = ('username', 'display_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        validate_username(username)
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username


class AccountSettingsForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use by another account.")
        return email
