from django.contrib import messages
from django.contrib.auth import login as sign_in
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ProfileForm, SignupForm, User
from .models import Profile


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    bound = request.method == 'POST'
    form = SignupForm(request.POST if bound else None, request.FILES if bound else None)
    if form.is_valid():
        try:
            user = form.save()
        except IntegrityError:
            if not User.objects.filter(username=form.cleaned_data['username']).exists():
                raise
            form.add_error('username', 'Этот логин уже занят.')
        else:
            sign_in(request, user)
            return redirect('index')
    return render(request, 'core/signup.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def profile(request):
    try:
        member = request.user.profile
    except Profile.DoesNotExist:
        member = Profile(user=request.user)

    bound = request.method == 'POST'
    form = ProfileForm(request.POST if bound else None, request.FILES if bound else None, instance=member)
    if form.is_valid():
        form.save()
        messages.success(request, 'Настройки сохранены.')
        return redirect('profile')
    return render(request, 'core/profile.html', {'form': form})
