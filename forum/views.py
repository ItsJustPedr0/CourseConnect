from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.http import Http404
from django.http import HttpResponse
from .models import Department
from .models import Course

def index(request):
  return HttpResponse("Hello, world. You're at the forum page.")
# Create your views here.

def course_index(request, abbrev):
  target_dept = get_object_or_404(Department, slug=abbrev)
  courses_list = Course.objects.filter(dept = target_dept.id)
  template = loader.get_template("forum/index.html")
  context = {"courses_list": courses_list}
  return HttpResponse(template.render(context, request))
