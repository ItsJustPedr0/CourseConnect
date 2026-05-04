from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Department, Prof, Course, Post

CustomUser = get_user_model()


class ForumViewsTests(TestCase):
  def setUp(self):
    self.user = CustomUser.objects.create_user(student_id='232022', password='TestPass123')
    self.dept = Department.objects.create(name='Engineering', abbrev='ENG')
    self.prof = Prof.objects.create(first_name='Jane', last_name='Doe', dept=self.dept)
    self.course = Course.objects.create(code='ENG101', name='Intro to Engineering', dept=self.dept)
    self.course.prof.add(self.prof)
    self.post = Post.objects.create(title='Test Post', body='Test body', prof=self.prof, course=self.course)

  def test_index_requires_login(self):
    response = self.client.get(reverse('index'))
    self.assertRedirects(response, f"{reverse('login')}?next={reverse('index')}")

  def test_index_shows_departments(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('index'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.dept.name)

  def test_dept_index_shows_courses_and_profs(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('dept_index', kwargs={'abbrev': self.dept.slug}))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.course.name)
    self.assertContains(response, self.prof.full_name)

  def test_course_detail_show_posts(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('course_detail', kwargs={'abbrev': self.dept.slug, 'course_slug': self.course.slug}))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.post.title)

  def test_prof_detail_show_posts(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('prof_detail', kwargs={'abbrev': self.dept.slug, 'prof_slug': self.prof.slug}))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, self.post.title)

  def test_search_returns_json_results(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('search'), {'q': 'ENG'})
    self.assertEqual(response.status_code, 200)
    data = response.json()
    self.assertEqual(data['query'], 'ENG')
    self.assertTrue(any(item['type'] == 'course' for item in data['results']))

  def test_add_post_creates_new_post(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.post(reverse('add_post'), {
      'title': 'New Post',
      'body': 'New body',
      'prof_id': str(self.prof.id),
      'course_id': str(self.course.id),
      'dept_id': str(self.dept.id)
    })
    self.assertRedirects(response, reverse('course_detail', kwargs={'abbrev': self.dept.slug, 'course_slug': self.course.slug}))
    self.assertTrue(Post.objects.filter(title='New Post').exists())

  def test_get_profs_by_dept_returns_json(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('get_profs'), {'dept_id': self.dept.id})
    data = response.json()
    self.assertEqual(len(data['profs']), 1)
    self.assertEqual(data['profs'][0]['slug'], self.prof.slug)

  def test_get_courses_by_prof_returns_json(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('get_courses'), {'prof_id': self.prof.id})
    data = response.json()
    self.assertEqual(len(data['courses']), 1)
    self.assertEqual(data['courses'][0]['name'], self.course.name)

  def test_get_courses_by_dept_returns_json(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('get_courses_by_dept'), {'dept_id': self.dept.id})
    data = response.json()
    self.assertEqual(len(data['courses']), 1)
    self.assertEqual(data['courses'][0]['code'], self.course.code)

  def test_get_profs_by_course_returns_json(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('get_profs_by_course'), {'course_id': self.course.id})
    data = response.json()
    self.assertEqual(len(data['profs']), 1)
    self.assertEqual(data['profs'][0]['slug'], self.prof.slug)
