from django.urls import path, include

urlpatterns = [
    path('', include('phone_auth.urls')),
]
