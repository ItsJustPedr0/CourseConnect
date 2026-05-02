from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.http import Http404, HttpResponse, JsonResponse
from .models import Department, Course, Post, Prof

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

def add_post(request):
  depts = Department.objects.all()
  profs = Prof.objects.none()
  courses = Course.objects.none()

  if request.method == 'POST':
    title = request.POST.get('title')
    body = request.POST.get('body')
    prof_id = request.POST.get('prof_id')
    course_id = request.POST.get('course_id')

    print("prof_id:", prof_id)
    print("course_id:", course_id)
    print("POST data:", request.POST)

    # handle prof
    if prof_id == 'NEW':
      first_name = request.POST.get('new_prof_first_name', '').strip()
      last_name = request.POST.get('new_prof_last_name', '').strip()
      if not first_name or not last_name:
          return HttpResponse("Please enter both first and last name.", status=400)
      dept_id = request.POST.get('dept_id')
      dept = get_object_or_404(Department, id=dept_id)
      prof = Prof.objects.create(
        first_name=first_name,
        last_name=last_name,
        dept=dept
      )
    else:
      prof = get_object_or_404(Prof, id=prof_id)

    # handle course
    if course_id == 'NEW':
      new_course_name = request.POST.get('new_course_name', '').strip()
      if not new_course_name:
        return HttpResponse("Please enter a course name.", status=400)
      
      dept = prof.dept
      if dept is None:
        return HttpResponse("Selected professor has no department assigned.", status=400)

      if ':' in new_course_name:
        code, name = new_course_name.split(':', 1)
        code = code.strip()
        name = name.strip()
      else:
        code = new_course_name
        name = new_course_name
      
      course = Course.objects.create(code=code, name=name, dept=dept)
      course.prof.add(prof)
    else:
      course = get_object_or_404(Course, id=course_id)

    Post.objects.create(title=title, body=body, prof=prof, course=course)
    return redirect('course_detail', abbrev=course.dept.slug, course_slug=course.slug)

  template = loader.get_template("forum/add_post.html")
  context = {"depts": depts, "profs": profs, "courses": courses}
  return HttpResponse(template.render(context, request))

def get_profs_by_dept(request):
  dept_id = request.GET.get('dept_id')
  dept = get_object_or_404(Department, id=dept_id)
  profs = Prof.objects.filter(dept=dept).values('id', 'first_name', 'last_name', 'slug')
  return JsonResponse({'profs': list(profs)})

def get_courses_by_prof(request):
  prof_id = request.GET.get('prof_id')
  prof = get_object_or_404(Prof, id=prof_id)
  courses = Course.objects.filter(prof=prof).values('id', 'name', 'code')
  return JsonResponse({'courses': list(courses)})

def get_courses_by_dept(request):
    dept_id = request.GET.get('dept_id')
    dept = get_object_or_404(Department, id=dept_id)
    courses = Course.objects.filter(dept=dept).values('id', 'name', 'code')
    return JsonResponse({'courses': list(courses)})