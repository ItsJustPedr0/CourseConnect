from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from forum.models import Department, Course, Prof
from .models import Syllabus
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def repository(request):
  dept_list = Department.objects.all()
  course_list = Course.objects.all()
  prof_list = Prof.objects.all()
  syllabi = Syllabus.objects.all()
  context = {
    'dept_list': dept_list,
    'course_list': course_list,
    'prof_list': prof_list,
    'syllabi': syllabi
  }
  return render(request, 'syllabi/repository.html', context)

def upload_syllabus(request):
  if request.method == 'POST':
    dept_id = request.POST.get('dept_id')
    course_id = request.POST.get('course_id')
    prof_id = request.POST.get('prof_id')
    semester = request.POST.get('semester')
    school_year = request.POST.get('school_year')
    file = request.FILES.get('file')

    if not file:
      return HttpResponse("Please upload a syllabus file.", status=400)
    if not semester or not school_year:
      return HttpResponse("Please select a semester and school year.", status=400)

    dept = get_object_or_404(Department, id=dept_id)

    if prof_id == 'NEW':
      first_name = request.POST.get('new_prof_first_name', '').strip()
      last_name = request.POST.get('new_prof_last_name', '').strip()
      prof = Prof.objects.create(first_name=first_name, last_name=last_name, dept=dept)
    else:
      prof = get_object_or_404(Prof, id=prof_id)

    if course_id == 'NEW':
      new_course_name = request.POST.get('new_course_name', '').strip()
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

    # auto increment version
    latest = Syllabus.objects.filter(
      prof=prof,
      course=course,
      semester=semester,
      school_year=school_year
    ).order_by('-version').first()

    version = (latest.version + 1) if latest else 1

    Syllabus.objects.create(
      dept=dept,
      course=course,
      prof=prof,
      file=file,
      semester=semester,
      school_year=school_year,
      version=version
    )
    return redirect('repository')

  return redirect('repository')
  
def filter_syllabi(request):
  dept_id = request.GET.get('dept_id', '')
  course_id = request.GET.get('course_id', '')
  prof_id = request.GET.get('prof_id', '')
  query = request.GET.get('q', '')

  from django.db.models import Q
  syllabi = Syllabus.objects.all()

  if dept_id:
    syllabi = syllabi.filter(dept__id=dept_id)
  if course_id:
    syllabi = syllabi.filter(course__id=course_id)
  if prof_id:
    syllabi = syllabi.filter(prof__id=prof_id)
  if query:
    syllabi = syllabi.filter(
        Q(course__name__icontains=query) |
        Q(course__code__icontains=query) |
        Q(prof__last_name__icontains=query) |
        Q(prof__first_name__icontains=query)
    )

  results = []
  for s in syllabi:
    results.append({
      'id': s.id,
      'dept_id': s.dept.id,
      'course_id': s.course.id,
      'prof_id': s.prof.id if s.prof else None,
      'course': f"{s.course.code}: {s.course.name}",
      'prof': s.prof.full_name if s.prof else '',
      'term': f"{s.school_year} - {s.get_semester_display()}",
      'version': s.version,
      'verified': s.verified,
      'file_url': s.file.url,
    })

  return JsonResponse({'syllabi': results})