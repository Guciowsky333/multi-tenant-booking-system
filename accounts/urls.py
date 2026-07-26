from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    ChangePasswordAPIView,
    CreateAccountAPIView,
    LogoutAPIView,
    MeView,
    ResetPasswordAPIView,
    SendResetPasswordCodeAPIView,
    SendVerificationEmailView,
    ThrottledTokenObtainPairView,
)

urlpatterns = [
    path("token/", ThrottledTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("send_verification_email/", SendVerificationEmailView.as_view(), name="send_verification_email"),
    path("create/", CreateAccountAPIView.as_view(), name="create"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("change_password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("send_reset_password_code/", SendResetPasswordCodeAPIView.as_view(), name="send_reset_password_code"),
    path("reset_password/", ResetPasswordAPIView.as_view(), name="reset_password"),
]
