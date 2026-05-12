from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from forum.models import Prof, Course, Department

class Syllabus(models.Model):
  SEMESTER_CHOICES = [
    ('1', '1st Semester'),
    ('2', '2nd Semester'),
    ('0', 'Intercession'),
  ]

  dept = models.ForeignKey(Department, on_delete=models.CASCADE)
  course = models.ForeignKey(Course, on_delete=models.CASCADE)
  prof = models.ForeignKey(Prof, on_delete=models.SET_NULL, null=True, blank=True)
  file = models.FileField(upload_to='syllabi/syllabi/')
  semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
  school_year = models.CharField(max_length=9, help_text="e.g. 2024-2025")
  version = models.PositiveIntegerField(default=1)
  verified = models.BooleanField(default=False)

  class Meta:
    unique_together = ('prof', 'course', 'semester', 'school_year', 'version')
    verbose_name = 'Syllabus'
    verbose_name_plural = 'Syllabi'

  def __str__(self):
    first_year = self.school_year.split('-')[0].strip()
    return f"CS-{self.dept.slug}-{self.course.code}-{self.prof.slug}-{first_year}-{self.semester}"

# Signal to delete file when Syllabus object is deleted
@receiver(post_delete, sender=Syllabus)
def delete_syllabus_file(sender, instance, **kwargs):
  """Delete the file from storage when the Syllabus object is deleted"""
  if instance.file:
    # Delete the file from storage
    if instance.file.storage.exists(instance.file.name):
      instance.file.storage.delete(instance.file.name)