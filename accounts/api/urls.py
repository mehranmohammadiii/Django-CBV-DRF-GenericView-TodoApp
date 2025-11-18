from django.urls import path
from .views import (
    LoginApiView,
    LogoutApiView,
    RegisterApiView,
    CustomTokenObtainPairView,
    ChangePasswordView,
    SendEmailView,
)
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginApiView.as_view(), name="login"),
    path("logout/", LogoutApiView.as_view(), name="logout"),  # POST method
    path("register/", RegisterApiView.as_view(), name="register"),
    path(
        "jwt/create/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path("send-email/", SendEmailView.as_view(), name="send-email"),
]
