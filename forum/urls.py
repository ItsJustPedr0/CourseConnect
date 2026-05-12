from django.urls import path
from . import views

urlpatterns = [
  path("", views.index, name="index"),  
  path('get-profs/', views.get_profs_by_dept, name='get_profs'),
  path('get-profs-by-course/', views.get_profs_by_course, name='get_profs_by_course'),
  path('get-courses/', views.get_courses_by_prof, name='get_courses'),
  path('get-courses-by-dept/', views.get_courses_by_dept, name='get_courses_by_dept'),
  path('add-post/', views.add_post, name="add_post"),
  path('search/', views.search, name='search'),
  path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
  path('post/<int:post_id>/report/', views.add_report, name='add_report'),
  path("<str:abbrev>/", views.dept_index, name="dept_index"),
  path("<str:abbrev>/course/<str:course_slug>/", views.course_detail, name="course_detail"),
  path("<str:abbrev>/prof/<str:prof_slug>/", views.prof_detail, name="prof_detail")
] 