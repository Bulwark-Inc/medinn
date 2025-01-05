from django import forms
from allauth.account.forms import SignupForm
from .models import CustomUser

class CustomSignupForm(SignupForm):
    ROLE_CHOICES = CustomUser.ROLE_CHOICES
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    def save(self, request):
        user = super().save(request)
        user.role = self.cleaned_data.get('role')  # Set the role
        user.save()  # Save the user instance
        return user