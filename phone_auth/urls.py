from django.urls import path

from .views import LoginView, LogoutView, RegisterView

app_name = 'phone_auth'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
