from django.urls import path
from . import views
from .views import user_check

urlpatterns = [
	path('register', views.UserRegister.as_view(), name='register'),
	path('login', views.UserLogin.as_view(), name='login'),
	path('logout', views.UserLogout.as_view(), name='logout'),
    path('user-check', user_check, name='user-check'),
    path('user-change-password', views.UserChangePassword.as_view(), name='user-change-password'),
]