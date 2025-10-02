from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import RegisterView, ProfileView, LogoutView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),  # Add this line
    path("profile/", ProfileView.as_view(), name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
]