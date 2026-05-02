from django.urls import path
from . import views

urlpatterns = [
  path('', views.repository, name='repository'),
  path('upload/', views.upload_syllabus, name='upload_syllabus'),
  path('filter/', views.filter_syllabi, name='filter_syllabi'),
]