# Create your views here.
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import RegisterSerializer
from accounts.services import create_account


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
