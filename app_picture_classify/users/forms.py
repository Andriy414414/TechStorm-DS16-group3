from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


# class RegisterForm(UserCreationForm):
#     """Реєстрація користувача"""

#     username = forms.CharField(max_length=100,
#                                required=True,
#                                widget=forms.TextInput())

#     email = forms.EmailField(max_length=254,
#                              required=True,
#                              widget=forms.EmailInput())

#     password1 = forms.CharField(max_length=50,
#                                 required=True,
#                                 widget=forms.PasswordInput())
#     password2 = forms.CharField(max_length=50,
#                                 required=True,
#                                 widget=forms.PasswordInput())

    # class Meta:
    #     model = User
    #     fields = ['username', 'email', 'password1', 'password2']


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
    )

    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Email"}),
    )

    password1 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )
    password2 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


# class LoginForm(AuthenticationForm):
#     """Аутентифікація зареєстрованого користувача"""

#     class Meta:
#         model = User
#         fields = ['username', 'password']

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "placeholder": "Username"})
        self.fields["password"].widget.attrs.update({"class": "form-control", "placeholder": "Password"})