from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.http import Http404
from django.http import HttpResponse

def index(request):
  return render(request, "home/home.html")