from io import BytesIO
from tempfile import TemporaryDirectory
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Profile


User = get_user_model()
PASSWORD = 'Sample-password-for-forum-6!'


def png_avatar(filename='avatar.png'):
    buffer = BytesIO()
    Image.new('RGB', (8, 8), 'blue').save(buffer, format='PNG')
    return SimpleUploadedFile(filename, buffer.getvalue(), content_type='image/png')


class AccountsTests(TestCase):
    def test_signup_validates_password_and_creates_profile(self):
        data = {
            'username': 'new-member', 'email': 'new@example.com', 'first_name': 'Студент',
            'password1': '12345678', 'password2': '12345678',
        }
        signup = reverse('signup')
        failed = self.client.post(signup, data)
        self.assertTrue(failed.context['form'].errors)
        self.assertContains(failed, 'new@example.com')
        self.assertFalse(User.objects.filter(username='new-member').exists())

        data.update(password1=PASSWORD, password2=PASSWORD)
        self.assertRedirects(self.client.post(signup, data), reverse('index'))
        user = User.objects.get(username='new-member')
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))
        self.assertTrue(user.check_password(PASSWORD))
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_login_and_logout_validate_next(self):
        User.objects.create_user(username='member', password=PASSWORD)
        login, logout, hot = reverse('login'), reverse('logout'), reverse('hot')
        credentials = {'username': 'member', 'password': PASSWORD}

        failed = self.client.post(login, {'username': 'member', 'password': 'wrong', 'next': hot})
        self.assertTrue(failed.context['form'].non_field_errors())
        self.assertContains(failed, 'value="member"')
        self.assertRedirects(self.client.post(login, {**credentials, 'next': hot}), hot)
        self.assertRedirects(self.client.post(logout, {'next': hot}), hot)
        self.assertRedirects(self.client.post(login, {**credentials, 'next': '//outside.example/'}), '/')
        self.assertRedirects(self.client.post(logout, {'next': 'https://outside.example/'}), '/')
        self.assertEqual(self.client.get(logout).status_code, 405)

    def test_profile_updates_only_own_details_and_checks_avatars(self):
        user = User.objects.create_user(username='member', email='old@example.com')
        profile = reverse('profile')
        self.assertRedirects(self.client.get(profile), f'{reverse("login")}?next={profile}')
        self.client.force_login(user)
        self.assertContains(self.client.get(profile), 'value="old@example.com"')
        data = {'first_name': 'Никнейм', 'email': 'new@example.com'}
        with TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            invalid_files = [
                png_avatar('wrong.jpg'),
                SimpleUploadedFile('bad.png', b'not an image'),
                SimpleUploadedFile('large.png', b'x' * (2 * 1024 * 1024 + 1)),
            ]
            for upload in invalid_files:
                response = self.client.post(profile, {**data, 'avatar': upload})
                self.assertTrue(response.context['form'].errors.get('avatar'))
                self.assertContains(response, 'new@example.com')

            self.assertRedirects(self.client.post(profile, {**data, 'avatar': png_avatar()}), profile)
            user.refresh_from_db()
            self.assertEqual((user.username, user.first_name, user.email), ('member', 'Никнейм', 'new@example.com'))
            path = user.profile.avatar.name
            self.assertTrue(path.startswith('avatars/'))
            UUID(path.split('/')[-1].split('.')[0])
            self.assertTrue(user.profile.avatar.storage.exists(path))
            self.assertContains(self.client.get(profile), user.profile.avatar.url)
            self.client.post(profile, {**data, 'first_name': 'Обновлённый ник'})
            self.assertEqual(Profile.objects.get(user=user).avatar.name, path)
