from django.db import models
from django.utils.text import slugify

class Department(models.Model):
  name = models.CharField(max_length=100)
  abbrev = models.CharField(max_length=10, unique=True, null=True, blank=True)
  slug = models.SlugField(unique=True, blank=True)
  
  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.abbrev)
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name
  
class Prof(models.Model):
  last_name = models.CharField(max_length=100, null=True, blank=True)
  first_name = models.CharField(max_length=100, null=True, blank=True)
  slug = models.SlugField(unique=True, blank=True)

  @property
  def full_name(self):
    return f"{self.first_name} {self.last_name}"

  def save(self, *args, **kwargs):
    if not self.slug:
      initials = "".join(name[0] for name in self.first_name.split())
      self.slug = slugify(f"{initials}-{self.last_name}")
    super().save(*args, **kwargs)

  def __str__(self):
    return self.full_name

class Course(models.Model):
  code = models.CharField(max_length=20, unique=True)
  name = models.CharField(max_length=100)
  dept = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="courses")
  prof = models.ManyToManyField(Prof)
  slug = models.SlugField(unique=True, blank=True)
  
  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.code)
    super().save(*args, **kwargs)

  def __str__(self):
    return self.code

class Post(models.Model):
  title = models.CharField(max_length=200)
  body = models.TextField()
  post_date = models.DateTimeField(auto_now_add=True) 
  prof = models.ForeignKey(Prof,on_delete=models.CASCADE, null=True, blank=True, related_name="posts")
  course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name="posts")
  def __str__(self):
    return self.title
# Create your models here.
