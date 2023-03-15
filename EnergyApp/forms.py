from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, EnergyProvider

PROVIDER_CHOICES = [
    ('', "Select One"),
    ("EDF", "EDF"),
    ("British Gas", "British Gas"),
    ("EON", "EON"),
]


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    dob = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    # Energy_Provider = forms.ChoiceField(choices=(('', 'Select One'), ("EDF","EDF"), ("BRITISH GAS","British Gas"), ("EON", "EON"), ("OTHER", "Other")))
    # Energy_Provider = forms.ChoiceField(choices = PROVIDER_CHOICES)
    Energy_Provider = forms.ModelChoiceField(
        queryset=EnergyProvider.objects.all(), empty_label="Select Provider")

    class Meta:
        model = User
        fields = ["username", "email", "dob",
                  "Energy_Provider", "password1", "password2"]

    def clean_provider_field(self):
        Energy_Provider = self.cleaned_data['Energy_Provider']
        if select_field == '':
            raise forms.ValidationError("Please select a value")
        return Energy_Provider


# logentry
# id
# password
# last_login
# is_superuser
# username
# first_name
# last_name
# email
# is_staff
# is_active
# date_joined
# groups
# user_permissions
