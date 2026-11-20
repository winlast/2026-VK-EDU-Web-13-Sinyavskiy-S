from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from .models import Profile

User = get_user_model()


class BootstrapFields:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class AvatarField(forms.ImageField):
    formats = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP'}

    def __init__(self):
        super().__init__(
            label='Аватар', required=False, help_text='JPEG, PNG или WebP, до 2 МБ.',
            widget=forms.FileInput(attrs={'accept': 'image/jpeg,image/png,image/webp'}),
        )

    def to_python(self, data):
        if not data:
            return None
        if data.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Файл весит больше 2 МБ.')
        image_format = self.formats.get(Path(data.name).suffix.lower())
        if not image_format:
            raise forms.ValidationError('Загрузите файл JPEG, PNG или WebP.')
        upload = super().to_python(data)
        if upload.image.format != image_format:
            raise forms.ValidationError('Расширение не соответствует содержимому файла.')
        return upload


def check_email(email, *, user_id=None):
    if User.objects.filter(email__iexact=email).exclude(pk=user_id).exists():
        raise forms.ValidationError('Этот email уже используется.')
    return email


class ForumAuthenticationForm(BootstrapFields, AuthenticationForm):
    pass


class SignupForm(BootstrapFields, UserCreationForm):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='Имя / никнейм', max_length=150)
    avatar = AvatarField()

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'first_name')

    def clean_email(self):
        return check_email(self.cleaned_data['email'])

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(user=user, avatar=self.cleaned_data['avatar'] or '')
        return user


class ProfileForm(BootstrapFields, forms.ModelForm):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='Никнейм', max_length=150)
    avatar = AvatarField()

    class Meta:
        model = Profile
        fields = ('email', 'first_name', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial.update(email=self.instance.user.email, first_name=self.instance.user.first_name)

    def clean_email(self):
        return check_email(self.cleaned_data['email'], user_id=self.instance.user_id)

    @transaction.atomic
    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data['first_name']
        profile.user.email = self.cleaned_data['email']
        if commit:
            profile.user.save(update_fields=['first_name', 'email'])
            profile.save()
        return profile
