from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

from .models import Department, Prof, Course, Post, Comment, Report

CustomUser = get_user_model()


class ForumSetupMixin:
  """Reusable test setup for forum tests"""
  def setUp(self):
    self.client = Client()
    self.user = CustomUser.objects.create_user(student_id='232022', password='TestPass123')
    self.other_user = CustomUser.objects.create_user(student_id='232023', password='TestPass123')
    
    self.dept = Department.objects.create(name='Computer Science', abbrev='CS')
    self.prof = Prof.objects.create(first_name='John', last_name='Smith', dept=self.dept)
    self.course = Course.objects.create(code='CS101', name='Intro to CS', dept=self.dept)
    self.course.prof.add(self.prof)
    
    self.post = Post.objects.create(
      title='Great Course',
      body='This course was excellent!',
      prof=self.prof,
      course=self.course
    )


class ForumNavigationTests(ForumSetupMixin, TestCase):
  """Test forum page navigation and access control"""
  
  def test_forum_index_requires_login(self):
    """Test forum index redirects unauthenticated users"""
    response = self.client.get(reverse('index'))
    self.assertRedirects(response, f"{reverse('login')}?next={reverse('index')}")
  
  def test_forum_index_loads(self):
    """Test forum index loads for authenticated users"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('index'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Computer Science')
  
  def test_department_detail_loads(self):
    """Test department detail page loads"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('dept_index', args=[self.dept.slug]))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'CS101')
  
  def test_course_detail_loads(self):
    """Test course detail page loads with posts"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('course_detail', args=[self.dept.slug, self.course.slug]))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Great Course')
    self.assertContains(response, 'This course was excellent!')
  
  def test_prof_detail_loads(self):
    """Test professor detail page loads"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('prof_detail', args=[self.dept.slug, self.prof.slug]))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Great Course')


