# apps/usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'rol')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email == '':
            return None
        return email

class UsuarioChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = '__all__'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email == '':
            return None
        return email