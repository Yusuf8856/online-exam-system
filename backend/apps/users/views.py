from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "base.html")
def login_view(request):
    return render(request, 'auth/login.html')
def register_view(request):
    return render(request, 'auth/register.html')

