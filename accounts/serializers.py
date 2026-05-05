from rest_framework import serializers

from accounts.models import CustomUser


class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField()
    password_2 = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        password = data["password"]
        password_2 = data["password_2"]
        email = data["email"]

        if password != password_2:
            raise serializers.ValidationError("Passwords do not match")

        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")

        if not any(x.isupper() for x in password):
            raise serializers.ValidationError("Password must contain at least one uppercase character")

        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")

        return data


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
