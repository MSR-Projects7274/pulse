from django.shortcuts import render, redirect

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.views.decorators.http import require_POST


def register_view(request):

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect("home")

    else:
        form = UserCreationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )


def login_view(request):

    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            login(
                request,
                form.get_user()
            )
            return redirect("home")

    else:
        form = AuthenticationForm(request)

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


@require_POST
def logout_view(request):

    logout(request)

    return redirect("home")