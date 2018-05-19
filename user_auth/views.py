from django.shortcuts import render,redirect
from user_auth.forms import UserForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
# Create your views here.


def signup(request):

    if request.method == 'POST':
        form = UserForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if not password1 == password2:
                return redirect('signup')
            form.save()
            user = authenticate(username=username, password=password1)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('my_page')
    else:
        form = UserForm

    return render(request, 'user_auth/signup.html',
                  {'form': form})


def my_page(request):
    return render(request, 'user_auth/my_page.html',
                  {'profile_user': request.user})