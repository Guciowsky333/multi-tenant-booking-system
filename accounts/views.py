# Create your views here.
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import ChangePasswordSerializer, LogoutSerializer, RegisterSerializer
from accounts.services import change_password, create_account


class CreateAccountAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Create new account",
        description="""
        Create a new account with provided email and password.
        
        Business rules:
        - Fields email, password and password_2 are required.
        - Email must be unique.
        - Email must be in valid format (validated by Django EmailField).
        - Fields password and password_2 must be the same.
        - Password must be at least 8 characters long.
        - Password must contain at least one uppercase letter.
        """,
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(description="Account created successfully"),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        create_account(email, password)

        return Response(
            {
                "message": "Account created successfully",
            },
            status=201,
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout",
        description="""
        Add user refresh token to blacklist, after this, user cannot use this refresh token
        to take access token.
        
        Business rules:
        - Fields refresh_token is required.
        - Specified refresh_token must be correct.
        - Authentication required.
        """,
        request=LogoutSerializer,
        responses={
            200: OpenApiResponse(description="Account logout successfully"),
            400: OpenApiResponse(description="Validation error/ invalid refresh token"),
            401: OpenApiResponse(description="Unauthorized"),
        },
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh_token"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {
                    "message": "Account logout successfully",
                },
                status=200,
            )

        except TokenError as e:
            return Response(
                {
                    "message": str(e),
                },
                status=400,
            )


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change password",
        description="""
        Change password specified user account.
        
        Business rules:
        - Fields old_password, new_password and new_password_2 are required.
        - Old password must belongs to the request user 
        - New password cannot be the same as old password.
        - Fields new_password and new_password_2 must be the same.
        - New password must be at least 8 characters long and contain at least one uppercase letter.
        - Authentication required.
        """,
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Account password changed successfully"),
            400: OpenApiResponse(description="Validation error/ Field old_password not belong to the user account"),
            401: OpenApiResponse(description="Unauthorized"),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        try:
            change_password(old_password, new_password, user)
            return Response(
                {
                    "message": "Password changed successfully",
                },
                status=200,
            )

        except ValueError as e:
            return Response(
                {
                    "message": str(e),
                },
                status=400,
            )
