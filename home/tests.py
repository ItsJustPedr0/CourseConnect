from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class HomeViewsTests(TestCase):
  def setUp(self):
    self.user = CustomUser.objects.create_user(student_id='232022', password='TestPass123')

  def test_home_requires_login(self):
    response = self.client.get(reverse('home'))
    self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")

  def test_signup_get_renders_form(self):
    response = self.client.get(reverse('signup'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Student ID Number')

  def test_signup_post_creates_user(self):
    response = self.client.post(reverse('signup'), {
      'student_id': '123456',
      'password': 'Password1',
      'confirm_password': 'Password1'
    })
    self.assertRedirects(response, reverse('home'))
    self.assertTrue(CustomUser.objects.filter(student_id='123456').exists())

  def test_signup_invalid_passwords_show_error(self):
    response = self.client.post(reverse('signup'), {
      'student_id': '123457',
      'password': 'short',
      'confirm_password': 'short'
    })
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Password must be at least 6 characters long.')

  def test_login_post_with_valid_credentials(self):
    response = self.client.post(reverse('login'), {
      'student_id': '232022',
      'password': 'TestPass123'
    })
    self.assertRedirects(response, reverse('home'))
    self.assertTrue('_auth_user_id' in self.client.session)

  def test_login_post_with_invalid_credentials(self):
    response = self.client.post(reverse('login'), {
      'student_id': '232022',
      'password': 'WrongPassword'
    })
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Invalid student ID or password.')

  def test_logout_redirects_home(self):
    self.client.login(username='232022', password='TestPass123')
    response = self.client.get(reverse('logout'))
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, reverse('home'))
