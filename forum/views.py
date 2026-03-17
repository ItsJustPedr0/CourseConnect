from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.http import Http404
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Department
from .models import Course
from .models import Post
from .models import Prof

def index(request):
  dept_list = Department.objects.all()
  template = loader.get_template("forum/index.html")
  context = {"dept_list":dept_list}
  return HttpResponse(template.render(context, request))
# Create your views here.

def dept_index(request, abbrev):
  target_dept = get_object_or_404(Department, slug=abbrev)
  courses_list = Course.objects.filter(dept = target_dept.id)
  profs_list = Prof.objects.filter(dept = target_dept.id)
  template = loader.get_template("forum/dept_index.html")
  context = {"courses_list": courses_list, "profs_list": profs_list, "target_dept": target_dept}
  return HttpResponse(template.render(context, request))

def course_detail(request, abbrev, course_slug):
  target_dept = get_object_or_404(Department, slug=abbrev)
  target_course = get_object_or_404(Course, slug = course_slug)
  posts_list = Post.objects.filter(course = target_course.id)
  template = loader.get_template("forum/course_detail.html")
  context = {"posts_list": posts_list, "target_course": target_course}
  return HttpResponse(template.render(context, request))

def prof_detail(request, abbrev, prof_slug):
  target_dept = get_object_or_404(Department, slug=abbrev)
  target_prof = get_object_or_404(Prof, slug = prof_slug)
  posts_list = Post.objects.filter(prof = target_prof.id)
  template = loader.get_template("forum/prof_detail.html")
  context = {"posts_list": posts_list, "target_prof": target_prof}  
  return HttpResponse(template.render(context, request))

def search(request):
  query = request.GET.get('q', '')
  dept_slug = request.GET.get('dept', '')
  results = []
  
  if query:
    courses = Course.objects.filter(
      name__icontains=query) | Course.objects.filter(code__icontains=query)
    profs = Prof.objects.filter(
      first_name__icontains=query) | Prof.objects.filter(last_name__icontains=query)
    depts = Department.objects.filter(
      name__icontains=query) | Department.objects.filter(abbrev__icontains=query)

    if dept_slug:
      courses = courses.filter(dept__slug=dept_slug)
      profs = profs.filter(dept__slug=dept_slug)
      depts = depts.none()

    for dept in depts:
      results.append({
        'type': 'dept',
        'title': dept.name,
        'code': dept.abbrev,
        'url': f'/forum/{dept.slug}/'
      })

    for course in courses:
      results.append({
        'type': 'course',
        'title': course.name,
        'code': course.code,
        'url': f'/forum/{course.dept.slug}/course/{course.slug}/'
      })
    
    for prof in profs:
      results.append({
        'type': 'prof',
        'title': prof.full_name,
        'dept': prof.dept.name if prof.dept else '',
        'url': f'/forum/{prof.dept.slug}/prof/{prof.slug}/'
      })

  return JsonResponse({'results': results, 'query': query})