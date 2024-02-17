from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def signupuser(request):
    """Представлення реєстрації користувача"""

    if request.user.is_authenticated:
        return redirect(to='app_image:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():

            # створення нового користувача і збереження його в БД
            user = form.save(commit=False)
            user.save()

            # перенаправлення користувача на потрібну сторінку
            return redirect(to='app_image:home')
        else:
            # Если форма невалидна, отображаем ее с сообщениями об ошибках
            return render(request, 'users/signup.html', context={"form": form})

    # якщо запит GET, просто показуємо форму реєстрації
    return render(request, 'users/signup.html', context={"form": RegisterForm()})


def loginuser(request):
    """Представлення аутентифікації користувача"""

    if request.user.is_authenticated:
        return redirect(to='app_image:home')

    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is None:
            messages.error(request, 'Username or password didn\'t match')
            return redirect(to='users:login')

        login(request, user)
        return redirect(to='app_image:home')

    return render(request, 'users/login.html', context={"form": LoginForm()})


@login_required
def logoutuser(request):
    """Вихід із застосунку"""

    logout(request)
    return redirect(to='app_image:home_page')