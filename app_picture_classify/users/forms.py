from django import forms
<<<<<<< Updated upstream
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
=======
from django.contrib.auth.forms import UserCreationForm
>>>>>>> Stashed changes
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
<<<<<<< Updated upstream
    """Реєстрація користувача"""

=======
>>>>>>> Stashed changes
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput())

    email = forms.EmailField(max_length=254,
                             required=True,
                             widget=forms.EmailInput())

    password1 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput())

    class Meta:
        model = User
<<<<<<< Updated upstream
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    """Аутентифікація зареєстрованого користувача"""

    class Meta:
        model = User
        fields = ['username', 'password']
=======
        fields = ['username', 'password1', 'password2']
>>>>>>> Stashed changes
