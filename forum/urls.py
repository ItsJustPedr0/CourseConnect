from django.urls import path
from . import views

urlpatterns = [
  path("", views.index, name="index"),
  path('search/', views.search, name='search'),
  path("<str:abbrev>/", views.dept_index, name="dept_index"),
  path("<str:abbrev>/course/<str:course_slug>/", views.course_detail, name="course_detail"),
  path("<str:abbrev>/prof/<str:prof_slug>/", views.prof_detail, name="prof_detail")
] 