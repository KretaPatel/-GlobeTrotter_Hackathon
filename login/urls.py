from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "login"

urlpatterns = [
    # ---- Pages ----
    path("", views.login_page, name="login-page"),
    path("signup/", views.signup_page, name="signup-page"),

    # ---- JWT API ----
    path("api/register/", views.RegisterView.as_view(), name="api-register"),
    path("api/login/", views.CustomTokenObtainPairView.as_view(), name="api-login"),
    path("api/token/refresh/", TokenRefreshView.as_view(),
         name="api-token-refresh"),
    path("api/logout/", views.LogoutView.as_view(), name="api-logout"),
    path("api/profile/", views.ProfileView.as_view(), name="api-profile"),
]
