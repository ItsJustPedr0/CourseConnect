import tempfile
import shutil

from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings

from forum.models import Department, Prof, Course
from .models import Syllabus

CustomUser = get_user_model()

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SyllabiViewsTests(TestCase):
  @classmethod
  def tearDownClass(cls):
    shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
    super().tearDownClass()

  def setUp(self):
    self.user = CustomUser.objects.create_user(student_id='232022', password='TestPass123')
    self.client.login(username='232022', password='TestPass123')
    self.dept = Department.objects.create(name='Engineering', abbrev='ENG')
    self.prof = Prof.objects.create(first_name='Jane', last_name='Doe', dept=self.dept)
    self.course = Course.objects.create(code='ENG101', name='Intro to Engineering', dept=self.dept)
    self.course.prof.add(self.prof)
    self.syllabus_file = SimpleUploadedFile('syllabus.pdf', b'PDF content', content_type='application/pdf')

  def test_repository_requires_login(self):
    self.client.logout()
    response = self.client.get(reverse('repository'))
    self.assertRedirects(response, f"{reverse('login')}?next={reverse('repository')}")

  def test_repository_view_renders_lists(self):
    response = self.client.get(reverse('repository'))
    self.assertEqual(response.status_code, 200)
    self.assertIn(self.dept, response.context['dept_list'])
    self.assertIn(self.course, response.context['course_list'])
    self.assertIn(self.prof, response.context['prof_list'])

  def test_upload_syllabus_creates_record_and_redirects(self):
    response = self.client.post(
      reverse('upload_syllabus'),
      {
        'dept_id': str(self.dept.id),
        'prof_id': str(self.prof.id),
        'course_id': str(self.course.id),
        'semester': '1',
        'school_year': '2024-2025'
      },
      files={'file': self.syllabus_file}
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, reverse('repository'))
    syllabus = Syllabus.objects.get(course=self.course, prof=self.prof)
    self.assertEqual(syllabus.version, 1)
    self.assertEqual(syllabus.school_year, '2024-2025')

  def test_upload_syllabus_increments_version(self):
    first_file = SimpleUploadedFile('first.pdf', b'first', content_type='application/pdf')
    self.client.post(
      reverse('upload_syllabus'),
      {
        'dept_id': str(self.dept.id),
        'prof_id': str(self.prof.id),
        'course_id': str(self.course.id),
        'semester': '1',
        'school_year': '2024-2025'
      },
      files={'file': first_file}
    )
    second_file = SimpleUploadedFile('second.pdf', b'second', content_type='application/pdf')
    self.client.post(
      reverse('upload_syllabus'),
      {
        'dept_id': str(self.dept.id),
        'prof_id': str(self.prof.id),
        'course_id': str(self.course.id),
        'semester': '1',
        'school_year': '2024-2025'
      },
      files={'file': second_file}
    )
    versions = list(Syllabus.objects.filter(course=self.course, prof=self.prof).order_by('version'))
    self.assertEqual(len(versions), 2)
    self.assertEqual(versions[0].version, 1)
    self.assertEqual(versions[1].version, 2)

  def test_filter_syllabi_returns_data(self):
    file = SimpleUploadedFile('syllabus.pdf', b'PDF content', content_type='application/pdf')
    Syllabus.objects.create(
      dept=self.dept,
      course=self.course,
      prof=self.prof,
      file=file,
      semester='1',
      school_year='2024-2025',
      version=1
    )
    response = self.client.get(reverse('filter_syllabi'), {'dept_id': self.dept.id})
    self.assertEqual(response.status_code, 200)
    data = response.json()
    self.assertEqual(len(data['syllabi']), 1)
    self.assertEqual(data['syllabi'][0]['course'], f"{self.course.code}: {self.course.name}")
