from django.db import models

class Post(models.Model):
  post_title = models.CharField(max_length=200)
  post_body = models.CharField(max_length=1000)
  post_date = models.DateTimeField("date posted")

# Create your models here.
