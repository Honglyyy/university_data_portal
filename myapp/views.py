from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from myapp.forms import RegistrationForm


# Create your views here.
@login_required(login_url='/login')
def index(request):
    return render(request, 'myapp/base.html')

def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()

    return render(request, 'registration/sign_up.html', {'form': form})

