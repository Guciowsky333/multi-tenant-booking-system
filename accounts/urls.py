from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import ChangePasswordAPIView, CreateAccountAPIView, LogoutAPIView

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("create/", CreateAccountAPIView.as_view(), name="create"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("change_password/", ChangePasswordAPIView.as_view(), name="change_password"),
]
