from django.http import HttpResponse
from django.views import View
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .models import User

# Create your views here.

class LoginView(View):
    def get(self, request):
        return render(request, "authx/login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            print(e)
            return HttpResponse("Username not found")

        if password != user.password:
            return HttpResponse("Password Error")

        return render(request, "dashboard.html", {"user": user})



class RegisterView(View):
    def get(self, request):
        return render(request, "authx/register.html")

    def post(self, request):
        name = request.POST.get("username")
        passwd = request.POST.get("password")
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        user = User.objects.all()
        for i in user:
            if name == i.username:
                return HttpResponse("Username already exists")
        try:
            User.objects.create(username=name, password=passwd, email=email, first_name=first_name, last_name=last_name)
        except Exception as e:
            return HttpResponse("Register error")

        return redirect("authx:login")


class LogoutView(LoginRequiredMixin, View):
    """
    Logs out on GET and redirects to the login page.
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("authx:login")


class ForgetView(View):
    def get(self, request):
        return render(request, "authx/password-reset.html")


class AccountView(View):
    def get(self, request):
        return render(request, "profile/detailView.html")


class SearchView(View):
    def get(self, request):
        return render(request, "resumes/search.html")