class ForumPostCreationTests(ForumSetupMixin, TestCase):
  """Test forum post creation functionality"""
  
  def test_add_post_page_loads(self):
    """Test add post page loads"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('add_post'))
    self.assertEqual(response.status_code, 200)
  
  def test_create_post_success(self):
    """Test successfully creating a new post"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.post(reverse('add_post'), {
      'title': 'Amazing Professor!',
      'body': 'Prof Smith explains concepts very clearly.',
      'prof_id': self.prof.id,
      'course_id': self.course.id,
    })
    self.assertEqual(Post.objects.count(), 2)
    new_post = Post.objects.latest('post_date')
    self.assertEqual(new_post.title, 'Amazing Professor!')
    self.assertEqual(new_post.body, 'Prof Smith explains concepts very clearly.')
  
  def test_create_post_requires_login(self):
    """Test creating post requires authentication"""
    response = self.client.post(reverse('add_post'), {
      'title': 'Test',
      'body': 'Test body',
      'prof_id': self.prof.id,
      'course_id': self.course.id,
    })
    self.assertRedirects(response, f"{reverse('login')}?next={reverse('add_post')}")
  
  def test_create_post_empty_title_fails(self):
    """Test post creation fails with empty title"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.post(reverse('add_post'), {
      'title': '',
      'body': 'Test body',
      'prof_id': self.prof.id,
      'course_id': self.course.id,
    })
    self.assertEqual(response.status_code, 400)


class ForumCommentingTests(ForumSetupMixin, TestCase):
  """Test forum commenting functionality"""
  
  def test_add_comment_requires_login(self):
    """Test adding comment requires authentication"""
    response = self.client.post(
      reverse('add_comment', args=[self.post.id]),
      data=json.dumps({'body': 'Great review!'}),
      content_type='application/json'
    )
    self.assertEqual(response.status_code, 403)
  
  def test_add_comment_success(self):
    """Test successfully adding a comment"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.post(
      reverse('add_comment', args=[self.post.id]),
      data=json.dumps({'body': 'I agree with this!'}),
      content_type='application/json',
      HTTP_X_CSRFTOKEN=self._get_csrf_token()
    )
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.content)
    self.assertTrue(data['success'])
    self.assertEqual(Comment.objects.count(), 1)
    comment = Comment.objects.first()
    self.assertEqual(comment.body, 'I agree with this!')
    self.assertEqual(comment.user, self.user)
  
  def test_add_empty_comment_fails(self):
    """Test adding empty comment fails"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.post(
      reverse('add_comment', args=[self.post.id]),
      data=json.dumps({'body': '   '}),
      content_type='application/json',
      HTTP_X_CSRFTOKEN=self._get_csrf_token()
    )
    self.assertEqual(response.status_code, 400)
    self.assertEqual(Comment.objects.count(), 0)
  
  def test_multiple_comments_on_same_post(self):
    """Test multiple comments on same post"""
    self.client.login(username='232022', password='TestPass123')
    
    for i in range(5):
      self.client.post(
        reverse('add_comment', args=[self.post.id]),
        data=json.dumps({'body': f'Comment {i+1}'}),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=self._get_csrf_token()
      )
    
    self.assertEqual(Comment.objects.count(), 5)
    self.assertEqual(self.post.comments.count(), 5)
  
  def test_comment_displays_anonymous_user(self):
    """Test comments display as anonymous in queryset"""
    self.client.login(username='232022', password='TestPass123')
    self.client.post(
      reverse('add_comment', args=[self.post.id]),
      data=json.dumps({'body': 'Test comment'}),
      content_type='application/json',
      HTTP_X_CSRFTOKEN=self._get_csrf_token()
    )
    comment = Comment.objects.first()
    # User is stored but frontend should show as "Anonymous User"
    self.assertIsNotNone(comment.user)
  
  def _get_csrf_token(self):
    """Helper to get CSRF token"""
    response = self.client.get(reverse('course_detail', args=[self.dept.slug, self.course.slug]))
    return response.cookies.get('csrftoken').value if 'csrftoken' in response.cookies else ''


class ForumReportingTests(ForumSetupMixin, TestCase):
  """Test forum reporting functionality"""
  
  def test_add_report_requires_login(self):
    """Test adding report requires authentication"""
    response = self.client.post(
      reverse('add_report', args=[self.post.id]),
      data=json.dumps({'report_type': 'spam', 'explanation': 'Test'}),
      content_type='application/json'
    )
    self.assertEqual(response.status_code, 403)
  
  def test_add_report_success(self):
    """Test successfully adding a report"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.post(
      reverse('add_report', args=[self.post.id]),
      data=json.dumps({
        'report_type': 'spam',
        'explanation': 'This is spam content'
      }),
      content_type='application/json',
      HTTP_X_CSRFTOKEN=self._get_csrf_token()
    )
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.content)
    self.assertTrue(data['success'])
    self.assertEqual(Report.objects.count(), 1)
    report = Report.objects.first()
    self.assertEqual(report.report_type, 'spam')
    self.assertEqual(report.user, self.user)
  
  def test_report_types_validation(self):
    """Test only valid report types accepted"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.post(
      reverse('add_report', args=[self.post.id]),
      data=json.dumps({
        'report_type': 'invalid_type',
        'explanation': 'Test'
      }),
      content_type='application/json',
      HTTP_X_CSRFTOKEN=self._get_csrf_token()
    )
    self.assertEqual(response.status_code, 400)
    self.assertEqual(Report.objects.count(), 0)
  
  def test_multiple_reports_same_post(self):
    """Test multiple reports on same post"""
    for i in range(3):
      user = CustomUser.objects.create_user(student_id=f'23202{i}', password='TestPass123')
      self.client.login(username=f'23202{i}', password='TestPass123')
      self.client.post(
        reverse('add_report', args=[self.post.id]),
        data=json.dumps({
          'report_type': 'harassment',
          'explanation': f'Report {i+1}'
        }),
        content_type='application/json',
        HTTP_X_CSRFTOKEN=self._get_csrf_token()
      )
      self.client.logout()
    
    self.assertEqual(Report.objects.count(), 3)
    self.assertEqual(self.post.reports.count(), 3)
  
  def _get_csrf_token(self):
    """Helper to get CSRF token"""
    response = self.client.get(reverse('course_detail', args=[self.dept.slug, self.course.slug]))
    return response.cookies.get('csrftoken').value if 'csrftoken' in response.cookies else ''


class ForumSearchTests(ForumSetupMixin, TestCase):
  """Test forum search functionality"""
  
  def test_search_course_by_code(self):
    """Test searching for course by code"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('search'), {'q': 'CS101'})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.content)
    self.assertEqual(len(data['results']), 1)
    self.assertEqual(data['results'][0]['code'], 'CS101')
  
  def test_search_course_by_name(self):
    """Test searching for course by name"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('search'), {'q': 'Intro'})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.content)
    self.assertEqual(len(data['results']), 1)
    self.assertEqual(data['results'][0]['title'], 'Intro to CS')
  
  def test_search_professor_by_name(self):
    """Test searching for professor by name"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('search'), {'q': 'Smith'})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.content)
    self.assertTrue(any(r['type'] == 'prof' for r in data['results']))
  
  def test_search_department(self):
    """Test searching for department"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('search'), {'q': 'Computer'})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.content)
    self.assertTrue(any(r['type'] == 'dept' for r in data['results']))
  
  def test_search_no_results(self):
    """Test search with no results"""
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('search'), {'q': 'NonexistentCourse'})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.content)
    self.assertEqual(len(data['results']), 0)
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
