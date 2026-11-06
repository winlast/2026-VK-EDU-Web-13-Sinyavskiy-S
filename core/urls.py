from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
]
