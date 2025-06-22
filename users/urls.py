from django.urls import path, include
from .views import UserApiView, CreateUserView

urlpatterns = [
    path("users/", include('rest_framework.urls')),
    path('users/register', CreateUserView.as_view()),
    path('users/<str:username>', UserApiView.as_view()),
    
]