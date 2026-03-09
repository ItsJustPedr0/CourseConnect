from django.urls import path
from . import views

urlpatterns = [
  path("", views.index, name="index"),
  path("courses/<str:course_code>/", views.course_detail, name="course_detail")
]