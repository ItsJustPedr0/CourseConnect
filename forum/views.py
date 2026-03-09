from django.shortcuts import render
from django.http import HttpResponse

def index(request):
  return HttpResponse("Hello, world. You're at the forum page.")
# Create your views here.

def course_detail(request, course_code):
  return HttpResponse("Reviews of " % course_code)