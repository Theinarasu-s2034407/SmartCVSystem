from django.shortcuts import render

# Create your views here.
def careers(request):
    return render(request, "careers/careers.html")