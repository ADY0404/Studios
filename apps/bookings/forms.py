from django import forms
from apps.bookings.models import Service, AvailabilityRule, Booking

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'duration_minutes', 'price', 'currency', 'instructions', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 30-Minute Strategy Call'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describe your service and what the client gets...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'min': 5, 'step': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'step': '0.01'}),
            'currency': forms.TextInput(attrs={'class': 'form-input', 'maxlength': 3}),
            'instructions': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Instructions displayed after booking (e.g. Zoom link info)'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class AvailabilityRuleForm(forms.ModelForm):
    class Meta:
        model = AvailabilityRule
        fields = ['day_of_week', 'start_time', 'end_time', 'is_active']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class BookingRequestForm(forms.Form):
    visitor_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Full Name', 'required': True})
    )
    visitor_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your.email@example.com', 'required': True})
    )
    visitor_phone = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number (optional)'})
    )
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'required': True})
    )
    booking_time = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'selectedTimeInput', 'required': True})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'What would you like to focus on?'})
    )
