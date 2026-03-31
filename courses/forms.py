import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        label=_('Email'),
        max_length=254,
        help_text=_('Required. Enter a valid email address.')
    )
    username = forms.CharField(
        label=_('Username'),
        max_length=150,
        validators=[MinLengthValidator(3)],
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check for allowed characters
            if not re.match(r'^[\w.@+-]+$', username):
                raise forms.ValidationError(
                    _('Username can only contain letters, digits and @/./+/-/_')
                )
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('A user with that email already exists.'))
        return email.lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return user
