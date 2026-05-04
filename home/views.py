from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.http import Http404, HttpResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm

@login_required(login_url='login')
def index(request):
  return render(request, "home/home.html")

CustomUser = get_user_model()

def signup(request):
  if request.user.is_authenticated:
    return redirect('home')
  
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user, backend='django.contrib.auth.backends.ModelBackend')
      return redirect('home')
  else:
    form = SignUpForm()
  
  return render(request, 'signup.html', {'form': form})


def login_view(request):
  if request.user.is_authenticated:
    return redirect('home')

  if request.method == 'POST':
    form = LoginForm(request.POST)
    if form.is_valid():
      student_id = form.cleaned_data['student_id']
      password = form.cleaned_data['password']

      user = authenticate(request, username=student_id, password=password)
      if user is not None:
        login(request, user)
        return redirect('home')
      else:
        form.add_error(None, 'Invalid student ID or password.')
  else:
    form = LoginForm()

  return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
  logout(request)
  return redirect('home')