from django.urls import path
from . import views

urlpatterns = [
  path("", views.index, name="index"),

  path("<str:abbrev>", views.course_index, name="course_index")
]