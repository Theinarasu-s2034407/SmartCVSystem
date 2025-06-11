from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from apps.authx.models import User


# Create your views here.

class DetailView(View):
    def get(self, request):
        return render(request, "profile/detailView.html")




