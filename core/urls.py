from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import ForumAuthenticationForm

urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='core/login.html',
        authentication_form=ForumAuthenticationForm,
        next_page='index',
    ), name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
]
