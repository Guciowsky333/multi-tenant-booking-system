from rest_framework import serializers

from accounts.models import CustomUser
from accounts.validators import validate_passwords


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "first_name", "last_name", "email"]


class SendVerificationCodeSerializer(serializers.Serializer):
    password = serializers.CharField()
    password_2 = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        password = data["password"]
        password_2 = data["password_2"]
        email = data["email"]

        validate_passwords(password, password_2)

        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists")

        return data


class CreateAccountSerializer(serializers.Serializer):
    password = serializers.CharField()
    password_2 = serializers.CharField()
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        password = data["password"]
        password_2 = data["password_2"]
        email = data["email"]

        validate_passwords(password, password_2)

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

        validate_passwords(new_password, new_password_2)

        if new_password == old_password:
            raise serializers.ValidationError("New password must not be the same as old password")

        return data


class SendPasswordResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField()
    new_password_2 = serializers.CharField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        new_password = data["new_password"]
        new_password_2 = data["new_password_2"]

        validate_passwords(new_password, new_password_2)

        return data
