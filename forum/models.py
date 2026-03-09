from django.db import models

class Department(models.Model):
  department_name = models.CharField(max_length=100)
  def __str__(self):
    return self.department_name
  
class Prof(models.Model):
  prof_name = models.CharField(max_length=100)
  def __str__(self):
    return self.prof_name

class Course(models.Model):
  course_code = models.CharField(max_length=20)
  course_name = models.CharField(max_length=100)
  department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="courses")
  professor = models.ManyToManyField(Prof)
  def __str__(self):
    return self.course_code

class Post(models.Model):
  title = models.CharField(max_length=200)
  body = models.TextField()
  post_date = models.DateTimeField(auto_now_add=True) 
  prof = models.ForeignKey(Prof,on_delete=models.CASCADE, null=True, blank=True, related_name="posts")
  course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name="posts")
  def __str__(self):
    return self.title
# Create your models here.
