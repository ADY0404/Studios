from django import forms
from apps.profiles.models import Profile, Appearance
from apps.accounts.validators import validate_username

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'display_name', 'title_tagline', 'bio', 'avatar', 'location', 
            'website', 'public_email', 'phone', 
            'is_verified', 'show_contact_form', 'show_save_contact', 'is_public'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Eddie Scott'}),
            'title_tagline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Founder, Designer & Tech Consultant'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Helping founders build scalable modern products...'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'San Francisco, CA'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://eddiescott.com'}),
            'public_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'hello@eddiescott.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_contact_form': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_save_contact': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UsernameChangeForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        validators=[validate_username],
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'new_handle'})
    )

    def __init__(self, current_profile=None, *args, **kwargs):
        self.current_profile = current_profile
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username'].lower().strip()
        validate_username(username)
        
        # Check if already taken by someone else
        qs = Profile.objects.filter(username=username)
        if self.current_profile:
            qs = qs.exclude(pk=self.current_profile.pk)
        if qs.exists():
            raise forms.ValidationError("This username is already taken by another creator.")
        return username


class AppearanceForm(forms.ModelForm):
    class Meta:
        model = Appearance
        fields = [
            'theme', 'bg_type', 'bg_color', 'bg_gradient', 'bg_image', 'bg_overlay_opacity', 'bg_blur',
            'banner_image', 'profile_alignment', 'avatar_shape', 'avatar_border',
            'button_style', 'button_shape', 'card_shadow', 'hover_effect', 
            'button_color', 'button_text_color', 'accent_color',
            'font_family', 'text_color',
            'social_position', 'social_style'
        ]
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-select', 'id': 'themeSelector'}),
            'bg_type': forms.Select(attrs={'class': 'form-select', 'id': 'bgTypeSelector'}),
            'bg_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'id': 'bgColorInput'}),
            'bg_gradient': forms.TextInput(attrs={'class': 'form-control', 'id': 'bgGradientInput'}),
            'bg_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'bgImageInput'}),
            'bg_overlay_opacity': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': '0', 'max': '90', 'step': '5', 'id': 'bgOverlayInput'}),
            'bg_blur': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': '0', 'max': '20', 'step': '1', 'id': 'bgBlurInput'}),
            
            'banner_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'bannerImageInput'}),
            'profile_alignment': forms.Select(attrs={'class': 'form-select', 'id': 'alignmentSelector'}),
            'avatar_shape': forms.Select(attrs={'class': 'form-select', 'id': 'avatarShapeSelector'}),
            'avatar_border': forms.Select(attrs={'class': 'form-select', 'id': 'avatarBorderSelector'}),

            'button_style': forms.Select(attrs={'class': 'form-select', 'id': 'buttonStyleSelector'}),
            'button_shape': forms.Select(attrs={'class': 'form-select', 'id': 'buttonShapeSelector'}),
            'card_shadow': forms.Select(attrs={'class': 'form-select', 'id': 'cardShadowSelector'}),
            'hover_effect': forms.Select(attrs={'class': 'form-select', 'id': 'hoverEffectSelector'}),
            'button_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'id': 'buttonColorInput'}),
            'button_text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'id': 'buttonTextColorInput'}),
            'accent_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'id': 'accentColorInput'}),

            'font_family': forms.Select(attrs={'class': 'form-select', 'id': 'fontFamilySelector'}),
            'text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'id': 'textColorInput'}),

            'social_position': forms.Select(attrs={'class': 'form-select', 'id': 'socialPositionSelector'}),
            'social_style': forms.Select(attrs={'class': 'form-select', 'id': 'socialStyleSelector'}),
        }
