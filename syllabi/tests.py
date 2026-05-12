import tempfile
import shutil
import os

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings

from forum.models import Department, Prof, Course
from .models import Syllabus

CustomUser = get_user_model()

# Use temp directory for test media
MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SyllabiSetupMixin:
  """Reusable setup for syllabi tests"""
  def setUp(self):
    self.client = Client()
    self.user = CustomUser.objects.create_user(student_id='232022', password='TestPass123')
    
    self.dept = Department.objects.create(name='Engineering', abbrev='ENG')
    self.prof = Prof.objects.create(first_name='Dr', last_name='Engineering', dept=self.dept)
    self.course = Course.objects.create(code='ENG101', name='Engineering Basics', dept=self.dept)
    self.course.prof.add(self.prof)
  
  @classmethod
  def tearDownClass(cls):
    """Clean up temp media directory"""
    shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
    super().tearDownClass()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SyllabiRepositoryTests(SyllabiSetupMixin, TestCase):
  """Test syllabi repository page access and display"""
  
  def test_repository_requires_login(self):
    """Test syllabi repository redirects unauthenticated users"""
    response = self.client.get(reverse('repository'))
    self.assertRedirects(response, f"{reverse('login')}?next={reverse('repository')}")
  
  def test_repository_page_loads(self):
    """Test syllabi repository page loads for authenticated users"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('repository'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'syllabi/repository.html')
  
  def test_repository_displays_syllabi(self):
    """Test repository displays uploaded syllabi"""
    # Create test file
    test_file = SimpleUploadedFile(
      'test_syllabus.pdf',
      b'file_content',
      content_type='application/pdf'
    )
    
    Syllabus.objects.create(
      dept=self.dept,
      course=self.course,
      prof=self.prof,
      file=test_file,
      semester='1',
      school_year='2024-2025',
      version=1,
      verified=True
    )
    
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('repository'))
    self.assertContains(response, 'ENG101')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SyllabiUploadTests(SyllabiSetupMixin, TestCase):
  """Test syllabus file upload functionality"""
  
  def test_syllabus_upload_creates_file(self):
    """Test uploading a syllabus creates file in storage"""
    test_file = SimpleUploadedFile(
      'syllabus.pdf',
      b'PDF file content here',
      content_type='application/pdf'
    )
    
    syllabus = Syllabus.objects.create(
      dept=self.dept,
      course=self.course,
      prof=self.prof,
      file=test_file,
      semester='1',
      school_year='2024-2025',
      version=1
    )
    
    self.assertTrue(syllabus.file)
    self.assertEqual(Syllabus.objects.count(), 1)
  
  def test_syllabus_version_tracking(self):
    """Test syllabus versioning works"""
    test_file_v1 = SimpleUploadedFile(
      'v1.pdf',
      b'Version 1 content',
      content_type='application/pdf'
    )
    
    test_file_v2 = SimpleUploadedFile(
      'v2.pdf',
      b'Version 2 content',
      content_type='application/pdf'
    )
    
    syllabus_v1 = Syllabus.objects.create(
      dept=self.dept,
      course=self.course,
      prof=self.prof,
      file=test_file_v1,
      semester='1',
      school_year='2024-2025',
      version=1
    )
    
    syllabus_v2 = Syllabus.objects.create(
      dept=self.dept,
      course=self.course,
      prof=self.prof,
      file=test_file_v2,
      semester='1',
      school_year='2024-2025',
      version=2
    )
    
    self.assertEqual(Syllabus.objects.count(), 2)
    self.assertNotEqual(syllabus_v1.file.name, syllabus_v2.file.name)
  
  def test_syllabus_unique_constraint(self):
    """Test unique constraint on professor+course+semester+year+version"""
    test_file = SimpleUploadedFile(
      'test.pdf',
      b'content',
      content_type='application/pdf'
    )
    
    # Create first syllabus
    Syllabus.objects.create(
      dept=self.dept,
      course=self.course,
      prof=self.prof,
      file=test_file,
      semester='1',
      school_year='2024-2025',
      version=1
    )
    
    # Try to create duplicate - should fail
    test_file2 = SimpleUploadedFile(
      'test2.pdf',
      b'content',
      content_type='application/pdf'
    )
    
    with self.assertRaises(Exception):  # IntegrityError
      Syllabus.objects.create(
        dept=self.dept,
        course=self.course,
        prof=self.prof,
        file=test_file2,
        semester='1',
        school_year='2024-2025',
        version=1
      )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SyllabiDeletionTests(SyllabiSetupMixin, TestCase):
  """Test syllabus file deletion when object is deleted"""
  
  def test_syllabus_file_deleted_on_object_deletion(self):
    """Test that file is deleted when Syllabus object is deleted"""
    test_file = SimpleUploadedFile(
      'test_delete.pdf',
      b'content to delete',
      content_type='application/pdf'
    )
    
    syllabus = Syllabus.objects.create(
      dept=self.dept,
      course=self.course,
      prof=self.prof,
      file=test_file,
      semester='1',
      school_year='2024-2025',
      version=1
    )
    
    file_path = syllabus.file.name
    file_exists = syllabus.file.storage.exists(file_path)
    self.assertTrue(file_exists, "File should exist after creation")
    
    # Delete the syllabus
    syllabus_id = syllabus.id
    syllabus.delete()
    
    # Check file is deleted
    # Need to re-fetch storage instance
    from django.core.files.storage import default_storage
    file_deleted = not default_storage.exists(file_path)
    self.assertTrue(file_deleted, "File should be deleted when Syllabus is deleted")
    self.assertEqual(Syllabus.objects.count(), 0)
  
  def test_multiple_versions_files_preserved(self):
    """Test that deleting one version doesn't affect other versions"""
    test_file_v1 = SimpleUploadedFile(
      'v1.pdf',
      b'Version 1',
      content_type='application/pdf'
    )
    
    test_file_v2 = SimpleUploadedFile(
      'v2.pdf',
      b'Version 2',
      content_type='application/pdf'
    )
    
    syllabus_v1 = Syllabus.objects.create(
      dept=self.dept,
      course=self.course,
      prof=self.prof,
      file=test_file_v1,
      semester='1',
      school_year='2024-2025',
      version=1
    )
    
    syllabus_v2 = Syllabus.objects.create(
      dept=self.dept,
      course=self.course,
      prof=self.prof,
      file=test_file_v2,
      semester='1',
      school_year='2024-2025',
      version=2
    )
    
    v1_file_path = syllabus_v1.file.name
    v2_file_path = syllabus_v2.file.name
    
    # Delete v1
    syllabus_v1.delete()
    
    # v1 file should be deleted
    from django.core.files.storage import default_storage
    v1_deleted = not default_storage.exists(v1_file_path)
    self.assertTrue(v1_deleted, "V1 file should be deleted")
    
    # v2 file should still exist
    v2_exists = default_storage.exists(v2_file_path)
    self.assertTrue(v2_exists, "V2 file should still exist")
    
    # Only v2 should remain in DB
    self.assertEqual(Syllabus.objects.count(), 1)
    self.assertEqual(Syllabus.objects.first().version, 2)
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
