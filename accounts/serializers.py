from rest_framework import serializers

from accounts.models import CustomUser
from accounts.validators import validate_password


class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField()
    password_2 = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        password = data["password"]
        password_2 = data["password_2"]
        email = data["email"]

        validate_password(password)

        if password != password_2:
            raise serializers.ValidationError("Passwords do not match")

        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")

        return data


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_2 = serializers.CharField()

    def validate(self, data):
        old_password = data["old_password"]
        new_password = data["new_password"]
        new_password_2 = data["new_password_2"]

        validate_password(new_password)

        if new_password == old_password:
            raise serializers.ValidationError("New password must not be the same as old password")
        if new_password != new_password_2:
            raise serializers.ValidationError("new_password and new_password_2 must match")

        return data
