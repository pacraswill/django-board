# coding=utf8
from django.contrib.auth import views as auth_views
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core import mail
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase

'''
基础测试：
    测试能否正常访问到该页面； 是否对应的预计的处理函数； 是否包含 csrfmiddlewaretoken;
    是否包含预计表格；是否包含某些 h5 信息

'''


class PasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/reset/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 2)
        self.assertContains(self.response, 'type="email"', 1)


'''
测试成功的提交测试
    提交正确的数据后应该跳转到 ‘password_reset_done’
 '''


class SuccessfulPasswordResetTests(TestCase):
    def setUp(self):
        email = 'allen@bit.com'
        User.objects.create_user(username='allen', email=email, password='1234fds')
        url = reverse('password_reset')
        self.response = self.client.post(url, {'email': email})

    def test_redirection(self):
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_send_password_reset_email(self):
        self.assertEqual(1, len(mail.outbox))


class InvalidPasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.post(url, {'email': 'djsfj@23.com'})

    def test_redirection(self):
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_no_reset_email_sent(self):
        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_done')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/reset/done/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetDoneView)


class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='allen',
                                        email='allen@bit.com', password='123')
        self.uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        self.token = default_token_generator.make_token(user)

        url = reverse('password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        self.response = self.client.get(url, follow=True)

        def test_status_code(self):
            self.assertEquals(self.response.status_code, 200)

        def test_view_function(self):
            view = resolve('/reset/{uidb64}/{token}/'.format(uidb64=self.uid, token=self.token))
            self.assertEquals(view.func.view_class, auth_views.PasswordResetConfirmView)

        def test_csrf(self):
            self.assertContains(self.response, 'csrfmiddlewaretoken')

        def test_contains_form(self):
            form = self.response.context.get('form')
            self.assertIsInstance(form, SetPasswordForm)

        def test_form_inputs(self):
            '''
            The view must contain two inputs: csrf and two password fields
            '''
            self.assertContains(self.response, '<input', 3)
            self.assertContains(self.response, 'type="password"', 2)


class InvalidPasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='john', email='john@doe.com', password='123abcdef')
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = default_token_generator.make_token(user)

        '''
        invalidate the token by changing the password
        '''
        user.set_password('abcdef123')
        user.save()

        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_html(self):
        password_reset_url = reverse('password_reset')
        self.assertContains(self.response, 'invalid password reset link')
        self.assertContains(self.response, 'href="{0}"'.format(password_reset_url))


class PasswordRestCompleteTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_complete')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/reset/complete/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetCompleteView)
